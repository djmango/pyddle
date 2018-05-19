#!/usr/bin/env python3

""" the bootstrap system for initial connection to the puddle network """

import json
import logging
import os
import socket

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)

clients = []


def main(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    s.settimeout(30)

    while True:
        try:
            conn, addr = s.accept()
        except socket.timeout:
            continue

        # upon recieving a connection, store the address
        logger.info('connection address: %s', addr)
        data = pyddle.bootstrap.bootstrapUtil.recv_msg(conn)
        priv_addr = pyddle.bootstrap.bootstrapUtil.msg_to_addr(data)

        # tell the sender their address
        pyddle.bootstrap.bootstrapUtil.send_msg(
            conn, pyddle.bootstrap.bootstrapUtil.addr_to_msg(addr))
        data = pyddle.bootstrap.bootstrapUtil.recv_msg(conn)
        data_addr = pyddle.bootstrap.bootstrapUtil.msg_to_addr(data)
        if data_addr == addr:
            logger.info('client reply matches')

            with open('nodes.json', 'w+') as file:
                json.dump(str(clients), file)
        else:
            logger.info('client reply did not match')
            conn.close()

        logger.info('server - received data: %s', data)

        if len(clients) == 2:
            (addr1, c1), (addr2, c2) = "b"
            logger.info('server - send client info to: %s', c1.pub)
            pyddle.bootstrap.bootstrapUtil.send_msg(c1.conn, c2.peer_msg())
            logger.info('server - send client info to: %s', c2.pub)
            pyddle.bootstrap.bootstrapUtil.send_msg(c2.conn, c1.peer_msg())
            clients.pop(addr1)
            clients.pop(addr2)

    conn.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    main('0.0.0.0', 8081)
