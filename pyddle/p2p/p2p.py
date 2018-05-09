#!/usr/bin/env python3

""" the p2p system is designed to locate all possible peers, and check if they are alive """

import inspect
import logging
import os
import socket
import sys
from threading import Event, Thread

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


def connBootstrap(host, port):
    # build socket and get private address
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.connect((host, port))
    priv_addr = sa.getsockname()

    # connect to bootstrap server
    pyddle.bootstrap.bootstrapUtil.send_msg(
        sa, pyddle.bootstrap.bootstrapUtil.addr_to_msg(priv_addr))
    data = pyddle.bootstrap.bootstrapUtil.recv_msg(sa)
    logger.info("client %s %s - received data: %s",
                priv_addr[0], priv_addr[1], data)

    # store our public address and tell the server that we recieved
    pub_addr = pyddle.bootstrap.bootstrapUtil.msg_to_addr(data)
    pyddle.bootstrap.bootstrapUtil.send_msg(
        sa, pyddle.bootstrap.bootstrapUtil.addr_to_msg(pub_addr))

    data = pyddle.bootstrap.bootstrapUtil.recv_msg(sa)
    pubdata, privdata = data.split(b'|')
    client_pub_addr = pyddle.bootstrap.bootstrapUtil.msg_to_addr(pubdata)
    client_priv_addr = pyddle.bootstrap.bootstrapUtil.msg_to_addr(privdata)
    logger.info(
        "client public is %s and private is %s, peer public is %s private is %s",
        pub_addr, priv_addr, client_pub_addr, client_priv_addr,
    )

    threads = {
        '0_accept': Thread(target=pyddle.p2p.p2pUtil.accept, args=(priv_addr[1],), daemon=True),
        '1_accept': Thread(target=pyddle.p2p.p2pUtil.accept, args=(client_pub_addr[1],), daemon=True),
        '2_connect': Thread(target=pyddle.p2p.p2pUtil.connect, args=(priv_addr, client_pub_addr,), daemon=True),
        '3_connect': Thread(target=pyddle.p2p.p2pUtil.connect, args=(priv_addr, client_priv_addr,), daemon=True),
    }
    for name in sorted(threads.keys()):
        logger.info('start thread %s', name)
        threads[name].start()

    while threads:
        keys = list(threads.keys())
        for name in keys:
            try:
                threads[name].join(1)
            except TimeoutError:
                continue
            if not threads[name].is_alive():
                threads.pop(name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, message='%(asctime)s %(message)s')
    connBootstrap('35.185.101.249', 8081)
