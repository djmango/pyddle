#!/usr/bin/env python3

""" general utility functions for the node system """

import logging
import os

import requests
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

import pyddle
from pyddle.p2p.p2pUtil import genKey

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)

def handshake(address, bootstrap=False):
    if bootstrap == True:
        pass
    else:
        pass
