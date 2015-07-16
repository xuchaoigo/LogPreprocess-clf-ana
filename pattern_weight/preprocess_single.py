from __future__ import division  
import os
import ConfigParser
import string
from common import *
import sys
from Similarity import *
import time

def _remove_same(vector_list):
    single_list=[]
    num=0
    vector_length=len(vector_list)
    while num<vector_length:
        single_list.append(vector_list[num])
        num_next=num+1
        while num_next<vector_length:
            if Similar_N_gram(vector_list[num],vector_list[num_next]):
                num_next += 1
            else:
                break
        num=num_next 
    return single_list


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

def _log2mist(log_lines,ngram):
    mist_lines = []
    for line in log_lines:
        line=line.strip('\n')
        line=line.strip('\\')
        MistLine=_get_paramlist(line)
        if len(MistLine)<3:
            continue
        mist_lines.append(_format_mist(MistLine))
    if ngram != 1:
        mist_lines=_mist2join(mist_lines,ngram)
    fet_lines=_remove_same(mist_lines)
    return fet_lines

def process_file(log_file,fet_file,ngram):
    log_handle = open(log_file,'r')
    fet_lines = _log2mist(log_handle.readlines(),ngram)
    log_handle.close()
    fet_handle = open(fet_file,'w')
    for line in fet_lines:
        fet_handle.write('%s\n'%line)
    fet_handle.close()
