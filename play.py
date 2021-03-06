#!/usr/bin/env python

from pymocap.manager import Manager
from pymocap.color_terminal import ColorTerminal
from pymocap.readers.natnet_file_reader import NatnetFileReader
from pymocap.writers.osc_writer import OscWriter
from pymocap.writers.natnet_file_writer import NatnetFileWriter

import sys, os

default_file_path = 'walk-198frames.binary.recording'

counter = 0

def onFrame(frame, manager):
    global counter
    counter += 1
    ColorTerminal().blue('Frame count: {0}, frameno: {1}'.format(str(counter), str(frame.frameno)))

# config
file_path = default_file_path if len(sys.argv) < 2 else sys.argv[1]
osc_host = '127.0.0.1' if len(sys.argv) < 3 else sys.argv[2]
osc_port = 8080 if len(sys.argv) < 4 else sys.argv[3]

# initialize all modules
manager = Manager()
manager.frameEvent += onFrame
writer = OscWriter({'host':osc_host, 'port':osc_port, 'manager':manager})
reader = NatnetFileReader({'path': file_path, 'manager': manager, 'autoStart': False})
# uncomment the following line to re-record all frames into a new file
# writer = NatnetFileWriter({'manager': manager})

reader.start()

# execution loop
while True:
    try:
        # when the reader receives new data, it will process it and feed it into the manager
        # the manager will trigger some events when it gets new data
        # the writer will respond to the manager's events and output information
        reader.update()
    except KeyboardInterrupt:
        break

reader.stop()
writer.stop()
