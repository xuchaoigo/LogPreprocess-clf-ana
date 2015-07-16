# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import os,time
from common import *
from Similarity import *
from multiprocessing import Process,Manager
import time

def _get_readable_time():
    return time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))

def split_tables(table_dir):
    gid=0
    for root,dirs,files in os.walk(table_dir):
        for name in files:
            table_file = os.path.join(root,name)
            file_handle=open(table_file,'r')
            for line in file_handle: #each line is one independent table      
                pos = line.find(delimiter_table)
                if pos!=-1:
                    table_name = line[:pos]
                else:
                    print 'invalid table:',line
                    return
                gid+=1
                write_handle=open('%s/splite%d.%s'%(table_dir,gid,table_name.replace('$','_')),'w')
                write_handle.write(line)
                write_handle.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' dir_to_handle'
        print 'dir_to_handle: must be global feature directory!'
        sys.exit()
    
    merge_table_dir = sys.argv[1]
    split_tables(merge_table_dir);     

    print 'Main process exit.'
