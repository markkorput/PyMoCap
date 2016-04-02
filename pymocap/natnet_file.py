from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

import struct

class NatnetFile:
    def __init__(self, path=None, loop=True):
        self.path = path
        self.loop = loop

        # file handles
        self.read_file = None
        # self.write_file = None

        # last read frame info
        self.currentFrame = None
        self.currentTime = None

        # events
        self.loopEvent = Event()

    def startReading(self):
        self.stopReading()

        try:
            self.read_file = open(self.path, 'rb')
            ColorTerminal().success("NatnetFile opened file: %s" % self.path)
        except:
            ColorTerminal().fail("NatnetFile Couldn't open file: %s" % self.path)
            self.read_file = None

    def stopReading(self):
        if self.read_file:
            self.read_file.close()
            self.read_file = None

    def stop(self):
        self.stopReading()

    def setLoop(self, loop):
        self.loop = loop

    def nextFrame(self):
        bytecount = self._readFrameSize() # int: bytes
        self.currentTime = self._readFrameTime() # float: seconds

        if bytecount == None or self.currentTime == None:
            return None

        self.currentFrame = self.read_file.read(bytecount)
        return self.currentFrame

    def _readFrameSize(self):
        # int is 4 bytes
        value = self.read_file.read(4)

        # end-of-file?
        if not value:
            if not self.loop:
                return None

            # reset file handle
            self.read_file.seek(0)
            # notify
            self.loopEvent(self)
            # try again
            return self._readFrameSize()

        # 'unpack' 4 binary bytes into integer
        return struct.unpack('i', value)[0]

    def _readFrameTime(self):
        # float of 4 bytes
        value = self.read_file.read(4)

        # end-of-file?
        if not value:
            # TODO; raise format error?
            return None

        # 'unpack' 4 binary bytes into float
        return struct.unpack('f', value)[0]
