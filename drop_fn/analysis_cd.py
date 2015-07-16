from __future__ import division
import os
import sys

def fetch_feature(selection_file):
    feature_dict={}
    file_handle=open(selection_file,'r')
    i = 1
    for line in file_handle:
        line_list=line.strip('\n').split('<IT>')
        black=int(line_list[1])
        white=int(line_list[2])
        max_value=max(white,black)
        min_value=max(1,min(white,black))
        if max_value/min_value <= 10:
            feature_dict[i]='media'
        elif white > black:
            feature_dict[i]='white'
        else:
            feature_dict[i]='black'
        i += 1
    file_handle.close()
    return feature_dict

'''
def fetch_feature(selection_file):
    feature_dict={}
    file_handle=open(selection_file,'r')
    i = 1
    for line in file_handle:
        line_list=line.strip('\n').split('<IT>')
        black=int(line_list[1])
        white=int(line_list[2])
        if white > black:
            feature_dict[i]='white'
        else:
            if black/(white+1) <= 10:
                feature_dict[i]='media'
            else:
                feature_dict[i]='black'
        i += 1
    file_handle.close()
    return feature_dict
'''
'''
def fetch_feature(selection_file):
    feature_dict={}
    i=1
    file_handle=open(selection_file,'r')
    for line in file_handle:
        line_list=line.strip('\n').split('<IT>')
        black=int(line_list[1])
        white=int(line_list[2])
        if black>white:
            feature_dict[i]='black'
        else:
            feature_dict[i]='white'
        i += 1
    file_handle.close()
    return feature_dict
'''

def count_line(line,feature_dict,vector_dict):
    file_handle=open('right_label_vector','a')
    line_list=line.split(' ')
    label = int(line_list[0])
    if label not in vector_dict:
        vector_dict[label]=[]
    black_count=0
    white_count=0
    media_count=0
    for i in range(1,len(line_list)):
        item_list=line_list[i].split(':')
        if feature_dict[int(item_list[0])] == 'black':
            black_count += 1
        elif feature_dict[int(item_list[0])] == 'media':
            media_count += 1
        else:
            white_count += 1
    file_handle.write('%d %d %d     %s\n'%(black_count,media_count,white_count,line))
    file_handle.close()
    vector_dict[label].append([black_count,media_count,white_count])
    
def white_black(vector_file,feature_dict):
    vector_dict={}
    file_handle=open(vector_file,'r')
    for line in file_handle:
        count_line(line.strip('\n'),feature_dict,vector_dict)
    file_handle.close()
    return vector_dict 
    
def save_distribution(vector_dict):
    file_handle=open('right_distribution','w')
    for label in vector_dict:
        file_handle.write('%d distribution\n'%label)
        for file_item in vector_dict[label]:
            file_handle.write('%d %d %d\n'%(file_item[0],file_item[1],file_item[2]))
    file_handle.close()
            

def process(selection_file,vector_file):
    feature_dict=fetch_feature(selection_file)
    vector_dict=white_black(vector_file,feature_dict)
    save_distribution(vector_dict)


if __name__=='__main__':
    if len(sys.argv)!=3:
        print 'Usage:'
        print sys.argv[0],' selection_file cd_vector_file'
        sys.exit()
    process(sys.argv[1],sys.argv[2])
