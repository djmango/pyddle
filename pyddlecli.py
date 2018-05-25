#!/usr/bin/env python3

""" pyddle is the python implementation of the puddle system """

import argparse
import logging
from os import path
from time import time
import sys

# get start time before pyddle package import, as included packages are predictable
start_time = time()


import pyddle

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s (%(name)s) %(message)s', stream=sys.stdout)

path = path.dirname(pyddle.__file__)
logging.info('found pyddle at ' + path)

parser = argparse.ArgumentParser(description='python3 implementation of the puddle system')
parser.add_argument('-t', '--test', help='test flag, runs specified test')

args = parser.parse_args()

if (args):
    testArg = args.test
    if (testArg == 'what'):
        # temp test, for whatever im doing
        # pyddle.p2p.p2p.connBootstrap('35.185.101.249', 8081)
        # pyddle.p2p.p2p.connBootstrap('127.0.0.1', 8081)
        # b = pyddle.database.databaseUtil.database('test', True)
        # b.insert(['jhon', 'groceryies'])
        # logging.info(b.get("t1='jhon'"))
        pyddle.bootstrap.bootstrap.main('0.0.0.0', 3132)
    
    if (testArg == 'w'):
        pyddle.p2p.p2p.connBootstrap('127.0.0.1', 3132)

logging.info("executed in %s seconds" % (time() - start_time))
