# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import os,time
import time

def _get_readable_time():
    return time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))

def check_tbl(table_dir):
    cnt=0
    dict = {}
    for root,dirs,files in os.walk(table_dir):
        for name in files:
            l = name.split('_')
            if l[1] in dict:
                dict[l[1]]+=1
            else:
                dict[l[1]]=1
    for k in dict:
        cnt+=1
        print '%s:%d'%(k,dict[k])
    print 'total %d tbl'%cnt

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' Feature_dir'
        sys.exit()
    
    merge_table_dir = sys.argv[1]
    check_tbl(merge_table_dir);     

    print 'Main process exit.'
