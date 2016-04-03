import Tkinter as tk

class OscView:
    def __init__(self, parent, writer, dummy_line=False):
        self.parent = parent
        self.writer = writer
        self.dummy_line = dummy_line
        self.setup()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.frame.grid_forget()

    def setup(self):
        # container
        self.frame = tk.Frame(self.parent, padx=10, pady=10)

        self.host_label = tk.Label(self.frame, text="OSC Host")
        self.host_entry = tk.Entry(self.frame, width=25)
        self.port_label = tk.Label(self.frame, text="Port")
        self.port_entry = tk.Entry(self.frame, width=5)
        self.status_label = tk.Label(self.frame, text='')
        if self.dummy_line:
            self.dummy_label = tk.Label(self.frame, text='')
        self.connect_button = tk.Button(self.frame, text='(re-)connect', command=self.onConnectButton)
        self.disconnect_button = tk.Button(self.frame, text='disconnect', command=self.onDisconnectButton)

        # position elements
        self.host_label.grid(column=0, row=0, sticky=tk.E)
        self.host_entry.grid(column=1, row=0, sticky=tk.W)
        self.port_label.grid(column=0, row=1, sticky=tk.E)
        self.port_entry.grid(column=1, row=1, sticky=tk.W)
        self.status_label.grid(column=0, row=2, columnspan=3, padx=10, pady=10)
        if self.dummy_line:
            self.dummy_label.grid(column=0, row=3, columnspan=3, padx=10, pady=10)
        self.connect_button.grid(column=0, row=4, sticky=tk.E)
        self.disconnect_button.grid(column=1, row=4, sticky=tk.W)

        # initialize
        self.host_entry.insert(0, self.writer.host())
        self.port_entry.insert(0, self.writer.port())

        self.writer.connectEvent += self.updateStatus
        self.writer.disconnectEvent += self.updateStatus
        self.updateStatus(self.writer)

    def onConnectButton(self):
        self.writer.stop()
        self.writer.configure({'host':self.host_entry.get(), 'port':self.port_entry.get()})
        self.writer.start()

    def onDisconnectButton(self):
        self.writer.stop()

    def updateStatus(self, osc_writer):
        if osc_writer.connected == True:
            txt = 'Connected to '+str(osc_writer.host())+'@'+str(osc_writer.port())
        else:
            txt = 'Disconnected'

        self.status_label.config(text=txt)
