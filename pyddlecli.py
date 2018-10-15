#!/usr/bin/env python3

""" pyddle is the python implementation of the puddle system """

import argparse
import logging
import os
from time import time
import sys

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

# get start time before pyddle package import, as included packages are predictable
start_time = time()


import pyddle

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(asctime)s (%(name)s) %(message)s', stream=sys.stdout)

path = os.path.dirname(pyddle.__file__)
logging.info('found pyddle at ' + path)

parser = argparse.ArgumentParser(description='python3 implementation of the puddle system')
parser.add_argument('-t', '--test', help='test flag, runs specified test')
parser.add_argument('-b', '--bootstrap', help='enables bootstrap mode', action='store_true')
parser.add_argument('-p', '--purge', help='purges p2p database', action='store_true')

args = parser.parse_args()    

if args:
    if args.purge:
        # purge the p2p database
        if os.path.exists(path + '/database/db.sqlite'):
            try:
                os.remove(path + '/database/db.sqlite')
                logging.info('purged database succesfully')
            except Exception as e:
                logging.error(e)
        else:
            logging.info('no database found, no need to purge')

    if args.bootstrap:
        # enable bootstrap mode
        bootstrap = True
    else:
        bootstrap = False

    if args.test:
        if (args.test == 'what'):
            # temp test, for whatever im doing
            # pyddle.p2p.p2p.connBootstrap('35.185.101.249', 8081)
            # pyddle.p2p.p2p.connBootstrap('127.0.0.1', 8081)
            # b = pyddle.database.databaseUtil.database('test', True)
            # b.insert(['jhon', 'groceryies'])
            # logging.info(b.get("t1='jhon'"))
            pyddle.p2p.p2p.runBootstrap('0.0.0.0')
        
        if (args.test == 'w'):
            pyddle.p2p.p2p.connBootstrap('192.168.192.96', bootstrap)

        if (args.test == 't'):
            b = pyddle.database.databaseUtil.database('test', True)
            b.insert(['jhon', 'groceryies'])
            logging.info(b.get("t1='jhon'"))
            c = pyddle.database.databaseUtil.database('peers', True)

logging.info("executed in %s seconds" % (time() - start_time))
