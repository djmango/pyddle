#!/usr/bin/env python3

""" complete a handshake given an address """

# imports
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import requests
from pyddle.p2p import p2pUtil

p2pUtil.genKey(3)

def handshake(address, bootstrap=False):
    if bootstrap == True:
        pass
    else:
        pass
