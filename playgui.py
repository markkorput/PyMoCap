#!/usr/bin/env python
from pymocap.manager import Manager
from pymocap.color_terminal import ColorTerminal
from pymocap.readers.natnet_file_reader import NatnetFileReader
from pymocap.writers.osc_writer import OscWriter
from pymocap.gui.play_view import PlayView

import Tkinter as tk
import os

class App(tk.Frame):
    def __init__(self, master=None):
        self.counter = 0
        self.manager = Manager()
        self.writer = OscWriter({'manager': self.manager})
        defaultfile = 'walk-198frames.binary.recording'
        self.reader = NatnetFileReader({'path': defaultfile, 'manager': self.manager, 'autoStart': False})

        tk.Frame.__init__(self, master, padx=10, pady=10)
        self.grid()

        self.master.title('PyMoCap Player v1.0')
        self.playView = PlayView(parent=self, reader=self.reader, writer=self.writer)
        # self.lift()
        self.reader.start()
        self.update()

    def update(self):
        self.reader.update()
        # every 1 ms, should be enough
        self.after(1, self.update)


if __name__ == '__main__':
    app = App()
    app.mainloop()
