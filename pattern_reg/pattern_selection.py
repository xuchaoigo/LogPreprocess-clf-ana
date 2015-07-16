from __future__ import division
import re
import os
import sys
import time
import string

def collection_single(g_pattern,file_name):
    if file_name.find('white')>=0:
        label=1
    else:
        label=0
    file_handle=open(file_name,'r')
    for line in file_handle:
        pattern,count=line.strip('\n').split(':')
        count= int(count)
        if pattern in g_pattern:
            g_pattern[pattern][label]=count
        else:
            g_pattern[pattern]=[count*(1-label),count*label]
    file_handle.close()

def contribution_value(feature,black_num,white_num):
    black_in=feature[0]
    white_in=feature[1]
    black_out=black_num-black_in
    white_out=white_num-white_in
    up=pow((black_in*white_out-white_in*black_out),2)
    down=(black_in+white_in)*(black_out+white_out)
    return up/down
 
def rank_pattern(g_pattern,selection_file,black_num,white_num):
    pattern_contribution={}
    for pattern in g_pattern:
        pattern_contribution[pattern]=contribution_value(g_pattern[pattern],black_num,white_num)
    contribution_list= sorted(pattern_contribution.iteritems(), key=lambda d:d[1], reverse = True)
    file_handle=open(selection_file,'w')
    for pattern in contribution_list:
        file_handle.write('%s:%f\n'%(pattern[0],pattern[1]))
    file_handle.close() 

def collection(black_pattern_file,white_pattern_file,selection_file,black_sample_num,white_sample_num):
    g_pattern={} 
    collection_single(g_pattern,white_pattern_file)
    collection_single(g_pattern,black_pattern_file)
    rank_pattern(g_pattern,selection_file,black_sample_num,white_sample_num)
  
def select_pattern(pattern_collection_dir,pattern_selection_dir,black_sample_num,white_sample_num):
    pattern_file_list=os.listdir(pattern_collection_dir)
    for pattern_file in pattern_file_list:
        if pattern_file.find('black')>=0:
            black_pattern_file=os.path.join(pattern_collection_dir,pattern_file)
            white_pattern_file=os.path.join(pattern_collection_dir,pattern_file.replace('black','white'))
            selection_file=pattern_file.replace('black','pattern')
            print 'rank pattern into %s'%selection_file
            selection_file=os.path.join(pattern_selection_dir,selection_file)
            collection(black_pattern_file,white_pattern_file,selection_file,black_sample_num,white_sample_num)

def count_file_num(vector_file):
    print 'count file num'
    file_handle=open(vector_file,'r')
    black_num=0
    white_num=0
    for line in file_handle:
        if line.find('+1')>=0:
            white_num += 1
        else:
            black_num +=1
    file_handle.close()
    return [black_num,white_num] 

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'Usage:'
        print sys.argv[0], ' pattern_collection_dir,pattern_selection_dir,vector_file'
        sys.exit()
    start_time=time.time()
    pattern_collection_dir=sys.argv[1]
    pattern_selection_dir=sys.argv[2]
    vector_file=sys.argv[3]
    black_sample_num,white_sample_num=count_file_num(vector_file)
    print 'black_num:%d white_num:%d'%(black_sample_num,white_sample_num)
    select_pattern(pattern_collection_dir,pattern_selection_dir,black_sample_num,white_sample_num)
    end_time=time.time()
    print 'select feature finished,time consumed:%d'(end_time-start_time)
    
