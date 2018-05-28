#!/usr/bin/env python3

""" the p2p system is designed to locate all possible peers, and check if they are alive """

import logging
import os
import threading

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


def handleTEST(peerconn, msgdata):
    logger.info(msgdata)
    logger.info(peerconn.id)

def handleECHO(peerconn, msgdata):
    logger.info(peerconn.host)
    pyddle.selfNode.connectandsend(peerconn.host, 51234, 'ECHO', msgdata)

def connBootstrap(host, port):
    pyddle.selfNode = pyddle.p2p.p2pUtil.peer(25, 51234)
    pyddle.selfNode.addhandler('ping')
    pyddle.selfNode.addhandler('echo', handleECHO)
    t = threading.Thread(target=pyddle.selfNode.mainloop)
    t.start()
    pyddle.selfNode.addpeer('bootstrap', host, 51234)
    pyddle.selfNode.addrouter({'bootstrap' : ['bootstrap', host, port]})
    pyddle.selfNode.sendtopeer('bootstrap', 'PING', '')
    pyddle.selfNode.sendtopeer('bootstrap', 'ECHO', 'hello im jeff')
