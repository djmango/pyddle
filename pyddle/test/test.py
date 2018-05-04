#!/usr/bin/env python3

""" tests for pyddle, should include a function for pretty much everything i care about """

import os
import pyddle

path = os.path.dirname(pyddle.__file__)

def getPath():
    print(path)
