#!/usr/bin/env python
from pymocap.manager import Manager
from pymocap.color_terminal import ColorTerminal
from pymocap.readers.natnet_reader import NatnetReader
from pymocap.writers.osc_writer import OscWriter
from pymocap.gui.osc_forward_view import OscForwardView

import Tkinter as tk

class App(tk.Frame):
    def __init__(self, master=None):
        self.counter = 0
        self.manager = Manager()
        self.writer = OscWriter({'manager': self.manager})
        self.reader = NatnetReader(manager=self.manager, multicast='239.255.42.99', port=1511, host='0.0.0.0')

        tk.Frame.__init__(self, master, padx=10, pady=10)
        self.grid()
        self.master.title('PyMoCap Osc Forwarder v1.0')
        self.playView = OscForwardView(parent=self, reader=self.reader, writer=self.writer)
        self.update()

    def update(self):
        self.reader.update()
        # every 1 ms, should be enough
        self.after(1, self.update)


if __name__ == '__main__':
    app = App()
    app.mainloop()
