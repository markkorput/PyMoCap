from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event

from datetime import datetime
import struct, os


from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

import json

try:
    import OSC
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for OscWriter")
    import pymocap.dependencies.OSC as OSC

class NatnetFileWriter:
    def __init__(self, path=None, manager=None, autoStart=True):
        self.setup()
        self.configure(path=path, manager=manager)

        if autoStart == True:
            self.start()

    def __del__(self):
        self.destroy()

    def setup(self):
        self.manager = None
        self.running = False
        self.file = None
        default_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'natnet_'+datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.binary'))
        self.path = default_file_path

        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.frameCount = 0
        self.frameEvent = Event()

    def destroy(self):
        self.stop()

    def configure(self, path=None, manager=None):
        if path:
            self.path = path

            if self.running:
                self.stop()
                self.start()

        if manager:
            # unregister existing from current manager
            if self.manager:
                self.manager.frameDataEvent -= self._onFrameData
            # set new manager
            self.manager = manager
            # register with new manager
            if self.manager:
                self.manager.frameDataEvent += self._onFrameData

    def start(self):
        self.file = open(self.path, 'wb')
        self.running = True

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None

        self.running = False

    def _onFrameData(self, data, manager):
        if self.running:
            self._writeBinaryFrameToFile(data)
            self.frameCount += 1
            self.frameEvent(self)

    def _writeBinaryFrameToFile(self, frame_data):
        # format;
        # 4-bytes binary integer indicating the size of the (binary) frame data
        # followed by the binary frame data
        # followed by the next frame

        # write 4-byte binary integer; size of the frame data
        self.file.write(struct.pack('i', len(frame_data)))
        # write binary frame data
        self.file.write(frame_data)
