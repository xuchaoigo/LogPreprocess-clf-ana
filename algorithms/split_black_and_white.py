# -*- coding: cp936 -*-
import os
import sys
import string
import os,time
import time

def split_black_and_white(vector_file):
    read_handle = open(vector_file,'r')
    black_handle = open('%s.nega'%vector_file, 'w')
    white_handle = open('%s.posi'%vector_file, 'w')

    black_cnt = 0
    white_cnt = 0
    lines = read_handle.readlines()
    for line in lines:
        if line[:2] == '-1':
            black_handle.write(line)
            black_cnt+=1
        else:
            white_handle.write(line)
            white_cnt+=1
    print 'black vec %d,white vec %d, all %d'%(black_cnt,white_cnt,white_cnt+black_cnt)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' vector_file'
        sys.exit()
    
    print 'Main process start.'
    vector_file = sys.argv[1]
    split_black_and_white(vector_file);     
    print 'Main process exit.'
