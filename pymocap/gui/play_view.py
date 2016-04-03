# from pymocap.color_terminal import ColorTerminal
# from pymocap.event import Event

import Tkinter as tk
import tkFileDialog

class PlayView:
    def __init__(self, parent, reader):
        self.parent = parent
        self.reader = reader
        self.setup()

    def setup(self):
        # container
        self.frame = tk.Frame(self.parent, padx=10, pady=10)

        # elements
        self.load_button = tk.Button(self.frame, text='Load File', command=self.onLoadButtonClicked)
        self.file_label = tk.Label(self.frame, text=self.reader.natnet_file.path)
        self.startstop_button = tk.Button(self.frame, text='Play', command=self.onStartStopButtonClicked)
        self.quitButton = tk.Button(self.frame, text='Quit', command=self.parent.quit)
        self.time_label = tk.Label(self.frame, text="time: 0s")

        # grid/positions
        self.frame.grid()
        self.file_label.grid(column=0, row=1, columnspan=3)
        self.time_label.grid(column=1, row=2)
        self.load_button.grid(column=0, row=3)
        self.startstop_button.grid(column=1, row=3)
        self.quitButton.grid(column=2, row=3)


        #
        # if self.reader:
        self.reader.startEvent += self.onStart
        self.reader.stopEvent += self.onStop

        self.updateStatus(self.reader)
        self.update()

    def destroy(self):
        self.frame.grid_forget()

    def onStartStopButtonClicked(self):
        if self.reader.isRunning():
            self.reader.stop()
        else:
            self.reader.start()

    def onLoadButtonClicked(self):
        file_path = tkFileDialog.askopenfile(**{})

        if file_path:
            self.reader.configure({'path':file_path.name})
            self.updateStatus(self.reader)

    def onStart(self, reader):
        self.updateStatus(reader)
        self.update()

    def onStop(self, reader):
        self.updateStatus(reader)
        self.time_label.configure(text='stopped')

    def updateStatus(self, reader):
        self.file_label.configure(text=reader.natnet_file.path)

        if reader.isRunning():
            self.startstop_button.configure(text='Stop')
        else:
            self.startstop_button.configure(text='Play')

    def update(self):
        if self.reader.isRunning():
            timeValue = '%.2f' % self.reader.getTime()
            self.time_label.configure(text='time: '+timeValue+'s')
            self.parent.after(100, self.update)
