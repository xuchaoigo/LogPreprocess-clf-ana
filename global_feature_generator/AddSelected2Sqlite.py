# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import sqlite3
import traceback

def add_selected_2Sqlite(feature_file, db_name):
    cx = sqlite3.connect("./%s"%db_name)
    cu=cx.cursor()
    Feature_Index=1
    table_count = 0
    read_handle = open(feature_file,'r')
    lines = read_handle.readlines()
    for line in lines:
        try:
            line = line.replace('\'','\'\'')
            table_name = get_table_name(line)
            create_tab_cmd='create table if not exists t%s(Feature_Index integer,Target varchar(256))'%table_name
            #print 'create cmd=',create_tab_cmd
            cu.execute(create_tab_cmd)
            cx.commit()
            [target,black_count,white_count] = line.split(delimiter_item)
            black_count = int(black_count)
            white_count = int(white_count)
            addcmd="insert into t%s(Feature_Index,Target) values(%d,'%s')"%(table_name,Feature_Index,target)
            #print 'addcmd=',addcmd
            cu.execute(addcmd)
            cx.commit()
            if Feature_Index%500==0:
                 print '[%s]features inserted:%d'%(get_readable_time(),Feature_Index)
            Feature_Index+=1
        except Exception,e:
            print 'AddItemToDb failed,fet=%s'%line
            print e
            print traceback.format_exc()
            #keep consistence of Feature_Index
            Feature_Index+=1
            create_tab_cmd='create table if not exists missing_feature(Feature_Index integer,Target varchar(256))'
            cu.execute(create_tab_cmd)
            cx.commit()
            addcmd="insert into missing_feature(Feature_Index,Target) values(%d,'null')"%(table_name,Feature_Index)
            cu.execute(addcmd)
            cx.commit()
            
    read_handle.close()
    cx.commit()
    cu.close()
    cx.close()
    print 'add_selected_2Sqlite finisned. total index=',Feature_Index-1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'selected_feature_file db_name'
        sys.exit()
    
    print 'ADD selected feature_file to Sqlite..'
    feature_file_name = sys.argv[1]
    db_name = sys.argv[2]
    add_selected_2Sqlite(feature_file_name,db_name)     
