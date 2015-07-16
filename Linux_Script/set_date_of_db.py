# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb
from datetime import *

def parse_date_str(dstr):
    #2014_02_03
    dlist = dstr.split('_')
    year = int(dlist[0])    
    month = int(dlist[1].lstrip('0'))    
    day = int(dlist[2].lstrip('0'))    
    return date(year,month,day)

def set_flag_already_run(db_name,start_date,end_date):
    StartDate = parse_date_str(start_date)
    EndDate = parse_date_str(end_date)

    InitCursor()
    SelectDB(db_name)

    table_list = GetTableList(db_name)
    NextDate = StartDate
    while NextDate <= EndDate:
        next_date = '%d_%02d_%02d'%(NextDate.year, NextDate.month, NextDate.day)
        if next_date in table_list:
            print 'SetHandled:',next_date
            SetHandled(next_date)

        NextDate += (date(2014, 1, 2)- date(2014, 1, 1))
    UnInitCursor()

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'Usage:'
        print '%s dbname start_date end_date'%sys.argv[0]
        print 'eg. python set_date_of_db.py Adware 2015_03_05 2015_03_11'
        exit(-1)
    dbname= sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]
    set_flag_already_run(dbname,start_date,end_date)     
    print 'Main process exit.'
