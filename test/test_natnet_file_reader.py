import test_helper
from pymocap.manager import Manager
from pymocap.readers.natnet_file_reader import NatnetFileReader

import unittest
import os

class TestNatnetFileReader(unittest.TestCase):

    def setUp(self):
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures', 'binary_natnet_frames'))
        self.manager = Manager()
        self.reader = NatnetFileReader({'path': self.file_path, 'manager': self.manager})

    def test_initial_frame(self):
        # before
        self.assertIsNone(self.manager.frame)
        # perform
        self.reader.update()
        # after
        self.assertIsNotNone(self.manager.frame)

if __name__ == '__main__':
    unittest.main()
