#!/usr/bin/env python3

""" the node acts as the http listener and sender for the rest of the system """

# imports
import threading
from pyddle.node import httplistener
from pyddle.node import httprequester

def main():
    threading.Thread(target=httplistener.run, daemon=True).start()
    threading.Thread(target=httprequester.request).start()
