from pymocap.color_terminal import ColorTerminal
from pymocap.manager import Manager
from pymocap.event import Event
from pymocap.natnet_file import NatnetFile

from datetime import datetime

class NatnetFileWriter:
    def __init__(self, options = {}):
        self.running = False
        self.natnet_file = NatnetFile()

        self.frameCount = 0
        self.frameEvent = Event()

        self.options = {}
        self.configure(options)

        # events
        self.startEvent = Event()
        self.stopEvent = Event()

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.start()

    def __del__(self):
        self.stop()

    def configure(self, options):
        previous_options = self.options
        self.options = dict(previous_options.items() + options.items())

        if 'path' in options:
            self.natnet_file = NatnetFile(path=options['path'])

            if self.running:
                self.stop()
                self.start()

        if 'manager' in options:
            # unregister from previous manager
            if 'manager' in previous_options and previous_options['manager']:
                self.previous_options['manager'].frameDataEvent -= self._onFrameData

            # register with new manager
            if options['manager']:
                options['manager'].frameDataEvent += self._onFrameData

    def start(self):
        self.natnet_file.startWriting()
        self.running = True
        self.startTime = datetime.now()
        self.startEvent(self)

    def stop(self):
        self.natnet_file.stopWriting()
        self.running = False
        self.stopEvent(self)

    def _time(self):
        return (datetime.now() - self.startTime).total_seconds()

    def _onFrameData(self, data, manager):
        if self.running:
            self.natnet_file.writeFrame(data, self._time())
            self.frameCount += 1
            self.frameEvent(self)
