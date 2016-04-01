from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event

from datetime import datetime
import struct

class NatnetFileReader:
    def __init__(self, path, loop=True, manager=None, autoStart=True):
        # params
        self.path = path
        self.loop = loop
        # self.sync = sync
        self.manager = manager

        self.setup()

        if autoStart == True:
            self.start()

    def __del__(self):
        self.destroy()

    def setup(self):
        self._natnet_version = (2, 7, 0, 0)

        # attributes
        self.file = None
        self.startTime = None

        self.startEvent = Event()
        self.stopEvent = Event()
        self.updateEvent = Event()

    def destroy(self):
        self.stop()

    def update(self):
        data = self._nextFrame()

        if data:
            self.manager.processFrameData(data)

    def start(self):
        self.stop()

        try:
            self.file = open(self.path, 'rb')
            ColorTerminal().success("Opened file %s" % self.path)
        except:
            ColorTerminal().fail("Could not open file %s" % self.path)

        self.startTime = datetime.now()
        self.startEvent(self)

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None

        self.startTime = None
        self.stopEvent(self)

    def configure(self, path=None, loop=None):
        if path: self.path = path
        if loop: self.loop = loop

        if path and self.isRunning():
            self.stop()
            self.start()

    def getTime(self):
        if self.startTime is None:
            return 0
        return (datetime.now()-self.startTime).total_seconds()

    def isRunning(self):
        return self.startTime != None

    def _nextFrame(self):
        s = self._readFrameSize()

        if s == None:
            return None

        # print('size', s)
        return self.file.read(s)

    def _readFrameSize(self):
        # int is 4 bytes
        value = self.file.read(4)

        # end-of-file?
        if not value:
            if not self.loop: return None
            # print('loop')
            # rewind
            self.file.seek(0)
            # reset timer
            self.startTime = datetime.now()
            # try again
            return self._readFrameSize()

        # 'unpack' 4 binary bytes into integer
        return struct.unpack('i', value)[0]

    # todo; create raw_binary_writer?
    def _writeBinaryFrameToFile(self, frame_data):
        if not hasattr(self, 'raw_binary_file'):
            self.raw_binary_file = open('data/raw_binary_natnet', 'wb')

        # # size of next block
        # self.file.write(str(len(frame_data))+'bytes')
        self.raw_binary_file.write(struct.pack('i', len(frame_data)))
        # # block
        self.raw_binary_file.write(frame_data)
