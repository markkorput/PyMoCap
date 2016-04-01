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

    def processFrameData(self, data):
        self.frameDataEvent(data, self)

        packet = rx.unpack(data, version=self._natnet_version)

        if type(packet) is rx.SenderData:
            self._natnet_version = packet.natnet_version

        self.addFrame(packet)

    def addFrame(self, frame):
        self.frame = frame
        self.frameEvent(frame, self)
