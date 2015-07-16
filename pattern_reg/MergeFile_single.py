# -*- coding: cp936 -*-
from __future__ import division  
import os
import string
import os
from common import *
from Similarity import *
import time

def insert_feature(task_feature,line):
    feature=line
    table_name=get_table_name(feature) 
    if table_name == '1_8$1_8':
        return
    if table_name in task_feature:
        similar_bool= False
        for item in task_feature[table_name]:
            if Similar_N_gram(feature,item):
                similar_bool = True
                break
        if similar_bool == False:
            task_feature[table_name].append(feature)
    else:
        task_feature[table_name]=[]
        task_feature[table_name].append(feature) 
     
def merge_fet_file(task_feature,fet_file):
    file_handle=open(fet_file,'r')
    for line in file_handle: 
        insert_feature(task_feature,line.strip('\n'))
    file_handle.close()

def write_feature_file(task_feature,feature_file):
    write_handle=open(feature_file,'w')
    for table_name in task_feature:
        write_handle.write('%s%s'%(table_name,delimiter_table))
        for i in range(0,len(task_feature[table_name])-1):
            write_handle.write('%s%s'%(task_feature[table_name][i],delimiter_feature)) 
        write_handle.write('%s\n'%(task_feature[table_name][-1]))
    write_handle.close() 


