#!/usr/bin/env python3

""" migration functions unique to submodule """

# imports
import os
import sqlite3

import pyddle

# get project path
path = os.path.dirname(pyddle.__file__)


def migrateBootstrap():
    """ creates bootstrap table in bootstrap.db """
    dbconn = sqlite3.connect(path + '/database/bootstrap.db')
    db = dbconn.cursor()
    db.execute(
        """ create table bootstrap (ip varchar(50), privKey varchar(1000), pubKey varchar(1000)) """)

    dbconn.commit()
    dbconn.close()
