"""
Module description:
using mongoDB to track daily activities
minimal via app:
1. command line as mymoney project
2. -i insert new entry to database
3. -x export entry from database (_id export by default)
4. -u update entry status
5. that's it, not summary page etc for now, reuse as much code as possible, but copy-paste ok for now
"""
# import sys
import re
import openpyxl
# from openpyxl.styles import Alignment
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import WriteError
from bson import ObjectId
from typing import List
# from datetime import timedelta
from datetime import datetime

def connect_mongodb(url: str = None) -> MongoClient:
    """ connect to default cloud mongo db, return client """
    if url is None:
        cli = MongoClient("mongodb://simon:68paU6OlBbT1FsbA@cluster0-shard-00-00-rbqhf.mongodb.net:27017,cluster0-shard-00-01-rbqhf.mongodb.net:27017,cluster0-shard-00-02-rbqhf.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
    else:
        cli = MongoClient(url)
    return cli

def connect_database(cli: MongoClient, name: str) -> Database:
    """ connect datebase @p name in the client, create if not exist """
    return cli.get_database(name)

def close_mongodb(cli: MongoClient) -> None:
    cli.close()

def query_id_exist(collection: Collection, _id: ObjectId) -> bool:
    cursor = collection.find_one({'_id': _id})
    return cursor is not None

def query_delete(collection: Collection, _id: ObjectId) -> None:
    collection.delete_one({'_id': _id})

def query_insert_one(collection: Collection, doc: dict, flag_auto_id) -> bool:
    if flag_auto_id:
        new_doc = {}
        for (key, value) in zip(doc.keys(), doc.values()):
            if key != '_id':
                new_doc[key] = value
    else:
        new_doc = doc
    try:
        collection.insert_one(new_doc)
    except WriteError as error:
        print('Insertion failed with', error.details)
        return False
    return True

def str_to_int(string: str) -> int:
    try:
        rest = int(string)
    except ValueError:
        rest = None
    return rest

def get_keys(row: tuple) -> dict:
    rest = {}
    for item in row:    # type: Cell
        if item.value is not None and str(item.value) != '':
            rest[item.value] = item.col_idx-1   # col_index start at 1
    return rest

def get_format_doc_from_row(keys: dict, row: tuple, critical_keys: List = None) -> dict:
    """ return a document with _id field, and there is a date key
    only 5 possible data type: None, str, date, int, IdObject string  """
    doc = {}
    for (key, value) in zip(keys.keys(), keys.values()):
        doc[key] = row[value].value
    # _id field is either None or 24 char string
    if len(str(doc['_id'])) == 24:
        doc['_id'] = ObjectId(doc['_id'])
    else:
        doc['_id'] = None
    # format date field
    datestr = re.sub('[ -]', '', str(doc['date']))
    if isinstance(doc['date'], datetime):
        pass
    elif doc['date'] is None or datestr == '':
        doc['date'] = datetime.today()
    elif datestr.isdigit() and len(datestr) == 8:
        doc['date'] = datetime(int(datestr) // 10000, (int(datestr) // 100) % 100, int(datestr) % 100)
    else:
        doc['date'] = None
    # check valid entry against critical key list
    if critical_keys is not None and critical_keys != []:
        for key in critical_keys:
            if doc[key] is not None:
                return doc
        doc = None
    return doc

def get_valid_doc_from_xlsx(filename: str, critical_keys: List = None) -> List:
    wb = openpyxl.load_workbook(filename)
    ws = wb.worksheets[0]         # type: Worksheet
    keys = {}
    doc_list = []
    for i, row in enumerate(ws):
        # first row is key string
        if i == 0:
            keys = get_keys(row)
            continue
        # rest row are data entries, format doc before insertion
        doc = get_format_doc_from_row(keys, row, critical_keys)
        if doc is not None:
            doc_list.append(doc)
    wb.close()
    return doc_list

def write_doc_to_xlsx(filename: str, doc_list: List[dict]):
    if len(doc_list) == 0:
        return
    wb = openpyxl.Workbook()
    ws = wb.worksheets[0]         # type: Worksheet
    # first row is key, write key
    row = 1
    for j, key in enumerate(doc_list[0].keys()):
        ws.cell(row, j+1).value = key
    row += 1
    # write content
    for doc in doc_list:
        for j, (key, value) in enumerate(zip(doc.keys(), doc.values())):
            if key == '_id':
                value = str(value)
            elif key == 'date':
                value = str(value)[:10]
            ws.cell(row, j+1).value = value
        row += 1
    wb.save(filename)
    wb.close()

def db_insert(db_name: str, collection_name: str, doc_list: List[dict], flag_auto_id=True) -> int:
    client = connect_mongodb()
    db = connect_database(client, db_name)
    collection = db.get_collection(collection_name)
    insert_count = 0
    for doc in doc_list:
        if query_insert_one(collection, doc, flag_auto_id):
            insert_count += 1
    return insert_count

def db_find_all(db_name: str, collection_name: str) -> List[dict]:
    client = connect_mongodb()
    db = connect_database(client, db_name)
    collection = db.get_collection(collection_name)
    cursor = collection.find()
    return list(cursor)

def db_update(db_name: str, collection_name: str, doc_list: List[dict]) -> int:
    """ find and update using _id by delete and re-insert, TODO: change later to modify """
    client = connect_mongodb()
    db = connect_database(client, db_name)
    collection = db.get_collection(collection_name)
    update_count = 0
    for doc in doc_list:
        if query_id_exist(collection, doc['_id']):
            query_delete(collection, doc['_id'])
            if query_insert_one(collection, doc, True):
                update_count += 1
        else:
            print(doc['_id'], 'not found, skip')
    return update_count

# end of module


# start top level
if __name__ == '__main__':
    # plan_list = get_valid_doc_from_xlsx('plan.xlsx')
    # print('Insertion count ==> ', db_insert('tracker', 'simon', plan_list))
    # write_doc_to_xlsx('output.xlsx', db_find_all('tracker', 'simon'))

    update_list = get_valid_doc_from_xlsx('update.xlsx', ['_id'])
    print('Update count ==> ', db_update('tracker', 'simon', update_list))

# end of top level

# end of file
