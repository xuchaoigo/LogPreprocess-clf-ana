from __future__ import division
import os
import ConfigParser
import string
from common import *
import sys

def Similarity_single_arg(arg1,arg2):
    list1 = arg1.split(delimiter_arg)
    list2 = arg2.split(delimiter_arg)
    len1 = len(list1)
    len2 = len(list2)
    if abs(len1-len2) >= 3:
        return 0.0
    if len1 > len2:
        len_min = len2
    else:
        len_min = len1

    if len_min == 0:
   	    return 0.0

    sum=0.0
    for i in xrange(0, len_min):
        if list1[i] == list2[i]:
            sum = sum+(1.0/len1+1.0/len2)/2
        else:
            break
    return sum
"""
def Similarity_multi_args(arg1_list,arg2_list):
    len1 = len(arg1_list) 
    len2 = len(arg2_list)
    if len1 != len2:
  	    return 0.0
    len_common = len1; 

    if len_common ==0:
        return 0.0

    weight = 1.0/len_common
    similarity_value = 0.0
    for i in xrange(0,len_common):
    	similarity_value += weight*Similarity_single_arg(arg1_list[i],arg2_list[i])
    
    return similarity_value
"""

def Similar(vector1,vector2):
    arg1 = vector1.split(delimiter_target)
    arg2 = vector2.split(delimiter_target)
    len1 = len(arg1)
    len2 = len(arg2)
    if len1 != len2:
	    return False
    if arg1[0] != arg2[0]:
	    return False
    if arg1[1] != arg2[1]:
	    return False
    if len1 <=2:
        return True

    Threshold=ThresholdList[int(arg1[0])]
    sublen=len1-2  #but arg[0], arg[1]
    weight = 1.0/sublen   
    similarity_value = 0.0
    for i in xrange(0,sublen):
        similarity_value += weight*Similarity_single_arg(arg1[i+2],arg2[i+2])
        if similarity_value >= Threshold - 1e-6:
    	    return True
    return False 

def Similar_N_gram(feature1,feature2):
    vectorlist1=feature1.split(delimiter_behavior)
    vectorlist2=feature2.split(delimiter_behavior)
    len1=len(vectorlist1)
    len2=len(vectorlist2)
    if len1 != len2:
        return False
    for i in xrange(0,len1):
        if not Similar(vectorlist1[i],vectorlist2[i]):
            return False
    return True
