from __future__ import division
import os
import ConfigParser
import string
from common import *
import sys

def Similarity_single_arg(arg1,arg2):
    List1 = arg1.split(delimiter_in_arg)
    List2 = arg2.split(delimiter_in_arg)
    len1 = len(List1)
    len2 = len(List2)
    if len1 > len2:
        len_min = len2
    else:
        len_min = len1

    if len_min == 0:
   	return 0.0

    sum=0.0
    for i in range(0, len_min):
        if List1[i] == List2[i]:
            sum = sum+(1.0/len1+1.0/len2)/2
        else:
            break
    return sum

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
    for i in range(0,len_common):
    	similarity_value += weight*Similarity_single_arg(arg1_list[i],arg2_list[i])
    
    return similarity_value


def Similar(vector1,vector2):
    arg1 = vector1.split('#')
    arg2 = vector2.split('#')
    len1 = len(arg1)
    len2 = len(arg2)
    if len(arg1) != len(arg2):
	return False
    if arg1[0] != arg2[0]:
	return False
    if arg1[1] != arg2[1]:
	return False

    partial_arg1_list = arg1[2:len(arg1)]
    partial_arg2_list = arg2[2:len(arg2)]
    if Similarity_multi_args(partial_arg1_list,partial_arg2_list) >= Threshold - 1e-6:
    	return True
    else:
	return False 
