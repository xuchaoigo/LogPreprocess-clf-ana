# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import os,time
from common import *
from Similarity import *
from multiprocessing import Process,Manager,Pool
import time


def _get_readable_time():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def insert_fullfeature(task_feature,feature_list,table_name):
    for i,item in enumerate(task_feature[table_name]):
        #print '###compare:'
        #print feature_list[0]
        #print item[0]
        if Similar_N_gram(feature_list[0],item[0]):
            #print 'similar'
            #task_feature[table_name][i][1] += int(feature_list[1])
            #task_feature[table_name][i][2] += int(feature_list[2])
            return
    #print 'not similar'
    featuretemp=[]
    featuretemp.append(feature_list[0])
    #featuretemp.append(int(feature_list[1])) 
    #featuretemp.append(int(feature_list[2]))
    task_feature[table_name].append(featuretemp)
    return
   
def insert_table(task_feature,line):
    print 'entering insert_table... line len=%d'%(len(line))
    pos = line.find(delimiter_table)
    if pos!=-1:
        table_name = line[:pos]
    else:
        print 'ERROR! invalid table.',line
        return
    print 'before line.split...'
    fullfeature_list = line[pos+len(delimiter_table):].split(delimiter_feature)
    print 'after line.split,list len=%d'%(len(fullfeature_list))
    if table_name in task_feature:
        #print 'merge to existing task_feature'
        #print '%d fullfeature to insert'%(len(fullfeature_list))
        count = 0
        for fullfeature in fullfeature_list:
            count += 1
            #if count%1000 == 0:
            print '[%s] %d' %(_get_readable_time(),count)
            feature_list = fullfeature.split(delimiter_item)
            if len(feature_list)!=1:
                print 'invalid feature:',feature_list
                continue
            insert_fullfeature(task_feature,feature_list,table_name) 
    else:
        if len(task_feature)==0:
            print 'insert to empty task_feature'
            task_feature[table_name]=[]
            #print '%d fullfeature to insert'%(len(fullfeature_list))
            for fullfeature in fullfeature_list:
                feature_list = fullfeature.split(delimiter_item)
                if len(feature_list)!=1:
                    print 'invalid feature:',feature_list
                    continue
                featuretemp=[]
                featuretemp.append(feature_list[0])
                #featuretemp.append(int(feature_list[1])) 
                #featuretemp.append(int(feature_list[2]))
                task_feature[table_name].append(featuretemp)
        else:
            print '\nERROR! inconsistent table name,check the splited tbl!'
            return

def write_file(task_feature,write_handle):
    for table_name in task_feature:
        write_handle.write('%s%s'%(table_name,delimiter_table))
        for i in range(0,len(task_feature[table_name])-1):
            #write_handle.write('%s%s%d%s%d%s'%(task_feature[table_name][i][0],delimiter_item,\
            #task_feature[table_name][i][1],delimiter_item,\
            #task_feature[table_name][i][2],delimiter_feature))
            write_handle.write('%s%s'%(task_feature[table_name][i][0],delimiter_feature) )
        #write_handle.write('%s%s%d%s%d\n'%(task_feature[table_name][-1][0],delimiter_item,\
        #task_feature[table_name][-1][1],delimiter_item,\
        #task_feature[table_name][-1][2]))
        write_handle.write('%s\n'%(task_feature[table_name][-1][0]))
    write_handle.close() 


def merge_tables(table_list_per_worker,task_id,table_dir):
    task_feature={}
    for table_file in table_list_per_worker:
        print table_file
        file_handle=open(table_file,'r')
        for line in file_handle:#should be 1 line only
            insert_table(task_feature,line.strip('\n'))
            pos = line.find(delimiter_table)
            if pos!=-1:
                table_name = line[:pos]
                if table_name=='1_8$1_8':
                    print 'omit 1_8$1_8,file=',table_file
                    return
            else:
                print 'ERROR!invalid table_file:',table_file
                return
        file_handle.close()
    
    #print 'task_feature=\n',task_feature
    write_name_handle=open('%s/tab%s_task%d.tbl'%(table_dir,table_name,task_id),'w')
    write_file(task_feature,write_name_handle)
    write_name_handle.close()   

    for files in table_list_per_worker:
        os.remove(files)  
  
def parallel_merge_tables(table_dir):
    file_list = []
    for root,dirs,files in os.walk(table_dir):
        for name in files:
            table_file = os.path.join(root,name)
            file_list.append(table_file)

    MERGE_NUM = 2
    file_num = len(file_list)
    task_num = int(file_num/MERGE_NUM)
    worker_list = []
    
    if task_num==0:#only 1 input file! rename and output 
        file_handle=open(table_file,'r')
        line = file_handle.readline()
        pos = line.find(delimiter_table)
        if pos!=-1:
            table_name = line[:pos]
        else:
            print 'ERROR!invalid table_file:',table_file
            return 'INVALID_TABLE_NAME'
        file_handle.close()
        new_name = '%s/tab%s_task%d.tbl'%(table_dir,table_name,0)
        os.rename(table_file,new_name)
        print 'output file is ',new_name
        return new_name

    #table_list_per_worker=file_lisg
    #merge_tables(table_list_per_worker,123,table_dir)
    task_id=0
    while task_num!=0:
        print '###start %d workers'%task_num
        pool = Pool(processes=10)   
        for i in xrange(0,task_num):
            table_list_per_worker=file_list[i*MERGE_NUM:(i+1)*MERGE_NUM]
            print 'table_list_per_worker=',table_list_per_worker
            task_id+=1
                        
            pool.apply_async(merge_tables, (table_list_per_worker,task_id,table_dir))
            """
            worker = Process(target=merge_tables,args=(table_list_per_worker,task_id,table_dir))
            worker.start()
            worker_list.append(worker)
            print 'Task %d invoked.'%task_id
            """

        pool.close()
        pool.join()
        print 'all worker exit.'
        
        file_list=[]
        for root,dirs,files in os.walk(table_dir):
            for name in files:
                table_file = os.path.join(root,name)
                file_list.append(table_file)
        file_num = len(file_list)
        task_num = int(file_num/MERGE_NUM)
        print 'cur file list=',file_list
        print '\n'

    #now we have the last survived file.
    print 'output file is ',file_list[0]
    return file_list[0]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' dir_to_handle '
        print 'dir_to_handle: must be global feature directory!'
        sys.exit()
    
    merge_table_dir = sys.argv[1]
    parallel_merge_tables(merge_table_dir);     

    print 'Main process exit.'
