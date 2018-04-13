#!/usr/bin/env python3

""" general utility functions for the bootstrap system """

# imports
import struct
from collections import namedtuple


def args_to_addr(args, ip='127.0.0.1', port=9999):
    """ convert arguments [ip, port] into an address (ip, port) """
    if len(args) >= 3:
        ip, port = args[1], int(args[2])
    elif len(args) == 2:
        ip, port = ip, int(args[1])
    else:
        ip, port = ip, port
    return ip, port


def msg_to_addr(data):
    """ convert raw message (ip:port) into an address (ip, port) """
    ip, port = data.decode('utf-8').strip().split(':')
    return (ip, int(port))


def addr_to_msg(addr):
    """ convert address (ip, port) into a message (ip:port) """
    return '{}:{}'.format(addr[0], str(addr[1])).encode('utf-8')


def send_msg(sock, msg):
    """ prefix each message with a 4-byte length (network byte order) """
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recvall(sock, n):
    """ helper function to recv n bytes or return None if EOF is hit """
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def recv_msg(sock):
    """ read message length and unpack it into an integer """
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # read the message data
    return recvall(sock, msglen)


class node:
    def __init__(self, conn, pub, priv):
        self.conn = conn
        self.pub = pub
        self.priv = priv

    def peer_msg(self):
        return addr_to_msg(self.pub) + b'|' + addr_to_msg(self.priv)
