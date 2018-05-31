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
    however i am not omniscient so i dont know if this will change in the future

        [table]: the table used for this instance, will be auto-populated if not already
    """

    def __init__(self, table, debug=False):
        self.table = table
        self.debug = debug
        self.__dbConnect()

    def __dbConnect(self):
        # initialize server connection
        self.dbConn = sqlite3.connect(path + '/database/db.sqlite', isolation_level=None)
        self.db = self.dbConn.cursor()

        # check if table exists
        self.db.execute(""" select name from sqlite_master where type='table' and name='%s'""" % self.table)
        # if table does not exist, create correct table
        if self.db.fetchone() is None:
            if self.table == 'peers':
                logger.debug('creating peers table')
                self.db.execute(""" create table peers (ip varchar(50), selfPrivKey varchar(5000), selfPubKey varchar(5000), peerPubKey varchar(1000)) """)
            if self.table == 'test':
                self.db.execute(""" create table test (t1 varchar(50), t2 varchar(50)) """)

    def insert(self, data):
        """ orginize given data and insert into table

            [data]: a standard list, this is what will be entered into the columns, in order
        """
        
        # when inserting n amount of values, we must parse the data into a single string
        values = ''
        n = 0
        for i in data:
            n = n + 1
            if n == len(data):
                values = values + "'" + i + "'"
            else:
                values = values + "'" + i + "', "

        # build query
        q = "insert into %s values (%s)" % (self.table, values)

        # insert into table
        self.db.execute(q)
    
    def update(self, data, where):
        """ update specified rows

            [data]: column1 = value1, column2 = value2

            [where]: a sql condition
        """

        # build query
        q = "update %s set %s where %s" % (self.table, where, data)

        # update values
        self.db.execute(q)

    def get(self, condition, select='*'):
        """ query table and retrieve all corresponding entries

            [condition]: sql conditions

            [select]: (optional) specify columns to return
        """

        # for some stupid reason, this wont work unless i reinitialize the connection
        self.__dbConnect()

        # build query, if you need to sanatize any input, use ? and use the built in string builder
        q = "select %s from %s where %s" % (select, self.table, condition)

        # execute query
        self.db.execute(q)

        # get first row and return
        return self.db.fetchone()

    def delete(self, where):
        """ delete a row

            [where]: a sql conditions
        """

        if self.table == "peers":
            self.db.execute("delete from peers where ?", (where))
        if self.table == "test":
            self.db.execute("delete from test where ?", (where))
