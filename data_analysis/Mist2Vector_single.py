# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
from common import *
import time
from Similarity import *

def _FindLocation(feature_dict,vector):
    TabName=get_table_name(vector)
    behavior_list = TabName.split(delimiter_table_name)
    if len(behavior_list)==2:
        if behavior_list[0][:3]=='1_8' and behavior_list[1][:3]=='1_8':
            return -1
    if TabName in feature_dict:
        for Feature in feature_dict[TabName]:
            if Similar_N_gram(vector,Feature[1]):
                return Feature[0]
    return -1

def Mist2Vector(feature_dict,fet_file,vector_handle,is_white):
    ReadHandle=open(fet_file,'r')
    digit_dict={}
    total_num=0
    #abandon_num=0
    reserve_num=0
    for line in ReadHandle:
        total_num += 1
        line=line.strip('\n')
        [feature,freq]=line.split(delimiter_count)
        index = _FindLocation(feature_dict,feature)
        if index == -1:
            #abandon_num += 1
            continue
        reserve_num += 1    
        freq = int(freq)
        digit_dict[index]=int(freq)

    if len(digit_dict)==0:
        return
    md5=fet_file[fet_file.rfind('/')+1:fet_file.rfind('.')]
    vector_handle.write('%s %d/%d '%(md5,reserve_num,total_num))
    digit_list=[(k,digit_dict[k]) for k in sorted(digit_dict.keys())]
    if is_white:
    	vector_handle.write('+1 ')
    else:
    	vector_handle.write('-1 ')
    
    for item in digit_list:
        vector_handle.write('%s:%d '%(item[0],item[1]))       
    vector_handle.write('\n')

    #reserve_num=total_num-abandon_num
    #supplyment_handle.write('%s:%d,%d,%d\n'%(FetFile,total_num,reserve_num,abandon_num)) 
    


