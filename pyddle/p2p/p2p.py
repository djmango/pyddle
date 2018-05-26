#!/usr/bin/env python3

""" the p2p system is designed to locate all possible peers, and check if they are alive """

import logging
import os
from threading import Event, Thread
from time import sleep

import requests

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


def connBootstrap(host, port):
    selfPeer = pyddle.p2p.p2pUtil.peer(25, 3131, debug=True)
    selfPeer.addhandler('ping')
    selfPeer.addpeer('bootstrap', host, 3132)
    selfPeer.addrouter({'bootstrap' : ['bootstrap', host, port]})
    selfPeer.sendtopeer('bootstrap', 'PING', '')
    selfPeer.sendtopeer('bootstrap', 'TEST', 'hello im jeff')
