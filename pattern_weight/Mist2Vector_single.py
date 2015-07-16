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
    if TabName == '1_8$1_8':
        return -1
    if TabName in feature_dict:
        for Feature in feature_dict[TabName]:
            if Similar_N_gram(vector,Feature[1]):
                return Feature[0]
    return -1

def Mist2Vector(feature_dict,fet_file,vector_handle,is_white):
    ReadHandle=open(fet_file,'r')
    digit_list=[]
    #total_num=0
    #abandon_num=0
    #reserve_num=0
    for line in ReadHandle:
        #total_num += 1
        line=line.strip('\n')
        index = _FindLocation(feature_dict,line)
        if index == -1:
            #abandon_num += 1
            continue
        digit_list.append(index)
    ReadHandle.close()
    if is_white:
    	vector_handle.write('+1 ')
    else:
    	vector_handle.write('-1 ')
    
    for digit in digit_list:
        vector_handle.write('%d '%digit)       
    vector_handle.write('\n')

    #reserve_num=total_num-abandon_num
    #supplyment_handle.write('%s:%d,%d,%d\n'%(FetFile,total_num,reserve_num,abandon_num)) 
    


