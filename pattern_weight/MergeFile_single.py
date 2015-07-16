# -*- coding: cp936 -*-
from __future__ import division  
import os
import string
import os
from common import *
from Similarity import *
import time

def insert_feature(local_feature,line,label):
    feature=line
    table_name=get_table_name(feature) 
    if table_name == '1_8$1_8':
        return
    if table_name in local_feature:
        similar_bool= False
        for i,item in enumerate(local_feature[table_name]):
            if Similar_N_gram(feature,item[0]):
                similar_bool = True
                break
        if similar_bool == False:
            local_feature[table_name].append([feature,1-label,label])
    else:
        local_feature[table_name]=[]
        local_feature[table_name].append([feature,1-label,label]) 
     
def merge_fet_file(task_feature,fet_file,label):
    local_feature={}
    file_handle=open(fet_file,'r')
    for line in file_handle: 
        insert_feature(local_feature,line.strip('\n'),label)
    file_handle.close()
    for table_name in local_feature:
        if table_name in task_feature:
            for l_feature in local_feature[table_name]:
                similar_bool = False
                for i,g_feature in enumerate(task_feature[table_name]):
                    if Similar_N_gram(l_feature[0],g_feature[0]):
                        similar_bool = True 
                        task_feature[table_name][i][1+label] += 1 
                        break
                if similar_bool == False:
                    task_feature[table_name].append(l_feature)
        else:
            task_feature[table_name]=local_feature[table_name] 

def write_feature_file(task_feature,feature_file):
    write_handle=open(feature_file,'w')
    for table_name in task_feature:
        write_handle.write('%s%s'%(table_name,delimiter_table))
        for i in range(0,len(task_feature[table_name])-1):
            write_handle.write('%s%s%d%s%d%s'%(task_feature[table_name][i][0],delimiter_item,task_feature[table_name][i][1],delimiter_item,task_feature[table_name][i][2],delimiter_feature))
        write_handle.write('%s%s%d%s%d\n'%(task_feature[table_name][-1][0],delimiter_item,task_feature[table_name][-1][1],delimiter_item,task_feature[table_name][-1][2]))
    write_handle.close() 


