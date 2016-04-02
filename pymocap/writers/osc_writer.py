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
        # attributes
        self.client = None
        self.running = False
        self.connected = False

        # events
        self.connectEvent = Event()
        self.disconnectEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.start()

    def __del__(self):
        self.stop()

    def configure(self, options):
        # we might need the overwritten options
        previous_options = self.options
        # overwrite/update configuration
        self.options = dict(previous_options.items() + options.items())

        # new host or port configs? We need to reconnect, but only if we're running
        if ('host' in options or 'port' in options) and self.running:
            self.stop()
            self.start()

        # new manager? register callback
        if 'manager' in options:
            # unregister from previous manager if we had one
            if 'manager' in previous_options and previous_options['manager']:
                previous_options['manager'].frameEvent -= self._onFrame
            # register callback on new manager
            if options['manager']: # could also be None if caller is UNsetting the manager
                options['manager'].frameEvent += self._onFrame

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        self._disconnect()
        self.running = False

    def port(self):
        # default is 8080
        return int(self.options['port']) if 'port' in self.options else 8080

    def host(self):
        # default is localhost
        return self.options['host'] if 'host' in self.options else '127.0.0.1'

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

    # callback, called when manager gets a new frame of mocap data
    def _onFrame(self, frame, manager):
        if not self.running: return

        # sound out OSC message for every rigid body in the frame
        for rb in frame.rigid_bodies:
            self._sendMessage('/rigidbody', json.dumps({
                'id': rb.id,
                # 'name': rb.name,
                'position': rb.position,
                'orientation': rb.orientation
            }))

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
            # try to connect when we send the next message
