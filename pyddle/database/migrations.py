#!/usr/bin/env python3

""" migration functions unique to submodule """

# imports
import sqlite3
from pyddle import bootstrap

def migrateBootstrap():
    """ creates bootstrap table in bootstrap.db """
    dbconn = sqlite3.connect('./database/bootstrap.db')
    db = dbconn.cursor()
    db.execute(""" create table bootstrap (ip varchar(50), privKey varchar(1000), pubKey varchar(1000)) """)

    dbconn.commit()
    dbconn.close()
