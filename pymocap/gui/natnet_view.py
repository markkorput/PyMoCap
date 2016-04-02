import Tkinter as tk

class NatnetView:
    def __init__(self, parent, reader):
        self.parent = parent
        self.reader = reader
        self.setup()

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.frame.grid_forget()

    def setup(self):
        # container
        self.frame = tk.Frame(self.parent, padx=10, pady=10)

        # form elements
        self.host_label = tk.Label(self.frame, text="Natnet Host IP")
        self.host_entry = tk.Entry(self.frame, width=25)
        self.multicast_label = tk.Label(self.frame, text="Multicast IP")
        self.multicast_entry = tk.Entry(self.frame, width=25)
        self.port_label = tk.Label(self.frame, text="NatNet Port")
        self.port_entry = tk.Entry(self.frame, width=5)
        # status element
        self.connection_label = tk.Label(self.frame, text='')
        self.error_label = tk.Label(self.frame, text='')
        # buttons
        self.connect_button = tk.Button(self.frame, text='(re-)connect', command=self.onConnectButton)
        self.disconnect_button = tk.Button(self.frame, text='disconnect', command=self.onDisconnectButton)

        # grid/positions
        self.frame.grid()
        # self.file_label.grid(column=0, row=0, columnspan=3)
        # self.time_label.grid(column=1, row=1)
        # self.load_button.grid(column=0, row=2)
        # self.startstop_button.grid(column=1, row=2)
        # self.quitButton.grid(column=2, row=2)
        self.host_label.grid(column=0, row=0, sticky=tk.E)
        self.host_entry.grid(column=1, row=0, sticky=tk.W)
        self.multicast_label.grid(column=0, row=1, sticky=tk.E)
        self.multicast_entry.grid(column=1, row=1, sticky=tk.W)
        self.port_label.grid(column=0, row=2, sticky=tk.E)
        self.port_entry.grid(column=1, row=2, sticky=tk.W)
        self.connection_label.grid(column=0, row=3, columnspan=3, padx=10, pady=10)
        self.error_label.grid(column=0, row=4, columnspan=3, padx=10, pady=10)
        self.connect_button.grid(column=0, row=5, sticky=tk.E)
        self.disconnect_button.grid(column=1, row=5, sticky=tk.W)

        # initialize
        self.host_entry.insert(0, self.reader.host)
        if self.reader.multicast:
            self.multicast_entry.insert(0, str(self.reader.multicast))
        self.port_entry.insert(0, str(self.reader.port))

        self.reader.connectEvent += self.updateConnectionStatus
        self.reader.connectionLostEvent += self.updateConnectionStatus
        self.reader.connectionStatusUpdateEvent += self.updateConnectionStatus

        self.updateConnectionStatus(self.reader)

    def onConnectButton(self):
        self.reader.stop()
        multicast = self.multicast_entry.get()
        if multicast == '':
            multicast = None
        self.reader.configure(host=self.host_entry.get(), port=self.port_entry.get(), multicast=multicast)
        self.reader.start()

    def onDisconnectButton(self):
        self.reader.stop()

    def updateConnectionStatus(self, reader):
        if reader.connected == False:
            self.connection_label.config(text="Disconnected")
            self.error_label.config(text='')
            return

        self.connection_label.config(text=self.connectionInfo(reader))
        err = reader.connection_error if reader.connection_error else ''
        self.error_label.config(text=err)

    def connectionInfo(self, reader):
        if reader.multicast:
            return 'Connected to '+str(reader.host)+'@'+str(reader.port)+' ('+reader.multicast+')'

        return 'Connected to '+str(reader.host)+'@'+str(reader.port)
