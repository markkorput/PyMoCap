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
