#!/usr/bin/env python3

""" pyddle is the python implementation of the puddle system """

import argparse
import logging
from os import path
from time import time
import sys

# get start time before pyddle package import, as included packages are predictable
start_time = time()

# god?
import pyddle

# nobodyreadsme.md
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s (%(name)s) %(message)s', stream=sys.stdout)

# find god?
path = path.dirname(pyddle.__file__)
logging.info('found pyddle at ' + path)

parser = argparse.ArgumentParser(description='python3 implementation of the puddle system')
parser.add_argument('-t', '--test', help='test flag, runs specified test')

args = parser.parse_args()

if (args):
    testArg = args.test
    if (testArg == 'what'):
        # temp test, for whatever im doing
        pyddle.test.test.getPath()

logging.info("executed in %s seconds" % (time() - start_time))
