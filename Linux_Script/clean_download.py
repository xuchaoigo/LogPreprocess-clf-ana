# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb

def clean_download(db_name):
    InitCursor()
    SelectDB(db_name)
    table_list = GetTableList(db_name)
    clean_str = ''
    for table in table_list:
        d_and_r,not_run,not_download,num_all =  check_table_status(table)
        #delete_all_used_md5(table)
        #delete_table(table)
        print '%s: d_and_r=%d not_run=%d not_download=%d all=%d'%(table, d_and_r ,not_run, not_download, num_all)
        if d_and_r == num_all and num_all!=0:
            clean_str+=table
            clean_str+=" "

    print '%s '%clean_str
    UnInitCursor()

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print '%s dbname'%sys.argv[0]
        exit(-1)
    dbname= sys.argv[1]
    clean_download(dbname)     
    print 'Main process exit.'
