from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

try:
    import optirx as rx
except ImportError:
    ColorTerminal().warn("importing embedded version of the optirx library for NatnetReader")
    import pymocap.dependencies.optirx as rx

import threading

class NatnetReader:
    def __init__(self, host='0.0.0.0', multicast=None, port=1511, manager=None, threaded=False, autoStart=True):
        # configuration
        self.host = host
        self.multicast = multicast
        self.port = port
        self.manager = manager
        self.threaded = threaded

        # networking attributes
        self.connected = False
        self.dsock = None
        self.connection_error = None

        # threading attributes
        self.thread = threading.Thread(target=self._threaded_main)
        self._kill = False

        # events
        self.connectionLostEvent = Event()
        self.connectEvent = Event()
        self.connectionStatusUpdateEvent = Event()

        if autoStart:
            self.start()

    def __del__(self):
        self.stop()

    def update(self):
        if not self.dsock:
            # we need a connection to do anything
            return

        try:
            data = self.dsock.recv(rx.MAX_PACKETSIZE)
        except Exception as e:
            # error: [Errno 35] Resource temporarily unavailable
            # print('socket receive err: ', e.strerror)
            if self.connection_error != e.strerror:
                self.connection_error = e.strerror
                self.connectionStatusUpdateEvent(self)

            # connection issue, abort
            return

        # getting here, means there was no issue with connection
        if self.connection_error != None:
            # change connection status back to normal (None)
            self.connection_error = None
            # send notifications
            self.connectionStatusUpdateEvent(self)

        # give data to the manager
        self.manager.processFrameData(data)

    def start(self):
        self._connect()

        if not self.threaded:
            # done here
            return

        if self.thread and self.thread.isAlive():
            ColorTerminal().warn("NatnetReader - thread already running")
            return

        # start thread
        self._kill = False
        self.thread.start()

    def stop(self):
        self._disconnect()
        if self.threaded:
            # tell thread to stop
            self._kill = True

    def configure(self, host=None, multicast=None, port=None):
        if host:
            self.host = host
        if multicast:
            self.multicast = multicast
        if port:
            self.port = port

        # if connection is active; reconnect with new configuration
        if (host or port or multicast) and self.connected:
            self.stop()
            self.start()

    def _threaded_main(self):
        while not self._kill:
            self.update()

    def _connect(self):
        try:
            if self.host is None:
                self.dsock = rx.mkdatasock() #Connecting to localhost
            elif self.multicast is not None and self.multicast is not '' and self.port is not None:
                ColorTerminal().blue("NatnetReader connecting to natnet @ %s:%s (multicast: %s)" % (self.host, self.port, self.multicast))
                self.dsock = rx.mkdatasock(ip_address=self.host, multicast_address=self.multicast, port=int(self.port)) #Connecting to multicast address
            else:
                ColorTerminal().blue("NatnetReader connecting to natnet @ %s:%s" % (self.host, self.port))
                self.dsock = rx.mkdatasock(ip_address=self.host, port=int(self.port)) # Connecting to IP address

            self.dsock.setblocking(0)
            self.connected = True
            self.connectEvent(self)
            ColorTerminal().green("NatnetReader Connected")
        except:
            ColorTerminal().red("NatnetReader encountered an error while connecting")
            self._disconnect()

        return self.connected

    def _disconnect(self):
        self.dsock = None
        self.connected = False
        self.connectionLostEvent(self)
        ColorTerminal().green("NatnetReader Disconnected")
