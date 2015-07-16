# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb

def clean_MYSQL():
    InitCursor()
    db_name = 'Trojan'
    SelectDB(db_name)
    table_list = GetTableList(db_name)
    for table in table_list:
        #delete_all_used_md5(table)
        delete_table_if_empty(table)
    UnInitCursor()

if __name__ == '__main__':
    print 'start'
    clean_MYSQL()     
    print 'Main process exit.'
