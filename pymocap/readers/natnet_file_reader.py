from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event

from datetime import datetime
import struct

class NatnetFileReader:
    def __init__(self, path, loop=True, manager=None, fps=120, autoStart=True):
        self.setup()
        self.configure(path=path, fps=fps, loop=loop, manager=manager)

        if autoStart == True:
            self.start()

    def __del__(self):
        self.destroy()

    def setup(self):
        self.path = None
        self.loop = False
        self.fps = None
        self._timePerFrame = None
        self._nextFrameTime = None
        self.manager = None

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
        if not self.isRunning():
            return

        if self.syncEnabled():
            # get current playback time
            t = self.getTime()
            if t < self._nextFrameTime:
                # abort, not time for next frame yet
                return

            # update time for frame after the current frame
            self._nextFrameTime += self._timePerFrame

        data = self._nextFrame()

        if data and self.manager:
            self.manager.processFrameData(data)

    def start(self):
        self.stop()

        if not self.path:
            ColorTerminal().fail("NatnetFileReader - no file specified")
            return

        try:
            self.file = open(self.path, 'rb')
            ColorTerminal().success("Opened file %s" % self.path)
        except:
            ColorTerminal().fail("Could not open file %s" % self.path)

        self._rewind()
        self.startEvent(self)

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None

        self.startTime = None
        self.stopEvent(self)

    def configure(self, path=None, fps=None, loop=None, manager=None):
        if path:
            self.path = path

            if self.isRunning():
                # restart
                self.stop()
                self.start()

        if loop:
            self.loop = loop

        if fps:
            self.fps = int(fps)
            self._timePerFrame = 1.0/self.fps

        if manager:
            self.manager = manager

    # retuns a float value indicating the current playback time in seconds
    def getTime(self):
        if self.startTime is None:
            return 0
        return (datetime.now()-self.startTime).total_seconds()

    def isRunning(self):
        return self.startTime != None

    def syncEnabled(self):
        return self.fps != None

    def _rewind(self):
        # reset file handle
        self.file.seek(0)
        # reset timer
        self.startTime = datetime.now()
        # first frame immediately (if syncing)
        self._nextFrameTime = 0

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
            if not self.loop:
                return None

            self._rewind()
            # try again
            return self._readFrameSize()

        # 'unpack' 4 binary bytes into integer
        return struct.unpack('i', value)[0]
