"""
functional test module of tracker
first try GUI here
"""
import unittest
from datetime import datetime, timedelta
from tkinter import *
from tracker import MongoDB, XlsxFile
from typing import List
from bson import ObjectId

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
        # set left panel
        self.var_left_panel = []        # type: List[dict]
        self._display_left_panel(left_panel)
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
        # query button
        bt_query = Button(right_panel, padx=10, pady=10)
        bt_query.config(text='query', command=self.query_on_date)
        bt_query.pack(side=TOP, fill=X)
        # update button
        bt_update = Button(right_panel, padx=10, pady=10)
        bt_update.config(text='update', command=self.update_on_date)
        bt_update.pack(side=TOP, fill=X)
        # import button
        self.bt_import_xlsx = Button(right_panel)
        self.bt_import_xlsx.config(text='import xlsx', command=self.import_with_xlsx)
        self.bt_import_xlsx.pack(side=TOP, fill=X)
        # update button
        self.bt_update_xlsx = Button(right_panel)
        self.bt_update_xlsx.config(text='update xlsx', command=self.update_with_xlsx)
        self.bt_update_xlsx.pack(side=TOP, fill=X)
        # export button
        self.bt_export_xlsx = Button(right_panel)
        self.bt_export_xlsx.config(text='export xlsx', command=self.export_with_xlsx)
        self.bt_export_xlsx.pack(side=TOP, fill=X)
        # export all button
        self.bt_export_all = Button(right_panel)
        self.bt_export_all.config(text='export all', command=self.export_all_with_xlsx)
        self.bt_export_all.pack(side=TOP, fill=X)

    def _postfix(self):
        postfix = [{'_id': None, 'status': ' ', 'date': None, 'points': 0, 'task': ' ', 'update': ' '}]
        if len(self.showlist) < 20:
            self.showlist += postfix * (20-len(self.showlist))

    def _assign_var_left_panel(self):
        self._postfix()
        i = 0
        for item in self.showlist:
            self.var_left_panel[i]['radio'].set(item['status'])
            date_string = ' ' if item['date'] is None else str(item['date'])[:10]
            self.var_left_panel[i]['date'].set(date_string)
            self.var_left_panel[i]['points'].set(item['points'])
            self.var_left_panel[i]['task'].set(item['task'])
            self.var_left_panel[i]['update'].set(item['update'] if item['update'] is not None else ' ')
            i += 1

    def _read_var_left_panel(self):
        rslt = []
        for item in self.var_left_panel:        # type: dict
            # an entry is valid only if both points and task are set
            if item['points'].get() and item['task'].get().strip():
                entry = {}
                # read radio button
                tmp = item['radio'].get()
                if tmp.strip():
                    entry['status'] = tmp
                else:
                    entry['status'] = 'active'
                # read date field
                datestr = re.sub('[ -]', '', item['date'].get())
                if datestr:
                    entry['date'] = datetime(int(datestr) // 10000, (int(datestr) // 100) % 100, int(datestr) % 100)
                else:
                    entry['date'] = datetime(self.var_date['year'].get(), self.var_date['month'].get(), self.var_date['day'].get())
                # read points (int), task, and update
                entry['points'] = item['points'].get()
                entry['task'] = item['task'].get()
                entry['update'] = item['update'].get()
                rslt.append(entry)
        return rslt

    def _display_left_panel(self, parent):
        self._postfix()
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
            var['date'] = StringVar()
            date_string = ' ' if item['date'] is None else str(item['date'])[:10]
            var['date'].set(date_string)
            Label(row, width=14, textvariable=var['date']).pack(side=LEFT)
            # make points label
            var['points'] = IntVar()
            var['points'].set(item['points'])
            Entry(row, width=4, textvariable=var['points']).pack(side=LEFT)
            # make task entry
            var['task'] = StringVar()
            var['task'].set(item['task'])
            Entry(row, width=50, textvariable=var['task']).pack(side=LEFT)
            # make update entry
            var['update'] = StringVar()
            var['update'].set('' if item['update'] is None else item['update'])
            Entry(row, width=50, textvariable=var['update']).pack(side=LEFT)
            self.var_left_panel.append(var)

    def query_on_date(self):
        self.today_start = datetime(self.var_date['year'].get(), self.var_date['month'].get(), self.var_date['day'].get())
        self.today_end = self.today_start + timedelta(days=1)
        self.showlist = self.db.find_between_values('date', self.today_start, self.today_end)
        query_count = self.db.update_all(self.showlist)
        tmpstr = 'query count = %d\n' % query_count
        self.lb1.config(text=tmpstr)
        self._assign_var_left_panel()

    def update_on_date(self):
        new_showlist = self._read_var_left_panel()
        update_list = []
        insert_list = []
        for old_item, new_item in zip(self.showlist, new_showlist):
            if isinstance(old_item['_id'], ObjectId):
                new_item['_id'] = old_item['_id']
                update_list.append(new_item)
            else:
                insert_list.append(new_item)
        tmpstr = 'update count = %d insert count = %d\n' % (len(update_list), len(insert_list))
        self.lb1.config(text=tmpstr)
        self.db.update_all(update_list)
        self.db.insert_all(insert_list, True)

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
