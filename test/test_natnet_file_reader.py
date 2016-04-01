import test_helper
import unittest

from pymocap.manager import Manager

class TestNatnetFileReader(unittest.TestCase):

    def setUp(self):
        self.manager = Manager()

    def test_initial_frame(self):
        self.assertEqual(self.manager.frame, None)

if __name__ == '__main__':
    unittest.main()
