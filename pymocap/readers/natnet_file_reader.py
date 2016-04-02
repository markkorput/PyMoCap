from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event
from pymocap.natnet_file import NatnetFile
from pymocap.fps_sync import FpsSync

class NatnetFileReader:
    def __init__(self, options = {}):
        self.options = {}
        self.natnet_file = NatnetFile()
        self.manager = Manager()
        self.running = False
        self.configure(options)

        # events
        self.startEvent = Event()
        self.stopEvent = Event()

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
        self.natnet_file.stopReading()
        self.running = False
        self.stopEvent(self)

    def configure(self, options):
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
