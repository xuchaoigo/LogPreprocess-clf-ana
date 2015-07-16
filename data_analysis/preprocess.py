from __future__ import division  
import os
import ConfigParser
import string
import common
import sys
from Similarity import *
import time
from multiprocessing import Process,Manager
g_top_log_dir = ''
g_top_mist_dir = ''
g_top_join_dir = ''
g_top_fet_dir = ''

def _remove_same(vector_list):
    divisionlist=[]

    while 1:
        length=len(vector_list)
        if length<=0:
            break
        featuretemp=[]
        [featurevector_table_name,featurevector]=vector_list[0]
        featuretemp.append(featurevector)
        dellist=[]
        for i in range(0,length):
            [vector_table_name,vector]=vector_list[i]
            if featurevector_table_name != vector_table_name:
                continue 
            symbol=Similar_N_gram(featurevector,vector)
            if symbol:
                dellist.append(i)
        featuretemp.append(len(dellist))
        dellist.reverse()
        for item in dellist:
            del vector_list[item]
        divisionlist.append(featuretemp)
    return divisionlist

def _join2fet(join_lines):
    vectorlist=[]
    fet_lines = []
    for line in join_lines:
        line=line.strip('\n')
        table_name=get_table_name(line)
        #NOTE: only works in 2gram
        pos1 = table_name.find('$')        
        behav1 = table_name[0:3]
        behav2 = table_name[pos1+1:pos1+4]
        if behav1 =='1_8' and behav1 == behav2:
            continue
        #if table_name == '1_8$1_8':
        #    continue
        vectorlist.append([table_name,line])
    featurelist=_remove_same(vectorlist)
    for i in range(0,len(featurelist)):
        fet_lines.append('%s%s%d'%(featurelist[i][0],delimiter_count,featurelist[i][1]))
    return fet_lines

def _mist2join(mist_lines,Ngram):
    mistlist=[]
    join_lines = []
    for line in mist_lines:
        mistlist.append(line.strip('\n'))
    for i in range(0,len(mistlist)-Ngram+1):
        result_line = ''
        for j in range(i,i+Ngram-1):
            result_line = '%s%s'%(mistlist[j],delimiter_behavior)
        result_line += '%s'%mistlist[i+Ngram-1]
        join_lines.append(result_line)
    return join_lines

def _get_paramlist(line):
    ParamList=[]
    LineList=line.split('|#|')
    if len(LineList)<3:
        return ParamList
    if TypeList.count(LineList[0])==0:
    	return ParamList
    #xuc: v3 add weird Thread:THREAD|#|0|#|. delete it.
    if LineList[0]=='THREAD' and LineList[1]=='0' and not LineList[2]:   
        return ParamList
    ParamList.append(str(TypeList.index(LineList[0])))
    for i in range(1,len(LineList)):
        if len(LineList[i])!=0:
        	if LineList[i][0]=='\\':
			LineList[i]=LineList[i][1:len(LineList[i])]
    	ParamList.append(LineList[i].replace('\\',delimiter_arg))
    return ParamList
    
def _format_mist(MistLine):
    length=len(MistLine)
    mist = ''
    for item in range(0,length-1):
        if MistLine[item]!='':
            mist += MistLine[item]
            mist += delimiter_target
    mist += MistLine[length-1]
    return mist
def ProcessLine(line):
    ParamList=[]
    LineList=line.split('|#|')
    if len(LineList)<3:
        return ParamList
    if TypeList.count(LineList[0])==0:
    	return ParamList
    ParamList.append(str(TypeList.index(LineList[0])))
    for i in range(1,len(LineList)):
        if len(LineList[i])!=0:
        	if LineList[i][0]=='\\':
			LineList[i]=LineList[i][1:len(LineList[i])]
    	ParamList.append(LineList[i].replace('\\',delimiter_arg))
    return ParamList
    
def _log2mist(log_lines):
    mist_lines = []
    for line in log_lines:
        line=line.strip('\n')
        line=line.strip('\\')
        MistLine=_get_paramlist(line)
        if len(MistLine)<3:
            continue
        mist_lines.append(_format_mist(MistLine))
    return mist_lines

def process_file(log_file):
    tail_path = log_file[len(g_top_log_dir):]
    fet_file = g_top_fet_dir+tail_path
    fet_dir = fet_file[:fet_file.rfind('/')]
    if os.path.exists(fet_file):
        return
    if not os.path.exists(fet_dir):
        os.makedirs(fet_dir)
    log_handle = open(log_file,'r')    
    mist_lines = _log2mist(log_handle)
    join_lines = _mist2join(mist_lines,2)#NOTE: 2-gram    
    fet_lines = _join2fet(join_lines)
    fet_handle = open(fet_file,'w')
    for line in fet_lines:
        fet_handle.write('%s\n'%line)

def process_file_list(file_list,task_id):
    for log_file in file_list:
        process_file(log_file)

def parallel_process_pool(log_dir,fet_dir,num_tasks):
    file_list = []
    for root,dirs,files in os.walk(log_dir):
        for name in files:
            log_file = os.path.join(root,name)
            file_list.append(log_file)

            tail_path = log_file[len(g_top_log_dir):]
            fet_file = g_top_fet_dir+tail_path
            if not os.path.exists(fet_dir):
                os.makedirs(fet_dir)
        
    print '%d files to process.'%len(file_list)
    #print file_list[0]
    #process_pool = Pool(processes=num_tasks)
    #process_pool.map(process_file,file_list)
    #process_file(file_list[0])
    num_files_per_task = int(len(file_list)/num_tasks)
    worker_list = []
    object_manager = Manager()
    #process_file_list(file_list,1)    
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
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],' dir_of_Log dir_of_Fet num_tasks'
        print 'num_tasks: number of processes to invoke'
        sys.exit()
    start_time=time.time() 
    g_top_log_dir = sys.argv[1]
    g_top_fet_dir = sys.argv[2]
    num_tasks = int(sys.argv[3])
    if common.g_sample_log not in g_top_log_dir:
        print '%s MUST contains %s'%(g_top_log_dir, common.g_sample_log)
        sys.exit()
    if common.g_sample_fet not in g_top_fet_dir:
        print '%s MUST contains %s'%(g_top_fet_dir, common.g_sample_fet)
        sys.exit()
    if num_tasks >12 or num_tasks < 1:
        print 'invalid num_tasks: %d' %num_tasks
        sys.exit()
    
    parallel_process_pool(g_top_log_dir,g_top_fet_dir,num_tasks)
       
    print 'Main process exit!'
    end_time=time.time()
    print 'new preprocess time consumed:%f'%(end_time-start_time)
