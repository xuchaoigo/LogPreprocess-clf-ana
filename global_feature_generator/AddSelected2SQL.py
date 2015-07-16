# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb
import traceback

def add_selected_2SQL(feature_file, db_name):
    mysql_conn = MySQLdb.connect(host='nj02-sw-kvmserver01.nj02',user='root',passwd='123456',port=3306)
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute('create database if not exists %s'%db_name)
    mysql_conn.select_db(db_name)
    Feature_Index=1
    table_count = 0
    read_handle = open(feature_file,'r')
    lines = read_handle.readlines()
    for line in lines:
        try:
            [old_index,target,black_count,white_count] = line.split(delimiter_item)
            black_count = int(black_count)
            white_count = int(white_count)
            table_name = get_table_name(target)
            create_tab_cmd='create table if not exists %s(Feature_Index Int,Target varchar(256)) character set = utf8'%table_name
            #print 'create cmd=',create_tab_cmd
            mysql_cursor.execute(create_tab_cmd)
            #addcmd='insert ignore into %s(Feature_Index,Target,black_count,white_count) values(%d,"%s",%d,%d)'%(table_name,Feature_Index,target,black_count,white_count)
            addcmd='insert ignore into %s(Feature_Index,Target) values(%d,"%s")'%(table_name,Feature_Index,target)
            #print 'addcmd=',addcmd
            mysql_cursor.execute(addcmd)
            if Feature_Index%500==0:
                 print '[%s]features inserted:%d'%(get_readable_time(),Feature_Index)
            Feature_Index+=1
        except Exception,e:
            print 'fet=%s'%line
            print e
            print traceback.format_exc()               
    read_handle.close()
    
    mysql_cursor.close()
    mysql_conn.commit()
    mysql_conn.close()
    print 'add_tables_2SQL finisned. total index=',Feature_Index-1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'selected_feature_file db_name'
        sys.exit()
    
    print 'start add selected feature_file to SQL..'
    feature_file_name = sys.argv[1]
    db_name = sys.argv[2]
    add_selected_2SQL(feature_file_name,db_name)     
    print 'Main process exit.'
