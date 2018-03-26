""" used to generate rsa public-private keypair and complete a handshake given an address """

# imports
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import requests

def genKey(size):
    return RSA.generate(size)

def exchangeKeyRequest(address):
    # generate private key
    privateKey = genKey(2048)

    # parse private key
    privateKeyObject = PKCS1_OAEP.new(privateKey)

    # test enc
    enc = privateKeyObject.encrypt(b"dee")

    # derive public key from private key and export
    publicKey = privateKey.publickey().exportKey("PEM").decode('utf-8')

    requests.post(address, json={"publicKey": publicKey})

    # decode message
    dec = privateKeyObject.decrypt(enc)
    print(dec)

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
