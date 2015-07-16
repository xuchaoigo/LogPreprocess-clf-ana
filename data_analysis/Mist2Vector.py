# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import common
import time
from Similarity import *
from multiprocessing import Process,Manager

def FindLocation(g_feature_dict,vector):
    TabName=get_table_name(vector)
    behavior_list = TabName.split(delimiter_table_name)
    if len(behavior_list)==2:
        if behavior_list[0][:3]=='1_8' and behavior_list[1][:3]=='1_8':
            return -1
    if TabName in g_feature_dict:
        for Feature in g_feature_dict[TabName]:
            if Similar_N_gram(vector,Feature[1]):
                return Feature[0]
    return -1

def Mist2Vector(g_feature_dict,fet_file,vector_handle,is_white):
    ReadHandle=open(fet_file,'r')
    digit_dict={}
    total_num=0
    #abandon_num=0
    reserve_num=0
    for line in ReadHandle:
        total_num += 1
        line=line.strip()
        [feature,freq]=line.split(delimiter_count)
        index = FindLocation(g_feature_dict,feature)
        if index == -1:
            #abandon_num += 1
            continue
        reserve_num += 1
        freq = int(freq)
        digit_dict[index]=int(freq)

    if len(digit_dict)==0:
        return
    md5=fet_file[fet_file.rfind('/')+1:fet_file.rfind('.')]
    vector_handle.write('%s %d/%d '%(md5,reserve_num,total_num))
    digit_list=[(k,digit_dict[k]) for k in sorted(digit_dict.keys())]
    if is_white:
    	vector_handle.write('+1 ')
    else:
    	vector_handle.write('-1 ')

    for item in digit_list:
        vector_handle.write('%s:%d '%(item[0],item[1]))       
    vector_handle.write('\n')
    

def process_file_list(file_list,task_id,vec_dir,db_ip,db_name):
    g_feature_dict = common.FetchFeature(db_ip,db_name)
    vector_file_name = 'vector_%d_%d.vec' %(int(time.time()),os.getpid())
    try:
        if not os.path.exists(vec_dir):
            os.mkdir(vec_dir)
    except Exception,e:
        print e
    vector_handle = open(vec_dir+vector_file_name,'w')
    for fet_file in file_list:
        is_white = True
        if 'White' in fet_file:
            is_white = True
        else:
            is_white = False
        Mist2Vector(g_feature_dict,fet_file,vector_handle,is_white)

def parallel_file_list(fet_dir,vec_dir,num_tasks,db_ip,db_name):
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
        
        worker = Process(target=process_file_list,args=(current_file_list,task,vec_dir,db_ip,db_name))
        worker.start()
        worker_list.append(worker)
        print 'Task %d invoked.'%task    
    
    for worker in worker_list:
        worker.join()
        print 'one worker exit.'

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print 'Usage:'
        print sys.argv[0],' dir_of_fet dir_of_vector db_ip db_name num_tasks'
        sys.exit()
    
    fet_dir = sys.argv[1]
    vec_dir = sys.argv[2]
    db_ip = sys.argv[3]
    db_name = sys.argv[4]
    num_tasks = int(sys.argv[5])
    if fet_dir[-1]!= '/':
        fet_dir+='/'
    if vec_dir[-1]!= '/':
        vec_dir+='/'

    if num_tasks > 12 or num_tasks < 1:
        print 'invalid num_tasks: %d' %num_tasks
        sys.exit()

    if not common.g_sample_fet in fet_dir:
        print 'invalid input directory:',fet_dir
        print 'MUST contain:',common.g_sample_fet
        sys.exit()
    if not common.g_vector_dir in vec_dir:
        print 'invalid input directory:',vec_dir
        print 'MUST contain:',common.g_vector_dir
        sys.exit()

    parallel_file_list(fet_dir,vec_dir,num_tasks,db_ip,db_name);     
    print 'Main process exit.'

    


