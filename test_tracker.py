"""
functional test module of tracker
first try GUI here
"""
import unittest
from datetime import datetime, timedelta
from tkinter import *
from tracker import MongoDB, XlsxFile
from typing import List

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
        title_string = '%s %s' % (username, str(self.today_start)[:10])
        self.root.title(title_string)
        # set top summary field
        self.showlist = self.db.find_between_values('date', self.today_start, self.today_end)
        self.lb1 = Label(self.root)
        self.lb1.config(text='task count = %d' % len(self.showlist))
        self.lb1.pack(side=TOP)
        left = Frame(self.root)
        left.pack(side=LEFT, fill=Y)
        right = Frame(self.root)
        right.pack(side=RIGHT, fill=Y)
        left_panel = Frame(left)
        left_panel.pack(anchor=NW)
        # set right side panel of main frame
        right_panel = Frame(right)
        right_panel.pack(anchor=NE)
        # entry of year-month-day field
        self.var_date = {'year': IntVar(),
                         'month': IntVar(),
                         'day': IntVar()}
        self.var_date['year'].set(self.today_start.year)
        self.var_date['month'].set(self.today_start.month)
        self.var_date['day'].set(self.today_start.day)
        for field in ['year', 'month', 'day']:
            row = Frame(right_panel)
            row.pack(side=TOP)
            Label(row, width=5, text=field).pack(side=LEFT)
            Entry(row, width=5, textvariable=self.var_date[field]).pack(side=RIGHT, expand=NO)
        # import button
        self.bt_import = Button(right_panel)
        self.bt_import.config(text='import', command=self.import_with_xlsx)
        self.bt_import.pack(side=TOP, fill=X)
        # update button
        self.bt_update = Button(right_panel)
        self.bt_update.config(text='update', command=self.update_with_xlsx)
        self.bt_update.pack(side=TOP, fill=X)
        # export button
        self.bt_export = Button(right_panel)
        self.bt_export.config(text='export', command=self.export_with_xlsx)
        self.bt_export.pack(side=TOP, fill=X)
        # export all button
        self.bt_export_all = Button(right_panel)
        self.bt_export.config(text='export all', command=self.export_all_with_xlsx)
        self.bt_export.pack(side=TOP, fill=X)
        # set left panel
        self.var_left_panel = []        # type: List[dict]
        self._display_left_panel(left_panel)

    def _display_left_panel(self, parent):
        """
        all field should be variables, or maybe not
        each 2 lines are one entry, radio button, date, points, task, and update
        status state: active, delay, dismiss, done; date is ten
        """
        for item in self.showlist:
            var = {}
            # make a frame
            row = Frame(parent)
            row.pack(side=TOP, fill=X)
            # make radio button
            var['radio'] = StringVar()
            var['radio'].set(item['status'])
            for string in ['active', 'delay', 'dismiss', 'done']:
                Radiobutton(row, text=string, variable=var['radio'], value=string).pack(side=LEFT)
            # make date label
            Label(row, width=14, text=str(item['date'])[:10]).pack(side=LEFT)
            # make points label
            var['points'] = IntVar()
            var['points'].set(item['points'])
            Entry(row, width=4, textvariable=var['points']).pack(side=LEFT)
            # make task entry
            var['task'] = StringVar()
            var['task'].set(item['task'])
            Entry(row, width=48, textvariable=var['task']).pack(side=LEFT)
            # make update entry
            var['update'] = StringVar()
            var['update'].set('' if item['update'] is None else item['update'])
            Entry(row, width=48, textvariable=var['update']).pack(side=LEFT)
            self.var_left_panel.append(var)

    def import_with_xlsx(self):
        xlsx = XlsxFile('input.xlsx', False)
        tmplist = xlsx.get_valid_doc_from_xlsx(['points'])
        tmpstr = 'insert count = %d\n' % self.db.insert_all(tmplist, True)
        self.lb1.config(text=tmpstr)
        # self.lb2.config(text=self.get_today_all_string())

    def update_with_xlsx(self):
        xlsx = XlsxFile('update.xlsx', False)
        tmplist = xlsx.get_valid_doc_from_xlsx(['_id'])
        update_count = self.db.update_all(tmplist)
        tmpstr = 'update count = %d\n' % update_count
        self.lb1.config(text=tmpstr)
        # self.lb2.config(text=self.get_today_all_string())

    def export_with_xlsx(self):
        xlsx = XlsxFile('output.xlsx', True)
        tmplist = self.db.find_between_values('date', self.today_start, self.today_end)
        xlsx.write_doc_to_xlsx(tmplist)
        tmpstr = 'export %d\n' % len(tmplist)
        self.lb1.config(text=tmpstr)
        # self.lb2.config(text=self.get_today_all_string())

    def export_all_with_xlsx(self):
        xlsx = XlsxFile('output.xlsx', True)
        tmplist = self.db.find_between_values('date', None, None)
        xlsx.write_doc_to_xlsx(tmplist)
        tmpstr = 'export %d\n' % len(tmplist)
        self.lb1.config(text=tmpstr)
        # self.lb2.config(text=self.get_today_all_string())

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
