#!/usr/bin/env python
from pymocap.manager import Manager
from pymocap.color_terminal import ColorTerminal
from pymocap.readers.natnet_reader import NatnetReader
from pymocap.writers.natnet_file_writer import NatnetFileWriter

import sys

# config
file_path = None if len(sys.argv) < 2 else sys.argv[1]
natnet_host = '0.0.0.0' if len(sys.argv) < 3 else sys.argv[2]
natnet_multicast = '239.255.42.99' if len(sys.argv) < 4 else sys.argv[3]
natnet_port = 1511 if len(sys.argv) < 5 else sys.argv[4]

def onFrameRecorded(natnet_writer):
    ColorTerminal().blue('Recorded {0} frames'.format(str(natnet_writer.frameCount)))

# initialize
manager = Manager()
writer = NatnetFileWriter({'path':file_path, 'manager':manager})
reader = NatnetReader(manager=manager, host=natnet_host, multicast=natnet_multicast, port=natnet_port)

writer.frameEvent += onFrameRecorded

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
