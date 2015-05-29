# This file is part of the Pyvi software package. Released
# under the Creative Commons ATT-NC-ShareAlire license
# http://creativecommons.org/licenses/by-nc-sa/4.0/
# Copyright (C) 2014, 2015 LESS Industries S.A.
# Lucas Chiesa <lucas@lessinduestries.com>


import threading
import Queue
from utils import logs

from pyvi import MCUComm
from pyvi import ServerComm


class ThreadSerial(threading.Thread):

    def __init__(self, conf_file, transport, queues):
        """
        Threads that read from the Serial port and saves data to a Queue.
        """
        super(ThreadSerial, self).__init__()
        self.port = transport
        self.protocol = MCUComm()
        self.running = False
        self.l = logs.get_logger('Serial', conf_file=conf_file)
        self.queues = queues
        self.lr = logs.LogReader(conf_file)

    def run(self):
        self.running = True
        while self.running:
            try:
                pkg = self.port.read_package_from_xmega()
                if pkg is not None:
                    m = self.protocol.read(pkg)
                    for name, queue in self.queues.iteritems():
                        if not queue.full():
                            queue.put(m, timeout=0.1)
                            msg = "Read: {}".format(m)
                            self.l.debug(msg)
                        else:
                            self.l.error("Queue {} was full dropping {}".format(name, m))
            except:
                self.l.exception("Exception while reading from serial.")

    def kill(self):
        self.running = False


class ThreadUdp(threading.Thread):

    def __init__(self, conf_file, transport, pivi_id, queue):
        """
        Thread that reads from a Queue and sends data to a remote server
        """
        super(ThreadUdp, self).__init__()

        self.protocol = ServerComm(pivi_id=pivi_id)
        self.port = transport
        self.mac = self.protocol.less_mac
        self.running = False
        self.l = logs.get_logger('Udp', conf_file=conf_file)
        self.queue = queue
        self.lr = logs.LogReader(conf_file)

    def run(self):
        self.running = True
        while(self.running):
            try:
                m = self.queue.get(timeout=2)
                if m is not None:
                    msg = "Sending from mac: {}, pkg: {}".format(self.mac, m)
                    self.l.debug(msg)
                    pkg = self.protocol.pack(m)
                    self.port.write(pkg)
            except Queue.Empty:
                self.l.debug("Incoming queue empty")
            except:
                self.l.exception("Exception while sending via UDP.")

    def kill(self):
        self.running = False


class ThreadApi(threading.Thread):

    def __init__(self, conf_file, transport, queue):
        """
        Thread that reads from a Queue and sends data to a remote server
        """
        super(ThreadApi, self).__init__()

        self.port = transport
        self.running = False
        self.l = logs.get_logger('Api', conf_file=conf_file)
        self.queue = queue

    def run(self):
        self.running = True
        while self.running:
            try:
                m = self.queue.get(timeout=2)
                if m is not None:
                    result = self.port.write(m)
                    msg = "Sent pkg: {}, with result {}".format(m, result)
                    self.l.debug(msg)
            except Queue.Empty:
                self.l.debug("Incoming queue empty")
            except:
                self.l.exception("Exception while sending via API.")

    def kill(self):
        self.running = False
