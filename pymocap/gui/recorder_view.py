import Tkinter as tk
from subprocess import call

class RecordingView:
    def __init__(self, path, frameCount=None, parent=None):
        self.path = path
        self.frameCount = frameCount
        self.parent = parent
        self.setup()
        self.update()

    def setup(self):
        # create container
        self.frame = tk.Frame(self.parent, padx=3, pady=3)
        self.frame.grid()

        # create elements
        self.path_label = tk.Label(self.frame, text=self.text())
        self.find_button = tk.Button(self.frame, text='find', command=self.onFind)

        # position elements
        self.path_label.grid(column=0, row=0)
        self.find_button.grid(column=1, row=0)

    def configure(self, path=None, frameCount=None):
        if frameCount:
            self.frameCount = frameCount

        self.update()

    def update(self):
        self.path_label.configure(text=self.text())

    def destroy(self):
        self.frame.grid_forget()

    def onFind(self):
        try:
            # 'open -R' command; 'Reveal in Finder'
            call(["open", '-R', self.path])
        except:
            print('Cannot perform "Reveal in Finder" command. Is this even OSX?')
            # self.find_button.forget()

    def text(self):
        if self.frameCount:
            return '{0:s} {1:04d}'.format(self.path, self.frameCount)
        else:
            return '{0:s}'.format(self.path)

class RecorderView:
    def __init__(self, parent, writer):
        self.parent = parent
        self.writer = writer
        self.recording_views = []
        self.setup()


    def __del__(self):
        self.destroy()

    def destroy(self):
        self.frame.grid_forget()

    def setup(self):
        # container
        self.frame = tk.Frame(self.parent, padx=10, pady=10)

        # create elements
        self.record_button = tk.Button(self.frame, text='Start recording', command=self.onRecordButton)
        self.status_label = tk.Label(self.frame, text='')
        # position elements
        self.record_button.grid(column=0, row=0)
        self.status_label.grid(column=0, row=1)

        self.updateStatus(self.writer)
        self.writer.startEvent += self.onStart
        self.writer.stopEvent += self.onStop

        if self.writer.running:
            self.onStart(self.writer)

    def update(self):
        if self.writer.running:
            self.updateStatus(self.writer)
            self.parent.after(1, self.update)

    def onRecordButton(self):
        if self.writer.running:
            self.writer.stop()
        else:
            # generate new default (timestamped) json filename
            self.writer.configure({'path': None})
            # start recording
            self.writer.start()

    def onStart(self, writer):
        # add recording line
        self.recording_views.append(RecordingView(path=writer.natnet_file.path, frameCount=0, parent=self.frame))
        # change text of start/stop button
        self.record_button.configure(text='Stop recording')
        # update status label
        self.update()

    def onStop(self, writer):
        # update recording line
        self.recording_views[-1].configure(frameCount=writer.frameCount)
        # change start/button text
        self.record_button.configure(text='Start recording')
        # update status label
        self.updateStatus(writer)

    def updateStatus(self, writer):
        if writer.running:
            self.status_label.configure(text='Frames Recorded: {0:04d}'.format(writer.frameCount))
        else:
            self.status_label.configure(text='')
