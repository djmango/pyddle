#!/usr/bin/env python3

""" peer and peerConnection classes, contains everything needed for basic p2p communication and management """

import logging
import os
import socket
import ssl
import threading
import time
import traceback

import pyddle

path = os.path.dirname(pyddle.__file__)
logger = logging.getLogger(__name__)

# the following classes are based off of:
# python p2p framework base @ http://cs.berry.edu/~nhamid/p2p/framework-python.html

class peer:
    """ Implements the core functionality that might be used by a peer in a
    P2P network.

    """

    def __init__(self, maxpeers, serverport, myid=None, serverhost=None, debug=False, bootstrap=False):
        """ Initializes a peer servent (sic.) with the ability to catalog
        information for up to maxpeers number of peers (maxpeers may
        be set to 0 to allow unlimited number of peers), listening on
        a given server port , with a given canonical peer name (id)
        and host address. If not supplied, the host address
        (serverhost) will be determined by attempting to connect to an
        Internet host like Google.

        """
        self.debug = debug
        self.maxpeers = int(maxpeers)
        self.serverport = int(serverport)
        self.bootstrap = bootstrap
        if serverhost:
            self.serverhost = serverhost
        else:
            self.__initserverhost()

        if myid:
            self.myid = myid
        else:
            self.myid = '%s:%d' % (self.serverhost, self.serverport)

        self.peerlock = threading.Lock()  # ensure proper access to
        # peers list (maybe better to use
        # threading.RLock (reentrant))
        self.peers = {}        # peerid ==> (host, port) mapping
        self.shutdown = False  # used to stop the main loop

        self.handlers = {}
        self.router = None

        # context setup
        self.serverContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.serverContext.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 # disable the outdated
        self.serverContext.set_ciphers('EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH') # from https://cipherli.st/

    def __initserverhost(self):
        """ Attempt to connect to an Internet host in order to determine the
        local machine's IP address.

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("www.google.com", 80))
        self.serverhost = s.getsockname()[0]
        logger.debug('Found self at ' + self.serverhost)
        s.close()

    def __handlepeer(self, clientsock):
        """
        handlepeer( new socket connection ) -> ()

        Dispatches messages from the socket connection
        """

        logger.debug('New child ' + str(threading.currentThread().getName()))
        logger.debug('Connected ' + str(clientsock.getpeername()))

        host, port = clientsock.getpeername()
        peerconn = peerConnection(str(host), host, port, clientsock, debug=False, bootstrap=self.bootstrap)

        try:
            msgtype, msgdata = peerconn.recvdata()
            if msgtype:
                msgtype = msgtype.upper()
            if msgtype not in self.handlers:
                logger.debug('Not handled: %s: %s' % (msgtype, msgdata))
            else:
                logger.debug('Handling peer msg: %s: %s' % (msgtype, msgdata))
                self.handlers[msgtype](peerconn, msgdata)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        logger.debug('Disconnecting ' + str(clientsock.getpeername()))
        peerconn.close()
        # end handlepeer method

    def __runstabilizer(self, stabilizer, delay):

        while not self.shutdown:
            stabilizer()
            time.sleep(delay)

    def setmyid(self, myid):

        self.myid = myid

    def startstabilizer(self, stabilizer, delay):
        """ Registers and starts a stabilizer function with this peer. 
        The function will be activated every <delay> seconds. 

        """
        t = threading.Thread(target=self.__runstabilizer,
                             args=[stabilizer, delay])
        t.start()

    def addhandler(self, msgtype, handler=None):
        """ Registers the handler for the given message type with this peer """
        assert len(msgtype) == 4
        self.handlers[msgtype.upper()] = handler

    def addrouter(self, router):
        """ Registers a routing function with this peer. The setup of routing
        is as follows: This peer maintains a list of other known peers
        (in self.peers). The routing function should take the name of
        a peer (which may not necessarily be present in self.peers)
        and decide which of the known peers a message should be routed
        to next in order to (hopefully) reach the desired peer. The router
        function should return a tuple of three values: (next-peer-id, host,
        port). If the message cannot be routed, the next-peer-id should be
        None.

        """
        self.router = router

    def addpeer(self, peerid, host, port):
        """ Adds a peer name and host:port mapping to the known list of peers.

        """
        if peerid not in self.peers and (self.maxpeers == 0 or
                                         len(self.peers) < self.maxpeers):
            self.peers[peerid] = (host, int(port))
            return True
        else:
            return False

    def getpeer(self, peerid):
        """ Returns the (host, port) tuple for the given peer name """
        assert peerid in self.peers    # maybe make this just a return NULL?
        return self.peers[peerid]

    def removepeer(self, peerid):
        """ Removes peer information from the known list of peers. """
        if peerid in self.peers:
            del self.peers[peerid]

    def addpeerat(self, loc, peerid, host, port):
        """ Inserts a peer's information at a specific position in the 
        list of peers. The functions addpeerat, getpeerat, and removepeerat
        should not be used concurrently with addpeer, getpeer, and/or 
        removepeer. 

        """
        self.peers[loc] = (peerid, host, int(port))

    def getpeerat(self, loc):

        if loc not in self.peers:
            return None
        return self.peers[loc]

    def getpeerids(self):
        """ Return a list of all known peer id's. """
        return list(self.peers.keys())

    def numberofpeers(self):
        """ Return the number of known peer's. """
        return len(self.peers)

    def maxpeersreached(self):
        """ Returns whether the maximum limit of names has been added to the
        list of known peers. Always returns True if maxpeers is set to
        0.

        """
        assert self.maxpeers == 0 or len(self.peers) <= self.maxpeers
        return self.maxpeers > 0 and len(self.peers) == self.maxpeers

    def makeserversocket(self, port, backlog=5):
        """ Constructs and prepares a server socket listening on the given 
        port.

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s = self.serverContext.wrap_socket(s, server_side=True)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(backlog)
        return s

    def sendtopeer(self, peerid, msgtype, msgdata, waitreply=True):
        """
        sendtopeer( peer id, message type, message data, wait for a reply )
         -> [ ( reply type, reply data ), ... ] 

        Send a message to the identified peer. In order to decide how to
        send the message, the router handler for this peer will be called.
        If no router function has been registered, it will not work. The
        router function should provide the next immediate peer to whom the 
        message should be forwarded. The peer's reply, if it is expected, 
        will be returned.

        Returns None if the message could not be routed.
        """

        if self.router:
            nextpid, host, port = self.router[peerid]
        if not self.router or not nextpid:
            logger.debug('Unable to route %s to %s' % (msgtype, peerid))
            return None
        #host,port = self.peers[nextpid]      
        return self.connectandsend(host, port, msgtype, msgdata,
                                   pid=nextpid,
                                   waitreply=waitreply)

    def connectandsend(self, host, port, msgtype, msgdata,
                       pid=None, waitreply=True):
        """
        connectandsend( host, port, message type, message data, peer id,
        wait for a reply ) -> [ ( reply type, reply data ), ... ]

        Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list of tuples.

        """
        msgreply = []
        try:
            print(pid)
            print(host)
            print(port)
            print(type(msgdata))
            print(msgtype)
            print(self.bootstrap)
            peerconn = peerConnection(pid, host, port, debug=self.debug, bootstrap=self.bootstrap)
            print('got peercon')
            peerconn.senddata(msgtype, msgdata)
            logger.debug('Sent %s: %s' % (pid, msgtype))

            if waitreply:
                onereply = peerconn.recvdata()
                while (onereply != (None, None)):
                    msgreply.append(onereply)
                    logger.debug('Got reply %s: %s'
                                 % (pid, str(msgreply)))
                    onereply = peerconn.recvdata()
            peerconn.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        return msgreply

    # end connectsend method

    def checklivepeers(self):
        """ Attempts to ping all currently known peers in order to ensure that
        they are still active. Removes any from the peer list that do
        not reply. This function can be used as a simple stabilizer.

        """
        todelete = []
        for pid in self.peers:
            isconnected = False
            try:
                logger.debug('Check live %s' % pid)
                host, port = self.peers[pid]
                peerconn = peerConnection(pid, host, port, debug=self.debug, bootstrap=self.bootstrap)
                peerconn.senddata('PING', '')
                isconnected = True
            except:
                todelete.append(pid)
            if isconnected:
                peerconn.close()

        self.peerlock.acquire()
        try:
            for pid in todelete:
                if pid in self.peers:
                    del self.peers[pid]
        finally:
            self.peerlock.release()
    # end checklivepeers method

    def mainloop(self):

        s = self.makeserversocket(self.serverport)
        s.settimeout(2)
        logger.debug('Server started: %s (%s:%d)'
                     % (self.myid, self.serverhost, self.serverport))

        while not self.shutdown:
            try:
                logger.debug('Listening for connections...')
                clientsock, clientaddr = s.accept()
                clientsock.settimeout(None)
                clientsock = self.serverContext.wrap_socket(clientsock, server_side=True)

                t = threading.Thread(target=self.__handlepeer,
                                     args=[clientsock])
                t.start()
            except KeyboardInterrupt:
                logger.info('KeyboardInterrupt: stopping mainloop')
                self.shutdown = True
                continue
            except ssl.SSLError as e:
                logger.debug(e)
                continue
            except:
                if self.debug:
                    traceback.print_exc()
                    continue

        # end while loop
        logger.debug('Main loop exiting')

        s.close()

    # end mainloop method


class peerConnection:

    def __init__(self, peerid, host, port, sock=None, debug=False, bootstrap=False):

        # any exceptions thrown upwards

        self.id = peerid
        self.debug = debug
        self.host = host
        self.port = port
        self.bootstrap = bootstrap

        if not sock:
            # self.context = context = ssl.create_default_context()
            self.clientContext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.clientContext.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # disable the outdated 
            self.clientContext.set_ciphers('EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH') # from https://cipherli.st/

            self.s.connect((host, int(port)))
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s = self.clientContext.wrap_socket(self.s)

        else:
            self.s = sock

    def __makemsg(self, msgtype, msgdata):

        # force msglen to be 8 chars
        msglen = str(len(msgdata))
        if int(msglen) > 99999999:
            logger.error('message can not be longer than 99,999,999 chars')
        while 8 - len(msglen) != 0:
            msglen = '0' + msglen

        msg = msgtype.encode() + msglen.encode() + msgdata.encode()
        return(msg)

    def senddata(self, msgtype, msgdata):
        """
        senddata( message type, message data ) -> boolean status

        Send a message through a peer connection. Returns True on success
        or False if there was an error.
        """

        try:
            msg = self.__makemsg(msgtype, msgdata)
            self.s.send(msg)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return False
        return True

    def recvdata(self):
        """
        recvdata() -> (msgtype, msgdata)

        Receive a message from a peer connection. Returns (None, None)
        if there was any error.
        """

        try:
            msgtype = self.s.recv(4).decode()
            if not msgtype:
                return (None, None)

            msglen = int(self.s.recv(8).decode())
            msgdata = ""

            if len(msgdata) != msglen:
                data = self.s.recv(min(2048, msglen - len(msgdata))).decode()
                msgdata += data

            if len(msgdata) != msglen:
                return (None, None)
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return (None, None)

        return (msgtype, msgdata)

    # end recvdata method

    def close(self):
        """
        close()

        Close the peer connection. The send and recv methods will not work
        after this call.
        """

        self.s.close()
        self.s = None

    def __str__(self):

        return "|%s|" % self.id
