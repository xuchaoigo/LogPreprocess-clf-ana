# -*- coding: cp936 -*-
import os
import sys
import string
import os,time
import time

def merge_svm_data(svm_dir,outfile):
    file_list = []
    write_handle = open(outfile, 'w')
    for root,dirs,files in os.walk(svm_dir):
        for name in files:
            svm_file = os.path.join(root,name)
            read_handle = open(svm_file,'r')
            lines = read_handle.readlines()
            outlines=[]
            for line in lines:
                if line.strip()=='':
                    continue
                pos1 = line.find("None:")
                if pos1 != -1:
                    pos2 = line.find(" ",pos1)
                    newline = line[:pos1]+line[pos2+1:]
                    outlines.append(newline)
                else:
                    outlines.append(line)
            write_handle.writelines(outlines)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],' svm_data_dir output_file_name'
        sys.exit()
    
    print 'Main process start.'
    svm_dir = sys.argv[1]
    out_name = sys.argv[2]
    merge_svm_data(svm_dir,out_name);     
    print 'Main process exit.'
