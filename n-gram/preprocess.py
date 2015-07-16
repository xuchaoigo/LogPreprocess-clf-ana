from __future__ import division  
import os
import ConfigParser
import string
from common import *
import sys
from Similarity import *
import time
from multiprocessing import Process,Pool

g_top_log_dir = ''
g_top_mist_dir = ''
g_top_join_dir = ''
g_top_fet_dir = ''

def RemoveSame(vector_list):
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

def Merge(join_file,fet_file):
    readhandle=open(join_file,'r')
    writehandle=open(fet_file,'w')
    vectorlist=[]
    for line in readhandle:
        line=line.strip('\n')
        table_name=get_table_name(line)
        vectorlist.append([table_name,line])
    featurelist=RemoveSame(vectorlist)
    for i in range(0,len(featurelist)):
        writehandle.write('%s%s%d\n'%(featurelist[i][0],delimiter_count,featurelist[i][1]))
    readhandle.close()
    writehandle.close()

def Mist2NFet(mist_file,join_file):
    readhandle=open(mist_file,'r')
    writehandle=open(join_file,'w')
    mistlist=[]
    for line in readhandle:
        mistlist.append(line.strip('\n'))
    for i in range(0,len(mistlist)-Ngram+1):
        for j in range(i,i+Ngram-1):
            writehandle.write('%s%s'%(mistlist[j],delimiter_behavior))
        writehandle.write('%s\n'%mistlist[i+Ngram-1])
    readhandle.close()

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
    
def WriteLine(WriteHandle,MistLine):
    length=len(MistLine)
    for item in range(0,length-1):
        if MistLine[item]!='':
            WriteHandle.write(MistLine[item])
            WriteHandle.write(delimiter_target)
    WriteHandle.write(MistLine[length-1])
    WriteHandle.write('\n')

def SampleToMist(ReadPath,WritePath):
    ReadHandle=open(ReadPath,'r')
    WriteHandle=open(WritePath,'w')
    for line in ReadHandle:
        line=line.strip('\n')
        line=line.strip('\\')
        MistLine=ProcessLine(line)
        if len(MistLine)<3:
            continue
        WriteLine(WriteHandle,MistLine)
    ReadHandle.close()
    WriteHandle.close()

def process_file(log_file):
    tail_path = log_file[len(g_top_log_dir):len(log_file)]
    fet_file = g_top_fet_dir+tail_path
    if os.path.exists(fet_file):
        return
    
    mist_file = g_top_mist_dir+tail_path
    join_file = g_top_join_dir+tail_path
    SampleToMist(log_file,mist_file)
    Mist2NFet(mist_file,join_file)
    Merge(join_file,fet_file)

def parallel_process_pool(log_dir,num_tasks):
    #get all files under sample_dir
    file_list = []
    for root,dirs,files in os.walk(log_dir):
        for name in files:
            log_file = os.path.join(root,name)
            file_list.append(log_file)

            tail_path = log_file[len(g_top_log_dir):]
            mist_file = g_top_mist_dir+tail_path
            join_file = g_top_join_dir+tail_path
            fet_file = g_top_fet_dir+tail_path
            mist_dir = mist_file[0:mist_file.rfind('/')]
            if not os.path.exists(mist_dir):
                os.makedirs(mist_dir)
            join_dir = join_file[0:join_file.rfind('/')]
            if not os.path.exists(join_dir):
                os.makedirs(join_dir)
            fet_dir = fet_file[0:fet_file.rfind('/')]
            if not os.path.exists(fet_dir):
                os.makedirs(fet_dir)
        
    print '%d files to process.'%len(file_list)
    process_pool = Pool(processes=num_tasks)
    process_pool.map(process_file,file_list)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],' dir_to_handle dir_to_output num_tasks'
        print 'dir_to_handle: must be parent directory of Log directory!'
        print 'dir_to_output: must be the output(Mist/Join/Fet) directory!'
        print 'num_tasks: number of processes to invoke'
        sys.exit()
    start_time=time.time() 
    sample_dir = sys.argv[1]
    output_dir = sys.argv[2]
    num_tasks = int(sys.argv[3])
    if num_tasks >12 or num_tasks < 1:
        print 'invalid num_tasks: %d' %num_tasks
        sys.exit()

    #xuc: change dirs:sample_dir=XXXX/refiner_out
    g_top_log_dir = os.path.join(sample_dir,'Log')
    g_top_mist_dir = os.path.join(output_dir,'Mist')
    g_top_join_dir = os.path.join(output_dir,'Join')
    g_top_fet_dir = os.path.join(output_dir,'Fet')

    parallel_process_pool(g_top_log_dir,num_tasks)
       
    print 'Main process exit!'
    end_time=time.time()
    print 'new preprocess time consumed:%f'%(end_time-start_time)
