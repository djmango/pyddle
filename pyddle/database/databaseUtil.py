#!/usr/bin/env python3

""" database class, contains everything needed for data storage, retrieval, and management """

import logging
import os
import sqlite3

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)


class database:
    """ contains everything needed for data storage, retrieval, and management. 
    when a new instance of this class is created, a table is specified. 
    this will be the table refering to the module that is utilizing the class. 
    optimally, a module should not use a table that is not its own, 
    however i am not omniscient so i dont know if this will change in the future """

    def __init__(self, table, debug=False):

        self.table = table
        self.debug = debug
        self.__dbConnect()

    def __dbConnect(self):
        self.dbConn = sqlite3.connect(path + '/database/db.sqlite')
        self.db = self.dbConn.cursor()

    def __loadTable(self, table):
        self.db

    def insertIntoTable(self, table, data):
        for i in data:
            logger.info(i)
