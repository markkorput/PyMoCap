from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

import json

try:
    import OSC
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for OscWriter")
    import pymocap.dependencies.OSC as OSC

class OscWriter:
    def __init__(self, options = {}):
        self.client = None
        self.running = False
        self.connected = False

        self.connectEvent = Event()
        self.disconnectEvent = Event()

        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.start()

    def __del__(self):
        self.stop()

    def configure(self, options):
        previous_options = self.options
        self.options = dict(previous_options.items() + options.items())

        # new host or port configs? We need to reconnect, but only if we're running
        if ('host' in options or 'port' in options) and self.running:
            self.stop()
            self.start()

        # new manager? register callback
        if 'manager' in options:
            # unregister from any previous manager
            if 'manager' in previous_options and previous_options['manager']:
                previous_options['manager'].frameEvent -= self.onFrame
            # register callback on new manager
            if options['manager']: # could also be None
                options['manager'].frameEvent += self.onFrame

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        self._disconnect()
        self.running = False

    def _connect(self):
        try:
            self.client = OSC.OSCClient()
            self.client.connect((self.host(), self.port()))
        except OSC.OSCClientError as err:
            ColorTerminal().error("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        ColorTerminal().success("OSC client connected to " + self.host() + ':' + str(self.port()))
        self.connectEvent(self)
        return True

    def _disconnect(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()
            self.client = None
            self.connected = False
            ColorTerminal().success("OSC client closed")
            self.disconnectEvent(self)

    def port(self):
        # default is 8080
        return int(self.options['port']) if 'port' in self.options else 8080

    def host(self):
        return self.options['host'] if 'host' in self.options else '127.0.0.1'

    def onFrame(self, frame, manager):
        if not self.running:
            return

        for rb in frame.rigid_bodies:
            obj = {
                'id': rb.id,
                # 'name': rb.name,
                'position': rb.position,
                'orientation': rb.orientation
            }

            self._sendMessage('/rigidbody', json.dumps(obj))

    def _sendMessage(self, tag, content):
        msg = OSC.OSCMessage()
        msg.setAddress(tag) # set OSC address
        msg.append(content)

        try:
            self.client.send(msg)
        except OSC.OSCClientError as err:
            pass
            # ColorTerminal().warn("OSC failure: {0}".format(err))
            # no need to call connect again on the client, it will automatically
            # try to connect when we send ou next message
