from __future__ import division  
import os
import ConfigParser
import string
from common import *
import sys
from Similarity import *
import time

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

def process_file(log_file,fet_file,ngram):
    log_handle = open(log_file,'r')
    mist_lines = _log2mist(log_handle.readlines())
    log_handle.close()
    join_lines = _mist2join(mist_lines,ngram)
    fet_lines = _join2fet(join_lines)
    fet_handle = open(fet_file,'w')
    for line in fet_lines:
        fet_handle.write('%s\n'%line)
    fet_handle.close()
