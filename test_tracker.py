"""
functional test module of tracker
first try GUI here
"""
import unittest
from tkinter import *
from tracker import MongoDB

class BasicFuntionTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testcase01(self):
        test_mgdb = MongoDB(None, 'tracker', 'simon')
        # check number of items in database
        test_doc_list = test_mgdb.find_all()
        self.assertEqual(len(test_doc_list), 13)

class MainFrame:

    def __init__(self, db_name: str, username: str):
        self.db = MongoDB(None, db_name, username)
        self.root = Tk()
        self.root.title(username)
        self.bt1 = Button(self.root)
        self.bt1.config(text='start', command=self.get_all)
        self.bt1.pack(side=RIGHT)
        self.lb1 = Label(self.root)
        self.lb1.config(text='Empty')
        self.lb1.pack()

    def get_all(self):
        tmp = 'count = %d' % len(self.db.find_all())
        self.lb1.config(text=tmp)

if __name__ == '__main__':
    # unittest.main()
    frame = MainFrame('tracker', 'simon')
    frame.root.mainloop()

# end of file
