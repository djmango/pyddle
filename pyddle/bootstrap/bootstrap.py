#!/usr/bin/env python3

""" the bootstrap system for initial connection to the puddle network """

import json
import logging
import os
import socket
import threading
import time

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


def handleECHO(peerconn, msgdata):
    logger.info(peerconn.host)
    pyddle.bootstrapNode.connectandsend(peerconn.host, 51234, 'ECHO', msgdata)

def main(host, port):
    db = pyddle.database.databaseUtil.database('bootstrap', True)
    pyddle.bootstrapNode = pyddle.p2p.p2pUtil.peer(25, 51234)
    pyddle.bootstrapNode.addhandler('echo', handleECHO)
    pyddle.bootstrapNode.addhandler('ping')
    t = threading.Thread(target=pyddle.bootstrapNode.mainloop)
    t.start()
