""" the p2p system is designed to locate all possible peers, and check if they are alive """

# imports
import os
import sys
import inspect
import logging
import socket
import sys
from threading import Event, Thread

import bootstrapUtil

logger = logging.getLogger('client')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
STOP = Event()


def accept(port):
    logger.info("accept %s", port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(1)
    s.settimeout(5)
    while not STOP.is_set():
        try:
            conn, addr = s.accept()
        except socket.timeout:
            continue
        else:
            logger.info("Accept %s connected!", port)
            STOP.set()


def connect(local_addr, addr):
    logger.info("connect from %s to %s", local_addr, addr)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(local_addr)
    while not STOP.is_set():
        try:
            s.connect(addr)
        except socket.error:
            continue
        else:
            logger.info("connected from %s to %s success!", local_addr, addr)


def connBootstrap(host, port):
    # build socket and get private address
    sa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sa.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sa.connect((host, port))
    priv_addr = sa.getsockname()

    # connect to bootstrap server
    bootstrapUtil.send_msg(sa, bootstrapUtil.addr_to_msg(priv_addr))
    data = bootstrapUtil.recv_msg(sa)
    logger.info("client %s %s - received data: %s",
                priv_addr[0], priv_addr[1], data)

    # store our public address and tell the server that we recieved
    pub_addr = bootstrapUtil.msg_to_addr(data)
    bootstrapUtil.send_msg(sa, bootstrapUtil.addr_to_msg(pub_addr))

    data = bootstrapUtil.recv_msg(sa)
    pubdata, privdata = data.split(b'|')
    client_pub_addr = bootstrapUtil.msg_to_addr(pubdata)
    client_priv_addr = bootstrapUtil.msg_to_addr(privdata)
    logger.info(
        "client public is %s and private is %s, peer public is %s private is %s",
        pub_addr, priv_addr, client_pub_addr, client_priv_addr,
    )

    threads = {
        '0_accept': Thread(target=accept, args=(priv_addr[1],), daemon=True),
        '1_accept': Thread(target=accept, args=(client_pub_addr[1],), daemon=True),
        '2_connect': Thread(target=connect, args=(priv_addr, client_pub_addr,), daemon=True),
        '3_connect': Thread(target=connect, args=(priv_addr, client_priv_addr,), daemon=True),
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
