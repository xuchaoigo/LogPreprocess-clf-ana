from __future__ import division
import os
from common import *
import sys
def count_file_num(top_src_dir):
    num=0
    for root,dirs,files in os.walk(top_src_dir):
        for name in files:
            num +=1
    return num

def contribution_value(feature,black_num,white_num):
    black_in=feature[2]
    white_in=feature[3]
    black_out=black_num-black_in
    white_out=white_num-white_in
    up=pow((black_in*white_out-white_in*black_out),2)
    down=(black_in+white_in)*(black_out*white_out)
    return up/down
    
def compute_contribution(g_feature,black_num,white_num):
    num = 0
    g_feature_contribution={}
    g_feature_item={}
    for table_name in g_feature:
        for feature_item in g_feature[table_name]:
            num +=1 
            if num%10000==0:
                print 'feature processd:%d'%num
            g_feature_contribution[feature_item[0]]=contribution_value(feature_item,black_num,white_num)
            g_feature_item[feature_item[0]]=feature_item
    contribution_list= sorted(g_feature_contribution.iteritems(), key=lambda d:d[1], reverse = True)
    '''
    file_handle=open('contribution_file.log','w')
    for item in contribution_list:
        file_handle.write('%f:%s\n'%(item[1],item[0]))
    file_handle.close()
    '''
    file_handle=open('feature_file.log','w')
    for i in range(10000):
        file_handle.write('%d&,&%s&,&%d&,&%d\n'%(g_feature_item[contribution_list[i][0]][0],g_feature_item[contribution_list[i][0]][1],g_feature_item[contribution_list[i][0]][2],g_feature_item[contribution_list[i][0]][3]))
    file_handle.close()

def process():
    white_dir='./Sample_train/Fet/White'
    white_num=count_file_num(white_dir)
    black_dir='./Sample_train/Fet/Adware'
    black_num=count_file_num(black_dir)
    g_feature=FetchFeature() 
    feature_list=compute_contribution(g_feature,black_num,white_num)
process()
