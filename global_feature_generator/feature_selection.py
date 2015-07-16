from __future__ import division
import os
from common import *
import sys

def contribution_value(feature,black_num,white_num):
    black_in=int(feature[2])
    white_in=int(feature[3])
    black_out=black_num-black_in
    white_out=white_num-white_in
    up=pow((black_in*white_out-white_in*black_out),2)
    down=(black_in+white_in)*(black_out*white_out)
    return up/down
    
def compute_contribution(g_feature,db_name,black_num,white_num,output_feature_num):
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
    print
    file_handle=open('feature_file_%s_%s.log'%(output_feature_num,db_name),'w')
    print 'one fet:',g_feature_item[contribution_list[0][0]]
    for i in range(int(output_feature_num)):
        try:
            file_handle.write('%d%s%s%s%d%s%d\n'%(g_feature_item[contribution_list[i][0]][0],delimiter_item,g_feature_item[contribution_list[i][0]][1],delimiter_item,g_feature_item[contribution_list[i][0]][2],delimiter_item,g_feature_item[contribution_list[i][0]][3]))
        except Exception,e:
            print e
            print 'failed fet=',g_feature_item[contribution_list[i][0]]
            continue

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'db_name(in server01) feature_num'
        sys.exit()

    db_name = sys.argv[1]
    output_feature_num = sys.argv[2]
    
    #iter_g
    white_num = 1699109
    black_num = 4146950
    #iter_h
    #white_num = 1700000
    #black_num = 6410000
    print 'count num done, black=%d,white=%d'%(black_num,white_num)
    g_feature=FetchFeature('nj02-sw-kvmserver01.nj02',db_name) 
    feature_list=compute_contribution(g_feature,db_name,black_num,white_num, output_feature_num)



