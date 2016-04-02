from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event
from pymocap.natnet_file import NatnetFile

from datetime import datetime

class FpsSync:
    def __init__(self, fps=None):
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
    def __init__(self, options = {}):
        self.manager = Manager()
        self.running = False
        self.configure(options)

        # events
        self.startEvent = Event()
        self.stopEvent = Event()
        self.updateEvent = Event()

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.start()

    def __del__(self):
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

    def configure(self, options):
        if not hasattr(self, 'options'):
            self.options = {}

        if not hasattr(self, 'natnet_file'):
            self.natnet_file = NatnetFile()

        previous_options = self.options
        self.options = dict(previous_options.items() + options.items())

        if 'loop' in options:
            self.natnet_file.setLoop(options['loop'])

        if 'path' in options:
            self.natnet_file = NatnetFile(options['path'], loop=self.natnet_file.loop)

            if self.isRunning():
                # restart
                self.stop()
                self.start()

        if 'fps' in options:
            self._fpsSync = FpsSync(options['fps'])

        if 'manager' in options:
            self.manager = options['manager']

    # retuns a float value indicating the current playback time in seconds
    def getTime(self):
        return self._fpsSync.time()

    def isRunning(self):
        return self.running

    def syncEnabled(self):
        # enabled if fps option was set explicitly
        return True if 'fps' in self.options else False
