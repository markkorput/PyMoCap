from pymocap.gui.natnet_view import NatnetView
from pymocap.gui.recorder_view import RecorderView

import Tkinter as tk

class RecordView:
    def __init__(self, parent, reader, writer):
        self.parent = parent
        self.reader = reader
        self.writer = writer
        self.setup()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.frame.grid_forget()

    def setup(self):
        # container
        self.frame = tk.Frame(self.parent, padx=10, pady=10)
        self.frame.grid()
        self.natnet_view = NatnetView(parent=self.frame, reader=self.reader)
        self.recorder_view = RecorderView(parent=self.frame, writer=self.writer)

        self.natnet_view.frame.grid(row=0, column=0)
        self.recorder_view.frame.grid(row=1, column=0)
