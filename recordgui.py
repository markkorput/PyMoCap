#!/usr/bin/env python
from pymocap.manager import Manager
from pymocap.color_terminal import ColorTerminal
from pymocap.readers.natnet_reader import NatnetReader
from pymocap.writers.natnet_file_writer import NatnetFileWriter
from pymocap.gui.record_view import RecordView

import Tkinter as tk

class App(tk.Frame):
    def __init__(self, master=None):
        self.counter = 0
        self.manager = Manager()
        self.writer = NatnetFileWriter({'manager': self.manager, 'autoStart': False})
        self.reader = NatnetReader(manager=self.manager, multicast='239.255.42.99', port=1511, host='0.0.0.0')

        tk.Frame.__init__(self, master, padx=10, pady=10)
        self.grid()
        self.master.title('PyMoCap Recorder v1.0')
        self.playView = RecordView(parent=self, reader=self.reader, writer=self.writer)
        self.update()

    def update(self):
        self.reader.update()
        # every 1 ms, should be enough
        self.after(1, self.update)


if __name__ == '__main__':
    app = App()
    app.mainloop()
