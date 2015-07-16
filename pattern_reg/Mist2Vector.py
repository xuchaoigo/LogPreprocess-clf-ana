# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
from common import *
import time
from Similarity import *
from multiprocessing import Process,Manager

def FindLocation(g_feature_dict,vector):
    TabName=get_table_name(vector)
    if TabName in g_feature_dict:
        for Feature in g_feature_dict[TabName]:
            if Similar_N_gram(vector,Feature[1]):
                return Feature[0]
    return -1

def Mist2Vector(g_feature_dict,FetFile,task_id,SKHandle,debug_handle,supplyment_handle):
    ReadHandle=open(FetFile,'r')
    digit_dict={}
    total_num=0
    abandon_num=0
    reserve_num=0
    for line in ReadHandle:
        total_num += 1
        line=line.strip('\n')
        [feature,freq]=line.split(delimiter_count)
        index = FindLocation(g_feature_dict,feature)
        if index == -1:
            abandon_num += 1
            continue
        freq = int(freq)
        digit_dict[index]=int(freq)
    ReadHandle.close()

    if len(digit_dict)==0:
        return
    digit_list=[(k,digit_dict[k]) for k in sorted(digit_dict.keys())]
    if FetFile.find('White')>=0:
    	SKHandle.write('+1 ')
    elif FetFile.find('Black')>=0:
    	SKHandle.write('-1 ')
    else:
    	print 'Can not decide category'
    for item in digit_list:
        SKHandle.write('%s:%d '%(item[0],item[1]))       
    SKHandle.write('\n')

    reserve_num=total_num-abandon_num
    supplyment_handle.write('%s:%d,%d,%d\n'%(FetFile,total_num,reserve_num,abandon_num)) 
    

def process_file_list(file_list,task_id):
    g_feature_dict=FetchFeature()
    sk_handle =open('svm_train_%s.log'%task_id,'w')
    supplyment_handle=open('supplyment_%d.log'%task_id,'w')
    total_files_processed = 0
    debug_handle = open('debug_m2v_%d.txt'%task_id,'w')
    debug_handle.write('%d files to process...\n'%len(file_list))
    debug_handle.flush()
    for fet_file in file_list:
        total_files_processed += 1
        Mist2Vector(g_feature_dict,fet_file,task_id,sk_handle,debug_handle,supplyment_handle)
        if total_files_processed%1000 == 0:
            debug_handle.write('[%s]'%get_readable_time()+'num files processed is %d\n'%total_files_processed)
            debug_handle.write('len of dict=%d\n'%len(g_feature_dict))
            debug_handle.flush()
    
    debug_handle.write('all files processed\n')
    debug_handle.close()
    sk_handle.close()
    supplyment_handle.close()

def parallel_file_list(fet_dir,num_tasks):
    file_list = []
    for root,dirs,files in os.walk(fet_dir):
        for name in files:
            fet_file = os.path.join(root,name)
            file_list.append(fet_file)
    #process_file_list(file_list,1)
    num_files_per_task = int(len(file_list)/num_tasks)
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
        print 'dir_to_handle: must be parent directory of Log directory!'
        print 'num_tasks: number of processes to invoke'
        sys.exit()
    
    fet_dir = sys.argv[1]
    num_tasks = int(sys.argv[2])

    if num_tasks > 12 or num_tasks < 1:
        print 'invalid num_tasks: %d' %num_tasks
        sys.exit()

    if not 'Fet' in fet_dir:
        print 'invalid input directory:'+fet_dir
        sys.exit()

    parallel_file_list(fet_dir,num_tasks);     
    print 'Main process exit.'

    


