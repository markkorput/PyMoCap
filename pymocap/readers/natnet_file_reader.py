# from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event
from pymocap.natnet_file import NatnetFile
from pymocap.fps_sync import FpsSync

class NatnetFileReader:
    def __init__(self, options = {}):
        self.options = {}
        self.natnet_file = NatnetFile()
        self.running = False
        self._fpsSync = FpsSync()
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

        if 'fps' in self.options: # fps syncing enabled?
            if not self._fpsSync.nextFrame():
                return

        # we're not waiting for loaded frame to go?
        if not self.waitingForFrameSync:
            # read next frame
            self.natnet_file.nextFrame()

        # frame-syncing enabled?
        if self.frameSyncEnabled():
            # this the first frame?
            if self.natnet_file.currentFrameIndex == 0:
                # use first frame's timestamp as time-shift correction
                # basically we're cutting all the delay from the start of
                # the recording until the first frame
                self.frameSyncTimeShift = self.natnet_file.currentFrameTime

            t = self.getTime() + self.frameSyncTimeShift

            # NatnetFile keeps timestamp of last read frame
            if t < self.natnet_file.currentFrameTime:
                # wait until it's time for this frame
                self.waitingForFrameSync = True
                # keep waiting
                return

            # time to continue
            self.waitingForFrameSync = False

        # if we got new frame data and a manager
        if 'manager' in self.options:
            self.options['manager'].processFrameData(self.natnet_file.currentFrame)

    def start(self):
        if self.running:
            self.stop()
        self.natnet_file.loopEvent += self._onLoop
        self.running = True
        self.waitingForFrameSync = False
        self.frameSyncTimeShift = 0.0
        self._fpsSync.reset()
        self.natnet_file.startReading()
        self.startEvent(self)

    def stop(self):
        self.natnet_file.stopReading()
        self.natnet_file.loopEvent -= self._onLoop
        self.running = False
        self.stopEvent(self)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        if 'loop' in options:
            self.natnet_file.setLoop(options['loop'])

        if 'path' in options:
            active = self.isRunning()
            if active:
                self.stop()

            self.natnet_file = NatnetFile(options['path'], loop=self.natnet_file.loop)

            if active:
                self.start()

        if 'fps' in options:
            self._fpsSync = FpsSync(options['fps'])

    # retuns a float value indicating the current playback time in seconds
    def getTime(self):
        return self._fpsSync.time()

    def isRunning(self):
        return self.running

    def frameSyncEnabled(self):
        # enabled by default (of sync option is not specified)
        return not 'sync' in self.options or self.options['sync']

    def _onLoop(self, natnetFile):
        self._fpsSync.reset()
