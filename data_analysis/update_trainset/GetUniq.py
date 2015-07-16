# -*- coding: cp936 -*-
import os
import sys
import string
import os,time

VectorDict={}
def insert_dict_ingore_label(line):
    global VectorDict
    if len(line)<=2:
        return
    newline=line[3:len(line)]
    if newline not in VectorDict:
        VectorDict[newline]=[1,line]
    else:
        VectorDict[newline][0] += 1  

def get_uniq_ingore_label(VectorDict_tmp):
    cnt=0
    for item in VectorDict_tmp:
        cnt+=1
        insert_dict_ingore_label(item.strip('\n'))
        if cnt%10000==0:
            print 'line=',cnt

def write2File_ingore_label(filter_vector_file):
    global VectorDict      
    print 'start Write2File'
    vector_handle=open(filter_vector_file,'w')
    for item in VectorDict:
        if VectorDict[item][0] == 1:
            vector_handle.write('%s\n'%VectorDict[item][1])
    vector_handle.close()

##################

def insert_dict(line,VectorDict_tmp):
    if line in VectorDict_tmp:
        VectorDict_tmp[line]+=1
    else:
        VectorDict_tmp[line]=1

def get_uniq(srcfile,VectorDict_tmp):
    ReadHandle=open(srcfile,'r')
    cnt=0
    for line in ReadHandle:
        cnt+=1
        insert_dict(line,VectorDict_tmp)
        if cnt%10000==0:
            print 'line=',cnt
    ReadHandle.close()

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print sys.argv[0],' vec_file'
        print 'Used for eliminating duplicated feature vectors in vec_file'
        exit(-1)
    
    orig_file = sys.argv[1]
    final_uniq_file = '%s.uniq.final'%orig_file

    VectorDict_tmp={}
    get_uniq(orig_file,VectorDict_tmp)
    get_uniq_ingore_label(VectorDict_tmp)
    write2File_ingore_label(final_uniq_file)
    
    """
def Process():
    global VectorDict
    st=time.clock()
    write2File_ingore_label(final_uniq_file)
    et=time.clock()
    print 'getcnt time=',(et-st)
Process()
    """
