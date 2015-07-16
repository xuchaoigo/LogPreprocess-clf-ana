# -*- coding: cp936 -*-
import os
import sys
import string
import os,time



def insert_dict_ingore_label(VectorDict,line):
    newline=line[3:len(line)]
    if newline not in VectorDict:
        VectorDict[newline]=[1,line]
    else:
        VectorDict[newline][0] += 1  

def get_uniq_ingore_label(srcfile):
    VectorDict={}
    ReadHandle=open(srcfile,'r')
    vector_lines=ReadHandle.readlines()
    ReadHandle.close()
    cnt=0
    for i in range(len(vector_lines)):
        cnt+=1
        insert_dict_ingore_label(VectorDict,vector_lines[i].strip('\n'))
        if cnt%10000==0:
            print 'line=',cnt
    return VectorDict

def write2File_ingore_label(VectorDict,filter_vector_file):
    print 'start Write2File'
    vector_handle=open(filter_vector_file,'w')
    for item in VectorDict:
        if VectorDict[item][0] == 1:
            vector_handle.write('%s\n'%VectorDict[item][1])
    vector_handle.close()

##################

def insert_dict(line):
    global VectorDict
    if line in VectorDict:
        VectorDict[line]+=1
    else:
        VectorDict[line]=1

def get_uniq(srcfile):
    ReadHandle=open(srcfile,'r')
    cnt=0
    for line in ReadHandle:
        cnt+=1
        insert_dict(line)
        if cnt%10000==0:
            print 'line=',cnt
    ReadHandle.close()

def Write2File(writehandle):
    global VectorDict      
    print 'start Write2File'
    WriteHandle=open(writehandle,'w')
    VectorList= sorted(VectorDict.iteritems(), key=lambda d:d[1], reverse = True)
    for item in VectorList:
        #WriteHandle.write('%scnt=%s\n\n'%(item[0],item[1]))
        WriteHandle.write('%s'%(item[0]))
    WriteHandle.close() 
    #
def process(vector_dir,filter_dir):
    vector_file_list=os.listdir(vector_dir)
    for vector_file in vector_file_list:
        uniq_vector=get_uniq_ingore_label(os.path.join(vector_dir,vector_file))
        write2File_ingore_label(uniq_vector,os.path.join(filter_dir,vector_file))   
        

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'Usage:'
        print sys.argv[0],' vector_dir filter_vector_dir '
        print 'Used for eliminating duplicated feature vectors in vec_file'
        sys.exit()
    
    vector_dir = sys.argv[1]
    filter_dir=sys.argv[2]
    if not os.path.exists(filter_dir):
        os.mkdir(filter_dir)
    process(vector_dir,filter_dir) 
