from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event
from pymocap.natnet_file import NatnetFile

from datetime import datetime

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
    def __init__(self, path=None, loop=True, manager=None, fps=120, autoStart=True):
        self.natnet_file = NatnetFile(path=path, loop=loop)
        self.fps = None
        self.manager = None

        self._natnet_version = (2, 7, 0, 0)

        # attributes
        self._fpsSync = FpsSync(self.fps)
        self.running = False

        # events
        self.startEvent = Event()
        self.stopEvent = Event()
        self.updateEvent = Event()

        self.configure(fps=fps, manager=manager)

        if autoStart == True:
            self.start()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.stop()

    def update(self):
        if not self.isRunning():
            return

        if self.syncEnabled():
            if not self._fpsSync.nextFrame():
                return

        data = self.natnet_file.nextFrame()

        if data and self.manager:
            self.manager.processFrameData(data)

    def start(self):
        self.natnet_file.startReading()
        self.running = True
        self.startEvent(self)

    def stop(self):
        self.natnet_file.stop()
        self.running = False
        self.stopEvent(self)

    def configure(self, path=None, fps=None, loop=None, manager=None):
        if loop:
            self.natnet_file.setLoop(loop)

        if path:
            self.natnet_file = NatnetFile(path, loop=self.natnet_file.loop)

            if self.isRunning():
                # restart
                self.stop()
                self.start()

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
