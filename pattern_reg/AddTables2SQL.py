# -*- coding: cp936 -*-
import os
import sys
import string
import time
from common import *
import MySQLdb
import traceback

def add_tables_2SQL(table_dir,db_server,db_name):
    mysql_conn = MySQLdb.connect(host=db_server,user='root',passwd='123456',port=3306)
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute('create database if not exists %s'%db_name)
    mysql_conn.select_db(db_name)
    Feature_Index=1
    counter = 0
    for root,dirs,files in os.walk(table_dir):
        for name in files:
            table_file = os.path.join(root,name)
            read_handle = open(table_file,'r')
            line = read_handle.readline()
            [table_name,feature_set]=line.split(delimiter_table)
            fullfeature_list = feature_set.split(delimiter_feature)
            counter += 1
            print 'processing %d feature table,total features = %d'%(counter,len(fullfeature_list))
            for fullfeature in fullfeature_list:
                #without-weight version doesn't need to do delimiter_item
                if fullfeature.count('"'):
                        continue
                try:
                    create_tab_cmd='create table if not exists %s(Feature_Index Int,Target varchar(256)) character set = utf8'%table_name
                    mysql_cursor.execute(create_tab_cmd)
                    addcmd='insert ignore into %s(Feature_Index,Target) values(%d,"%s")'%(table_name,Feature_Index,fullfeature)
                    mysql_cursor.execute(addcmd)
                    if Feature_Index%500==0:
                         print '[%s]features inserted:%d'%(get_readable_time(),Feature_Index)
                    Feature_Index+=1
                except Exception,e:
                    print 'AddItemToDb failed,fet=%s'%fullfeature 
                    print e
                    print traceback.format_exc()               
            read_handle.close()
    mysql_cursor.close()
    mysql_conn.commit()
    mysql_conn.close()
    print 'add_tables_2SQL finisned.'

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],'feature_table_dir database_server database_name'
        sys.exit()
    
    print 'start add tables to SQL..'
    feature_table_dir = sys.argv[1]
    db_server = sys.argv[2]
    db_name = sys.argv[3]
    add_tables_2SQL(feature_table_dir,db_server,db_name)     
    print 'Main process exit.'
