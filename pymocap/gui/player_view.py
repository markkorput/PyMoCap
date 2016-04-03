from pymocap.gui.play_view import PlayView
from pymocap.gui.osc_view import OscView

import Tkinter as tk

class PlayerView:
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
        self.play_view = PlayView(parent=self.frame, reader=self.reader)
        self.osc_view = OscView(parent=self.frame, writer=self.writer)

        self.play_view.frame.grid(row=0, column=0, sticky=tk.S)
        self.osc_view.frame.grid(row=0, column=1, sticky=tk.S)
