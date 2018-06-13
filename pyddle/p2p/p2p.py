#!/usr/bin/env python3

""" the p2p system is designed to locate all possible peers, and check if they are alive """

import logging
import os
import threading
import time

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


def handleECHO(peerconn, msgdata):
    pyddle.p2pNode.connectandsend(peerconn.host, 51234, 'ECHO', msgdata)

def authenticatePeer(address):
    # generate private key, unique to the peer
    privKey = RSA.generate(2048)

    # derive public key from private key and export
    pubKey = privKey.publickey().exportKey("PEM").decode('utf-8')

    # remove newlines in pub and priv key
    pubKeyFormatted = ''.join([item for item in pubKey.split('\n')])
    privKeyFormatteed = ''.join([item for item in privKey.exportKey("PEM").decode('utf-8').split('\n')])

    # insert key in db
    # pyddle.dbPeers.insert([address, privKeyFormatteed, pubKeyFormatted, 'authInProg'])
    pyddle.dbPeers.insert([address, privKey.exportKey("PEM").decode('utf-8'), pubKey, 'authInProg'])

    # send public key
    pyddle.p2pNode.connectandsend(address, 51234, 'KREQ', pubKey)

def handleKREQ(peerconn, msgdata):
    """ this handles the key request, it *is* the key responder """

    # generate private key, unique to the peer
    privKey = RSA.generate(2048)

    # derive public key from private key and export
    pubKey = privKey.publickey().exportKey("PEM").decode('utf-8')

    # remove newlines in pub and priv key
    pubKeyFormatted = ''.join([item for item in pubKey.split('\n')])
    privKeyFormatteed = ''.join([item for item in privKey.exportKey("PEM").decode('utf-8').split('\n')])

    # reply with our public key
    pyddle.p2pNode.connectandsend(peerconn.host, 51234, 'KRES', pubKey)

    # store info in db
    # pyddle.dbPeers.insert([peerconn.host, privKeyFormatteed, pubKeyFormatted, str(msgdata)])
    pyddle.dbPeers.insert([peerconn.host, privKey.exportKey("PEM").decode('utf-8'), pubKey, str(msgdata)])

def handleKRES(peerconn, msgdata):
    """ this handles the key response. read the functions in plain english """

    # build condition
    c = "ip=" + "'" + peerconn.host + "'"

    # get our private key for the peer
    key = pyddle.dbPeers.get(c, 'selfPrivKey')
    key = key[0].replace('\n', """ \n """)
    selfPrivKey = RSA.import_key(key)

    # sign a verification message
    msg = SHA256.new(b'trustme?')
    verifMsg = pkcs1_15.new(selfPrivKey).sign(msg)

    # send with our signed verification message
    pyddle.p2pNode.connectandsend(peerconn.host, 51234, 'AREQ', str(verifMsg))

    # add the peer's public key to the database
    pyddle.dbPeers.update('peerPubKey=%s' % msgdata, 'ip=%s' % peerconn.host)

def handleAREQ(peerconn, msgdata):
    """ handle authentication requests """

    # build condition
    c = "ip=" + "'" + peerconn.host + "'"

    # get our private key for the peer
    selfPrivKey = RSA.import_key(pyddle.dbPeers.get(c, 'selfPrivKey'))
    # do this boi for everyone key = key[0].replace('\n', """ \n """) TODO

    # get their public key
    peerPubKey = RSA.import_key(pyddle.dbPeers.get(c, 'peerPubKey'))

    # check the signature
    try:
        pkcs1_15.new(peerPubKey).verify('trustme?', msgdata)
        logger.debug("The signature is valid.")

        # this peer is valid, add them to the list
        pyddle.p2pNode.addpeer(peerconn.host, peerconn.host, 51234)
        pyddle.p2pNode.addrouter({peerconn.host : [peerconn.host, peerconn.host, 51234]})

        # sign our own verification message
        verifMsg = pkcs1_15.new(selfPrivKey).sign('trustme?')

        # send with our signed verification message
        pyddle.p2pNode.connectandsend(peerconn.host, 51234, 'ARES', verifMsg)

    except (ValueError, TypeError):
        logger.debug("The signature is not valid.")
        pyddle.dbPeers.delete('ip=' % peerconn.host)
        #TODO blacklist the ip or something, its invalid

def handleARES(peerconn, msgdata):
    """ oh boy, our authentication request went through! lets see if this fellow is legit """

    # get their public key
    peerPubKey = RSA.import_key(pyddle.dbPeers.get('ip=%s' % peerconn.host, 'selfPrivKey'))

    # check the signature
    try:
        pkcs1_15.new(peerPubKey).verify('trustme?', msgdata)
        logger.debug("The signature is valid. We made a new friend!")

        # yay, we made a new friend! add them to the node list
        pyddle.p2pNode.addpeer(peerconn.host, peerconn.host, 51234)
        pyddle.p2pNode.addrouter({peerconn.host : [peerconn.host, peerconn.host, 51234]})

    except (ValueError, TypeError):
        logger.debug("The signature is not valid.")
        pyddle.dbPeers.delete('ip=' % peerconn.host)
        #TODO blacklist the ip or something, its invalid

def connBootstrap(host, port=51234):
    pyddle.dbPeers = pyddle.database.databaseUtil.database('peers', True)
    pyddle.p2pNode = pyddle.p2p.p2pUtil.peer(25, port)
    pyddle.p2pNode.addhandler('PING')
    pyddle.p2pNode.addhandler('ECHO', handleECHO)
    pyddle.p2pNode.addhandler('KREQ', handleKREQ)
    pyddle.p2pNode.addhandler('KRES', handleKRES)
    pyddle.p2pNode.addhandler('AREQ', handleAREQ)
    pyddle.p2pNode.addhandler('ARES', handleARES)
    t = threading.Thread(target=pyddle.p2pNode.mainloop)
    t.start()
    pyddle.p2pNode.addpeer('bootstrap', host, port)
    pyddle.p2pNode.addrouter({'bootstrap' : ['bootstrap', host, port]})
    pyddle.p2pNode.sendtopeer('bootstrap', 'PING', '')
    authenticatePeer(host)

def runBootstrap(host, port=51234):
    pyddle.dbPeers = pyddle.database.databaseUtil.database('peers', True)
    pyddle.p2pNode = pyddle.p2p.p2pUtil.peer(25, port, myid='bootstrap')
    pyddle.p2pNode.addhandler('PING')
    pyddle.p2pNode.addhandler('ECHO', handleECHO)
    pyddle.p2pNode.addhandler('KREQ', handleKREQ)
    pyddle.p2pNode.addhandler('KRES', handleKRES)
    pyddle.p2pNode.addhandler('AREQ', handleAREQ)
    pyddle.p2pNode.addhandler('ARES', handleARES)
    t = threading.Thread(target=pyddle.p2pNode.mainloop)
    t.start()
