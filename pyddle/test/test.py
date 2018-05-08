#!/usr/bin/env python3

""" tests for pyddle, should include a function for pretty much everything i care about """

import os
import pyddle
import logging
import sys

path = os.path.dirname(pyddle.__file__)
logging.basicConfig(level=logging.INFO, message='%(asctime)s %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)

def getPath():
    logger.info(path)
