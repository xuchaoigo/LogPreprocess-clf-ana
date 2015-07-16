# -*- coding: cp936 -*-
from __future__ import division  
import os
import string
import os
from common import *
from Similarity import *
import time

g_white_label = '+1'
g_black_label = '-1'

def insert_feature(task_feature,line,label):
    global g_white_label
    [feature,num]=line.split(delimiter_count)
    table_name=get_table_name(feature)
    behavior_list = table_name.split(delimiter_table_name)
    if len(behavior_list)==2:
        if behavior_list[0][:3]=='1_8' and behavior_list[1][:3]=='1_8':
            return    
    if table_name in task_feature:
        for i,item in enumerate(task_feature[table_name]):
            if Similar_N_gram(feature,item[0]):
                if label == g_white_label:
                    task_feature[table_name][i][2] += 1
                else:
                    task_feature[table_name][i][1] += 1
                return
        if label == g_white_label:
            feature_item=[feature,0,1]
        else:
            feature_item=[feature,1,0]
        task_feature[table_name].append(feature_item)
        return
    if label == g_white_label:
        feature_item=[feature,0,1]
    else:
        feature_item=[feature,1,0]
    task_feature[table_name]=[]
    task_feature[table_name].append(feature_item)    
     
def merge_fet_file(task_feature,local_fet_file,remote_fet_file):
    global g_white_label
    global g_black_label
    if remote_fet_file.find('White')>=0:
        sample_label = g_white_label
    else:
        sample_label = g_black_label
    file_handle=open(local_fet_file,'r')
    for line in file_handle: 
        insert_feature(task_feature,line.strip('\n'),sample_label)
    file_handle.close()

def write_feature_file(task_feature,feature_file):
    write_handle=open(feature_file,'w')
    for table_name in task_feature:
        write_handle.write('%s%s'%(table_name,delimiter_table))
        for i in range(0,len(task_feature[table_name])-1):
            write_handle.write('%s%s%d%s%d%s'%(task_feature[table_name][i][0],delimiter_item,task_feature[table_name][i][1],delimiter_item,task_feature[table_name][i][2],delimiter_feature))
        write_handle.write('%s%s%d%s%d\n'%(task_feature[table_name][-1][0],delimiter_item,task_feature[table_name][-1][1],delimiter_item,task_feature[table_name][-1][2]))
    write_handle.close()
    
