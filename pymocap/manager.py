from pymocap.event import Event
from pymocap.color_terminal import ColorTerminal

try:
    import optirx as rx
except ImportError:
    ColorTerminal().warn("importing embedded version of the optirx library for PyMoCap.Manager")
    import pymocap.dependencies.optirx as rx

class Manager:
    def __init__(self):
        # events
        self.resetEvent = Event()
        self.frameDataEvent = Event()
        self.frameEvent = Event()

        # for natnet data unpacking
        self._natnet_version = (2, 7, 0, 0)
        self.reset(False)

    # resets the current state of the manager (removes current frames and thus all rigid bodies)
    def reset(self, notify=True):
        self.frame = None
        if notify:
            self.resetEvent(self)

    # takes raw, binary, packed natnet frame data
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
