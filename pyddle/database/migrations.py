#!/usr/bin/env python3

""" migration functions unique to submodule """

import logging
import os
import sqlite3

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


def migrateBootstrap():
    """ creates bootstrap table in bootstrap.db """
    dbconn = sqlite3.connect(path + '/database/bootstrap.db')
    db = dbconn.cursor()
    db.execute(""" create table bootstrap (ip varchar(50), privKey varchar(1000), pubKey varchar(1000)) """)

    dbconn.commit()
    dbconn.close()
