# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb

def get_db_info():
    InitCursor()
    db_list=get_all_db()
    out_list = [("start",0)]
    for db_name in db_list:
        just_SelectDB(db_name)
        num = 0
        table_list = GetTableList(db_name)
        for table in table_list:
            num_all =  get_table_all_num(table)
            num += num_all
        print '%s:%d'%(db_name,num)
        out_list.append((db_name,num))
    print '------------------------------'
    out_list.sort(key=lambda x:x[1])
    for db,num in out_list:
        print '%s:%d'%(db,num)
    UnInitCursor()

if __name__ == '__main__':
    print 'start'
    get_db_info()     
