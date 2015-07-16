# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import os,time
from common import *
from Similarity import *
import time
import shutil 

def RenameTable2Split(dir_of_tab_1, dir_of_tab_2, dir_of_split):
    gid=0
    for root,dirs,files in os.walk(dir_of_tab_1):
        for name in files:
            table_file = os.path.join(root,name)
            gid+=1
            split_file = os.path.join(dir_of_split,name)
            shutil.copy(table_file,split_file)
            pos = name.find("task");
            table_name = name[3:pos-1]              
            table_name=table_name.replace("$","_")
            new_split_name = dir_of_split+'splite%d.%s'%(gid,table_name)
            os.rename(split_file,new_split_name)

    for root,dirs,files in os.walk(dir_of_tab_2):
        for name in files:
            table_file = os.path.join(root,name)
            gid+=1
            split_file = os.path.join(dir_of_split,name)
            shutil.copy(table_file,split_file)
            pos = name.find("task");
            table_name = name[3:pos-1]              
            table_name=table_name.replace("$","_")
            new_split_name = dir_of_split+'splite%d.%s'%(gid,table_name)
            os.rename(split_file,new_split_name)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],' dir_of_tab_1,dir_of_tab_2, dir_of_split '
        sys.exit()
    
    dir_of_tab_1 = sys.argv[1]
    dir_of_tab_2 = sys.argv[2]
    dir_of_split = sys.argv[3]
    
    RenameTable2Split(dir_of_tab_1, dir_of_tab_2, dir_of_split);     

    print 'Main process exit.'
