from pymocap.color_terminal import ColorTerminal
from pymocap.event import Event

import struct, os
from datetime import datetime

class NatnetFile:
    def __init__(self, path=None, loop=True):
        self.path = path
        self.loop = loop

        if not self.path:
            self.path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'natnet_'+datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.binary'))

        # file handles
        self.read_file = None
        self.write_file = None

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

    def startWriting(self):
        self.stopWriting()
        try:
            self.write_file = open(self.path, 'wb')
            ColorTerminal().success("NatnetFile opened file for writing: %s" % self.path)
        except:
            ColorTerminal().fail("NatnetFile couldn't open file for writing: %s" % self.path)
            self.write_file = None

    def stopWriting(self):
        if self.write_file:
            self.write_file.close()
            self.write_file = None

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
