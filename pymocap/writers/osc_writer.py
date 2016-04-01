from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

import json

try:
    import OSC
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for OscWriter")
    import pymocap.dependencies.OSC as OSC

class OscWriter:
    def __init__(self, host="127.0.0.1", port=8080, manager=None, autoStart=True):
        self.configure(host=host, port=port, manager=manager)
        self.setup()

        if autoStart == True:
            self.start()

    def __del__(self):
        self.destroy()

    def setup(self):
        self.client = None
        self.running = False
        self.connected = False

        self.connectEvent = Event()
        self.disconnectEvent = Event()

    def destroy(self):
        self.stop()

    def configure(self, host=None, port=None, manager=None):
        if host:
            self.host = host
        if port:
            self.port = port
        if manager:
            self._setManager(manager)

        if (host or port) and hasattr(self, 'running') and self.running:
            self.stop()
            self.start()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        self._disconnect()
        self.running = False

    def _connect(self):
        try:
            self.client = OSC.OSCClient()
            self.client.connect((self.host, int(self.port)))
        except OSC.OSCClientError as err:
            ColorTerminal().error("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        ColorTerminal().success("OSC client connected to " + self.host + ':' + str(self.port))
        self.connectEvent(self)
        return True

    def _disconnect(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()
            self.client = None
            self.connected = False
            ColorTerminal().success("OSC client closed")
            self.disconnectEvent(self)

    def _setManager(self, manager):
        if hasattr(self, 'manager') and self.manager:
            self.manager.frameEvent -= self.onFrame

        self.manager = manager

        if self.manager: # could also be None
            self.manager.frameEvent += self.onFrame

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
