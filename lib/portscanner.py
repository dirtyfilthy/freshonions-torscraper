import random
from datetime import *
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.task import react

from txsocksx.client import SOCKS5ClientEndpoint
from tor_db import *

from twisted.internet import reactor
TOR_HOST = os.environ['HIDDEN_SERVICE_PROXY_HOST']
TOR_PORT = int(os.environ['HIDDEN_SERVICE_PROXY_PORT'])
MAX_TOTAL_CONNECTIONS = 16
MAX_CONNECTIONS_PER_HOST = 1

PORTS = { 8333  : "bitcoin", 
          9051  : "bitcoin-control",
          9333  : "litecoin", 
          22556 : "dogecoin",
          6697  : "irc",
          6667  : "irc",
          143   : "imap",
          110   : "pop3",
          119   : "nntp",
          22    : "ssh",
          2222  : "ssh?",
          23    : "telnet",
          25    : "smtp",
          80    : "http",
          443   : "https",
          21    : "ftp",
          5900  : "vnc",
          27017 : "mongodb",
          9200  : "elasticsearch",
          3128  : "squid-proxy?",
          8080  : "proxy?" ,
          8118  : "proxy?" ,
          8000  : "proxy?" ,
          9878  : "richochet",
          666   : "hail satan!",
          31337 : "eleet",
          1337  : "eleet",
          69    : "good times",
          6969  : "double the fun",
          1234  : "patterns rule",
          12345 : "patterns rule",
        }

def pop_or_none(l):
    if len(l) == 0:
        return None
    return l.pop()


def get_service_name(port):
    return PORTS.get(port)

class PortScannerClient(Protocol):
    def connectionMade(self):
        self.data = []
        self.deferred = Deferred()
        self.transport.loseConnection()

    def dataReceived(self, data):
        self.data.append(data)

    def connectionLost(self, reason):
        self.factory.conn.next_port()
        #self.deferred.callback(''.join(self.data))

class PortScannerClientFactory(ClientFactory):

    def __init__(self, conn):
        self.conn = conn

    def buildProtocol(self, addr):
        p = PortScannerClient()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        print("connection lost")

    def clientConnectionFailed(self, connector, reason):
        print("connection failed")

def gotProtocol(p, conn):
    conn.active_host.add_open_port(conn.current_port)

def gotErr(failure, conn):
    conn.next_port()

class Connection:

    def __init__(self, scanner):
        self.scanner = scanner
        self.active_host = None
        self.current_port = None

    def next_port(self):
        self.current_port = self.active_host.next_port()
        if self.current_port:
            self.connect()
            return self.current_port
        else:
            print("%s is finished" % self.active_host.hostname)
            host = self.scanner.attach_to_next()
            if host is None:
                self.scanner.conn_finished(self)
                return None
            else:
                return self.attach_to(host)

    def attach_to(self, host):
        self.active_host = host
        self.active_host.n_conn += 1
        return self.next_port()


    def connect(self):
        torEndpoint = TCP4ClientEndpoint(reactor, TOR_HOST, TOR_PORT)
        proxiedEndpoint = SOCKS5ClientEndpoint(self.active_host.hostname.encode("ascii"), self.current_port, torEndpoint)
        d = proxiedEndpoint.connect(PortScannerClientFactory(self))
        d.addCallback(gotProtocol, self)
        d.addErrback(gotErr, self)
        #reactor.callLater(60, d.cancel)




class ActiveHost():
    @db_session
    def __init__(self, hostname):
        self.hostname = hostname
        self.port_queue = list(PORTS.keys())
        #self.port_queue = [80]
        self.n_conn = 0
        self.domain = Domain.find_by_host(self.hostname)
        self.domain.portscanned_at = datetime.now()
        random.shuffle(self.port_queue)
        self.domain.open_ports.clear()

    @db_session
    def add_open_port(self, port):
        print("Found open port %s:%d" % (self.hostname, port))
        domain = Domain.find_by_host(self.hostname)
        domain.open_ports.create(port=port)

    def next_port(self):
        return pop_or_none(self.port_queue)



class PortScanner:
    
    
    def conn_new(self):
        self.n_conn += 1
        return Connection(self)

    def conn_finished(self, conn):
        self.n_conn -= 1
        if self.n_conn < 1:
            reactor.stop()

    def attach_to_next(self):
        if self.last is None or self.last.n_conn >= MAX_CONNECTIONS_PER_HOST:
            hostname = pop_or_none(self.host_queue)
            if hostname:
                self.last = ActiveHost(hostname) 
            else:
                self.last = None 
        return self.last

    def __init__(self, hosts):
        self.host_queue   = list(hosts)
        self.active_hosts = list()
        self.n_conn       = 0
        self.last         = None
     
        for i in range(0, MAX_TOTAL_CONNECTIONS):
            host = self.attach_to_next()
            if host:
                conn = self.conn_new()
                conn.attach_to(host)

        reactor.run()
            