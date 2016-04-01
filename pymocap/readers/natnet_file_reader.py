from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event

from datetime import datetime
import struct

class FpsSync:
    def __init__(self, fps=120.0):
        self.fps = fps
        if not self.fps:
            self.fps = 120.0
        self._dtFrame = 1.0/self.fps
        self.reset()

    def start(self):
        self.reset()

    def reset(self):
        self.startTime = datetime.now()
        self.frameCount = 0
        self._nextFrameTime = 0

    def time(self):
        return (datetime.now()-self.startTime).total_seconds()

    def timeForNewFrame(self):
        return self.time() >= self._nextFrameTime

    def doFrame(self):
        self._nextFrameTime += self._dtFrame

    def nextFrame(self):
        if not self.timeForNewFrame():
            return False

        self.doFrame()
        return True

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
        self.manager = None

        self._natnet_version = (2, 7, 0, 0)

        # attributes
        self.file = None
        self._fpsSync = FpsSync(self.fps)
        self.running = False

        self.startEvent = Event()
        self.stopEvent = Event()
        self.updateEvent = Event()

    def destroy(self):
        self.stop()

    def update(self):
        if not self.isRunning():
            return

        if self.syncEnabled():
            if not self._fpsSync.nextFrame():
                return

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
        self.running = True
        self.startEvent(self)

    def stop(self):
        if self.file:
            self.file.close()
            self.file = None

        self.running = False
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
            self._fpsSync = FpsSync(self.fps)

        if manager:
            self.manager = manager

    # retuns a float value indicating the current playback time in seconds
    def getTime(self):
        return self._fpsSync.time()

    def isRunning(self):
        return self.running

    def syncEnabled(self):
        return self.fps != None

    def _rewind(self):
        # reset file handle
        self.file.seek(0)
        # reset timer
        self._fpsSync.reset()

    def _nextFrame(self):
        s = self._readFrameSize() # int: bytes
        t = self._readFrameTime() # float: seconds

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

    def _readFrameTime(self):
        # float of 4 bytes
        value = self.file.read(4)

        # end-of-file?
        if not value:
            # TODO; raise format error?
            return None

        # 'unpack' 4 binary bytes into float
        return struct.unpack('f', value)[0]
