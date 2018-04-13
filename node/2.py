#!/usr/bin/env python3

""" used to generate rsa public-private keypair and complete a handshake given an address """

# imports
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import requests

def genKey():
    return RSA.generate(2048)

def exchangeKeyRequest(address):
    # generate private key
    privateKey = genKey()

    # parse private key
    privateKeyObject = PKCS1_OAEP.new(privateKey)

    # test enc
    enc = privateKeyObject.encrypt(b"xd")
    print(enc)

    # derive public key from private key and export
    publicKey = privateKey.publickey().exportKey("PEM")

    r = requests.post(address, json={"publicKey": publicKey.decode('utf-8')})
    print(r.text)
    # decode message
    dec = privateKeyObject.decrypt(enc)
    print(dec)

exchangeKeyRequest("http://127.0.0.1:8081")
