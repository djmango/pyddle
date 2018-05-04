#!/usr/bin/env python3

""" pyddle is the python implementation of the puddle system """

# imports
import argparse
import logging
import os
import sys
import time

start_time = time.time()

import pyddle

parser = argparse.ArgumentParser(
    description='python3 implementation of the puddle system')
parser.add_argument('-t', '--test', help='test flag, runs specified test')

args = parser.parse_args()
print(args.test)

if (args.test):
    testArg = args.test
    if (testArg == 'what'):
        # temp test, for whatever im doing
        pyddle.test.test.getPath()

print("--- %s seconds ---" % (time.time() - start_time))
