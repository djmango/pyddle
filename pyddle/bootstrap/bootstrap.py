#!/usr/bin/env python3

""" the bootstrap system for initial connection to the puddle network """

import json
import logging
import os
import socket

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)

clients = []


def main(host, port):
    db = pyddle.database.databaseUtil.database('bootstrap', True)
    bootstrap = pyddle.p2p.p2pUtil.peer(25, 3132)
    bootstrap.addhandler('test')
    bootstrap.addhandler('ping')
    bootstrap.mainloop()
