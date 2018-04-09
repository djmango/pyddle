""" complete a handshake given an address """

# imports
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import requests
import keyUtil

keyUtil.genKey(3)

def handshake(address, bootstrap=False):
    if bootstrap == True:
        pass
    else:
        pass
