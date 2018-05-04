#!/usr/bin/env python3

""" requester """

# imports
import requests


def request():
    r = requests.post("http://127.0.0.1:8081",
                      json={'key': 'value', 'we': 'de'})
    print(r.text)
