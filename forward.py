#!/usr/bin/env python
from pymocap.manager import Manager
from pymocap.readers.natnet_reader import NatnetReader
from pymocap.writers.osc_writer import OscWriter

import sys

# config
natnet_host = '0.0.0.0' if len(sys.argv) < 2 else sys.argv[1]
natnet_multicast = '239.255.42.99' if len(sys.argv) < 3 else sys.argv[2]
natnet_port = 1511 if len(sys.argv) < 4 else sys.argv[3]
osc_host = '127.0.0.1' if len(sys.argv) < 5 else sys.argv[4]
osc_port = 8080 if len(sys.argv) < 6 else sys.argv[5]

# initialize
manager = Manager()
writer = OscWriter({'host':osc_host, 'port':osc_port, 'manager':manager})
reader = NatnetReader(manager=manager, host=natnet_host, multicast=natnet_multicast, port=natnet_port)

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
