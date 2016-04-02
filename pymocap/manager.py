from pymocap.event import Event
from pymocap.color_terminal import ColorTerminal

try:
    import optirx as rx
except ImportError:
    ColorTerminal().warn("importing embedded version of the optirx library")
    import pymocap.dependencies.optirx as rx

class Manager:
    def __init__(self):
        self.setup()

    def setup(self):
        self.resetEvent = Event()
        self.frameDataEvent = Event()
        self.frameEvent = Event()

        self._natnet_version = (2, 7, 0, 0)
        self.reset()

    def reset(self):
        self.frame = None
        self.resetEvent(self)

    # take raw, binary, packed natnet frame data
    # it unpacks the data, stores it without further processing
    # and triggers notification
    def processFrameData(self, data):
        # notify about new (raw, binary) frame data
        self.frameDataEvent(data, self)
        # unpack
        packet = rx.unpack(data, version=self._natnet_version)
        # change natnet version if necessary
        if type(packet) is rx.SenderData:
            self._natnet_version = packet.natnet_version
        # store
        self.frame = packet
        # notify about new (unpacked) frame
        self.frameEvent(packet, self)
