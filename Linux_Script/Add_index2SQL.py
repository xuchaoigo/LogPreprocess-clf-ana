# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb

def add_index_2SQL():
    InitCursor()
    SelectDB('Trojan')
    table_list = GetTableList('Trojan')
    for table in table_list:
        AddIndexToTable_test(table)
        print '%s done!'%table

    UnInitCursor()

if __name__ == '__main__':
    print 'start add index to DB'
    add_index_2SQL()     
    print 'Main process exit.'
