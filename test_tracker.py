"""
functional test module of tracker
first try GUI here
"""
import unittest
from datetime import datetime, timedelta
from tkinter import *
from tracker import MongoDB, XlsxFile
# from typing import List

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
        self.today_start = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        self.today_end = self.today_start + timedelta(days=1)
        self.root.title('%s %s' % (username, str(self.today_start)[:10]))
        # import button
        self.bt_import = Button(self.root)
        self.bt_import.config(text='import', command=self.import_with_xlsx)
        self.bt_import.pack(side=RIGHT)
        # update button
        self.bt_update = Button(self.root)
        self.bt_update.config(text='update', command=self.update_with_xlsx)
        self.bt_update.pack(side=RIGHT)
        # export button
        self.bt_export = Button(self.root)
        self.bt_export.config(text='export', command=self.export_with_xlsx)
        self.bt_export.pack(side=RIGHT)
        # status field one and two, TODO: change later
        self.lb1 = Label(self.root)
        self.lb1.config(text='Empty')
        self.lb1.pack()
        self.lb2 = Label(self.root)
        self.lb2.config(text=self.get_today_all_string())
        self.lb2.pack()

    def import_with_xlsx(self):
        xlsx = XlsxFile('input.xlsx', False)
        tmplist = xlsx.get_valid_doc_from_xlsx(['points'])
        tmpstr = 'insert count = %d\n' % self.db.insert_all(tmplist, True)
        self.lb1.config(text=tmpstr)
        self.lb2.config(text=self.get_today_all_string())

    def update_with_xlsx(self):
        xlsx = XlsxFile('update.xlsx', False)
        tmplist = xlsx.get_valid_doc_from_xlsx(['_id'])
        update_count = self.db.update_all(tmplist)
        tmpstr = 'update count = %d\n' % update_count
        self.lb1.config(text=tmpstr)
        self.lb2.config(text=self.get_today_all_string())

    def export_with_xlsx(self):
        xlsx = XlsxFile('output.xlsx', True)
        tmpstr = 'export \n'
        xlsx.write_doc_to_xlsx(self.db.find_between_values('date', self.today_start, self.today_end))
        self.lb1.config(text=tmpstr)
        self.lb2.config(text=self.get_today_all_string())

    def get_today_all_string(self) -> str:
        tmplist = self.db.find_between_values('date', self.today_start, self.today_end)
        rslt = ''
        for item in tmplist:
            tmp = "%s %s %s %d points %s [%s]\n" % (str(item['_id']), item['status'], str(item['date'])[:10],
                                                 item['points'], item['task'], item['update'])
            rslt += tmp
        return rslt


if __name__ == '__main__':
    # unittest.main()
    frame = MainFrame('tracker', 'simon')
    frame.root.mainloop()

# end of file
