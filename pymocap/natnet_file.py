from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

import struct, os
from datetime import datetime

class NatnetFile:
    def __init__(self, path=None, loop=True):
        self.path = path
        self.loop = loop

        # file handles
        self.read_file = None
        self.write_file = None

        # last read frame info
        self.currentFrame = None
        self.currentFrameTime = None
        self.currentFrameIndex = -1

        # events
        self.loopEvent = Event()

    def __del__(self):
        self.stop()

    def startReading(self):
        self.stopReading()

        try:
            if not self.path:
                self.path = 'walk-198frames.binary.recording'

            self.read_file = open(self.path, 'rb')
            ColorTerminal().success("NatnetFile opened: %s" % self.path)
        except:
            ColorTerminal().fail("NatnetFile couldn't be opened: %s" % self.path)
            self.read_file = None

    def stopReading(self):
        if self.read_file:
            self.read_file.close()
            self.read_file = None
            ColorTerminal().blue('NatnetFile closed')

    def startWriting(self):
        self.stopWriting()
        try:
            if not self.path:
                self.path = '/tmp/natnet_'+datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.binary'

            self.write_file = open(self.path, 'wb')
            ColorTerminal().success("NatnetFile opened for writing: %s" % self.path)
        except:
            ColorTerminal().fail("NatnetFile couldn't be opened for writing: %s" % self.path)
            self.write_file = None

    def stopWriting(self):
        if self.write_file:
            self.write_file.close()
            self.write_file = None
            ColorTerminal().blue('NatnetFile closed')

    def stop(self):
        self.stopReading()
        self.stopWriting()

    def setLoop(self, loop):
        self.loop = loop

    def nextFrame(self):
        bytecount = self._readFrameSize() # int: bytes
        self.currentFrameTime = self._readFrameTime() # float: seconds

        if bytecount == None or self.currentFrameTime == None:
            return None

        self.currentFrame = self.read_file.read(bytecount)
        self.currentFrameIndex += 1

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
            self.currentFrame = None
            self.currentFrameTime = None
            self.currentFrameIndex = -1
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

    def writeFrame(self, frameData, time=0.0):
        # frame format;
        # 4-bytes binary integer indicating the size of the (binary) frame data
        # 4-byte binary float indicating timestamp (in seconds) of the frame
        # followed by the binary frame data
        # [next frame]

        # write 4-byte binary integer; size of the frame data
        self.write_file.write(struct.pack('i', len(frameData)))
        # write 4-byte binary float; timestamp in seconds
        self.write_file.write(struct.pack('f', time))
        # write binary frame data
        self.write_file.write(frameData)
