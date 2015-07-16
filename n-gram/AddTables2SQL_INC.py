# -*- coding: cp936 -*-
import os
import sys
import string
import time
import common
from common import *
import MySQLdb
import traceback
from multiprocessing import Process,Manager 

def add_fet_list_2SQL(fet_list,task,db_server,db_name):
    mysql_conn = MySQLdb.connect(host=db_server,user='root',passwd='123456',port=3306)
    mysql_cursor = mysql_conn.cursor()
    mysql_conn.select_db(db_name)
    cnt = 0
    print 'task %d: start to insert %d fets..'%(task, len(fet_list))
    for fet in fet_list:
        try:
            cnt+=1
            table_name = fet[0]
            Feature_Index = fet[1]
            target = fet[2]
            black_count = int(fet[3])
            white_count = int(fet[4])
            create_tab_cmd='create table if not exists %s(Feature_Index Int,Target varchar(256),black_count Int, white_count Int) character set = utf8'%table_name
            mysql_cursor.execute(create_tab_cmd)
            addcmd='insert ignore into %s(Feature_Index,Target,black_count,white_count) values(%d,"%s",%d,%d)'%(table_name,Feature_Index,target,black_count,white_count)
            mysql_cursor.execute(addcmd)
            if cnt%1000==0:
                 print 'task %d: features inserted=%d, index=%d, %s'%(task, cnt, Feature_Index, get_readable_time())
        except Exception,e:
            print 'AddItemToDb failed,fet=%s'%fullfeature 
            print e
            print traceback.format_exc()               
    mysql_cursor.close()
    mysql_conn.commit()
    mysql_conn.close()
    print 'task %d:add_fet_list_2SQL finisned.'%task


def add_incremental_tables_2SQL(table_dir,db_server,db_name, start_index, num_tasks):
    Feature_Index=start_index
    table_count = 0
    feature_list=[]
    for root,dirs,files in os.walk(table_dir):
        for name in files:
            table_count +=1 
            if table_count%100 ==0:
                print 'Saving No. %d table: %s'%(table_count,name)
            table_file = os.path.join(root,name)
            read_handle = open(table_file,'r')
            line = read_handle.readline()
            [table_name,feature_set]=line.split(delimiter_table)
            fullfeature_list = feature_set.split(delimiter_feature)
            for fullfeature in fullfeature_list:
                #without-weight version doesn't need to do delimiter_item
                if fullfeature.count('"'):
                        continue
                try:
                #change tabs to list to parallel
                    [target,black_count,white_count] = fullfeature.split(delimiter_item)
                    black_count = int(black_count)
                    white_count = int(white_count)
                    FeatureTemp=[]
                    FeatureTemp.append(table_name)
                    FeatureTemp.append(Feature_Index)
                    FeatureTemp.append(target)
                    FeatureTemp.append(black_count)
                    FeatureTemp.append(white_count)
                    feature_list.append(FeatureTemp)   

                    if Feature_Index%5000==0:
                         print '[%s]features inserted:%d'%(get_readable_time(),Feature_Index)
                    Feature_Index+=1
                except Exception,e:
                    print 'AddItemToList failed,fet=%s'%fullfeature 
                    print e
            read_handle.close()
    print 'add to List finisned.'
    
    print '%d talbes in feature_list'%table_count
    print '%d features in feature_list'%len(feature_list)
    num_tabs_per_task = int(len(feature_list)/num_tasks)
    worker_list = []
    object_manager = Manager()
    
    for task in range(0,num_tasks):
        current_fet_list = []
        if task < num_tasks - 1:
            current_fet_list = object_manager.list(feature_list[task*num_tabs_per_task:(task+1)*num_tabs_per_task])
        else:
            current_fet_list = object_manager.list(feature_list[task*num_tabs_per_task:])

        worker = Process(target=add_fet_list_2SQL,args=(current_fet_list,task,db_server,db_name))
        worker.start()
        worker_list.append(worker)
        print 'Task %d invoked.'%task

    for worker in worker_list:
        worker.join()
        print 'one worker exit.'

    print '%d talbes in feature_list'%table_count
    print '%d features in feature_list'%len(feature_list)
    print 'add_incremental_tables_2SQL finish.'

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print 'Usage:'
        print sys.argv[0],'feature_table_dir database_server database_name task_num'
        print 'NOTE: database_name is the target db to ADD incremental fet, NOT a new db!'
        sys.exit()
    
    feature_table_dir = sys.argv[1]
    db_server = sys.argv[2]
    db_name = sys.argv[3]
    task_num = int(sys.argv[4])
    print 'start check fet_num in',db_name,'...'
    start_index = common.get_fet_num_of_gft(db_server,db_name)

    print 'start_index=',start_index
    #sys.exit(0)
    print 'start add incremental tables to SQL..'
    add_incremental_tables_2SQL(feature_table_dir,db_server,db_name,start_index+1, task_num)     
    print 'Main process exit.'
