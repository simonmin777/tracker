"""
functional test module of tracker
first try GUI here
"""
import unittest
from tracker import *


class BasicFuntionTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testcase01(self):
        # check number of items in database
        doc_list = db_find_all('tracker', 'simon')
        self.assertEqual(len(doc_list), 13)


if __name__ == '__main__':
    unittest.main()
