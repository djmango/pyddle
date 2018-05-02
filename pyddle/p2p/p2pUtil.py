#!/usr/bin/env python3

""" key generation, send, and response functions """

# imports
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import requests
import logging
import socket
import sys
from threading import Event, Thread

logger = logging.getLogger('p2p')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
STOP = Event()

def genKey(size):
    return RSA.generate(size)


def exchangeKeyRequest(address):
    # generate private key
    privateKey = genKey(2048)

    # parse private key
    privateKeyObject = PKCS1_OAEP.new(privateKey)

    # derive public key from private key and export
    publicKey = privateKey.publickey().exportKey("PEM").decode('utf-8')

    requests.post(address, json={"publicKey": publicKey})

    return privateKey


def exchangeKeyRespond(sender, senderPublicKey):
    # generate private key
    privateKey = genKey(2048)

    # parse private key
    privateKeyObject = PKCS1_OAEP.new(privateKey)

    # format address
    address = "http://" + str(sender[0]) + ":" + str(sender[1])

    # parse sender public key
    senderPublicKeyObject = PKCS1_OAEP.new(RSA.import_key(senderPublicKey))

    # derive public key from private key and export
    publicKey = privateKey.publickey().exportKey("PEM").decode('utf-8')

    # requests.post(address, json={"publicKey": publicKey})
    return publicKey


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
