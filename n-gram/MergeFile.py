# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import os,time
from common import *
from Similarity import *
from multiprocessing import Process,Manager
import time

def insert_feature(task_feature,line):
    [feature,num]=line.split(delimiter_count)
    table_name=get_table_name(feature) 
    if table_name in task_feature:
        similar_bool= False
        for item in task_feature[table_name]:
            if Similar_N_gram(feature,item):
                similar_bool = True
                break
        if similar_bool == False:
            task_feature[table_name].append(feature)
    else:
        task_feature[table_name]=[]
        task_feature[table_name].append(feature) 
     
def process_file(task_feature,fet_file):
    file_handle=open(fet_file,'r')
    for line in file_handle: 
        insert_feature(task_feature,line.strip('\n'))
    file_handle.close()

def write_file(task_feature,feature_file):
    write_handle=open(feature_file,'w')
    for table_name in task_feature:
        write_handle.write('%s%s'%(table_name,delimiter_table))
        for i in range(0,len(task_feature[table_name])-1):
            write_handle.write('%s%s'%(task_feature[table_name][i],delimiter_feature)) 
        write_handle.write('%s\n'%(task_feature[table_name][-1]))
    write_handle.close() 

def process_file_list(file_list,task_id):
    total_files_processed = 0
    task_feature={}
    debug_handle = open('debug_mergefile_%d.txt'%task_id,'w')
    debug_handle.write('processsing %d fils...\n'%len(file_list))
    debug_handle.flush()
    for fet_file in file_list:
        total_files_processed += 1
        process_file(task_feature,fet_file)
        if total_files_processed%2000 == 0:
            debug_handle.write('[%s]'%get_readable_time()+'num files processed is %d\n'%total_files_processed)
            debug_handle.flush()
    
    debug_handle.write('all files processed\n')
    debug_handle.close()

    feature_file='./global_feature_%d.txt'%task_id 
    write_file(task_feature,feature_file)
    
    write_name_handle=open('./feature_name_file.txt','a')
    write_name_handle.write('%s\n'%feature_file)
    write_name_handle.close()

def parallel_file_list(fet_dir,num_tasks):
    #get all files under sample_dir
    file_list = []
    for root,dirs,files in os.walk(fet_dir):
        for name in files:
            fet_file = os.path.join(root,name)
            file_list.append(fet_file)

    num_files_per_task = int(len(file_list)/num_tasks)
    print type(num_files_per_task)
    worker_list = []
    object_manager = Manager(); 
    for task in range(0,num_tasks):
        current_file_list = []
        if task < num_tasks - 1:
            current_file_list = object_manager.list(file_list[task*num_files_per_task:(task+1)*num_files_per_task])
        else:
            current_file_list = object_manager.list(file_list[task*num_files_per_task:])
        
        worker = Process(target=process_file_list,args=(current_file_list,task))
        worker.start()
        worker_list.append(worker)
        print 'Task %d invoked.'%task    
    
    for worker in worker_list:
        worker.join()
        print 'one worker exit.'



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],' dir_to_handle num_tasks'
        print 'dir_to_handle: must be Fet directory!'
        print 'num_tasks: number of processes to invoke'
        sys.exit()
    
    fet_dir = sys.argv[1]
    num_tasks = int(sys.argv[2])

    if num_tasks >12 or num_tasks < 1:
        print 'invalid num_tasks: %d' %num_tasks
        sys.exit()

    if not 'Fet' in fet_dir:
        print 'invalid input directory:'+fet_dir
        sys.exit()

    parallel_file_list(fet_dir,num_tasks);     

    print 'Main process exit.'
