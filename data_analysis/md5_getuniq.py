# -*- coding: cp936 -*-
import os
import sys
import string
import os,time

VectorDict={}
def insert_dict_ingore_label(line):
    global VectorDict
    if len(line)<=36:
        return
    part_line=line[36:]
    if part_line not in VectorDict:
        VectorDict[part_line]=[1,line]
    else:
        VectorDict[part_line][0] += 1  

def get_uniq_ingore_label(VectorDict_tmp):
    cnt=0
    for item in VectorDict_tmp:
        cnt+=1
        insert_dict_ingore_label(VectorDict_tmp[item][1])
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
def filter_None(line):
    begin=line.find('None')
    if begin < 0:
        return line
    end=line.find(' ',begin,-1)
    None_string=line[begin:end+1]
    line=line.replace(None_string,'')
    return line

def insert_dict(line,VectorDict_tmp):
    line=filter_None(line)
    part_line=line[32:]
    if part_line in VectorDict_tmp:
        VectorDict_tmp[part_line][0] += 1
    else:
        VectorDict_tmp[part_line]=[1,line]

def get_uniq(srcfile,VectorDict_tmp):
    ReadHandle=open(srcfile,'r')
    cnt=0
    for line in ReadHandle:
        cnt+=1
        insert_dict(line.strip('\n'),VectorDict_tmp)
        if cnt%10000==0:
            print 'line=',cnt
    ReadHandle.close()

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print sys.argv[0],' vec_file'
        print 'Used for eliminating duplicated feature vectors in vec_file'
        sys.exit() 
    
    orig_file = sys.argv[1]
    final_uniq_file = '%s.uniq.final'%orig_file
    VectorDict_tmp={}
    get_uniq(orig_file,VectorDict_tmp)
    get_uniq_ingore_label(VectorDict_tmp)
    write2File_ingore_label(final_uniq_file)
