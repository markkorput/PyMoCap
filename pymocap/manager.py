from pymocap.event import Event

class Manager:
    def __init__(self):
        self.setup()

    def setup(self):
        self.resetEvent = Event()
        self.frameEvent = Event()

        self._natnet_version = (2, 7, 0, 0)
        self.reset()

    def reset(self):
        self.frame = None
        self.resetEvent(self)
