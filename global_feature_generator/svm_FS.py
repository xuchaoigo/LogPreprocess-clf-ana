from __future__ import division
import os
import sys
from common import *
def compute_contribution(g_feature,black_num,white_num,output_feature_num):
    num = 0
    g_feature_item={}
    for table_name in g_feature:
        for feature_item in g_feature[table_name]:
            num +=1 
            if num%10000==0:
                print 'feature processd:%d'%num
            g_feature_item[feature_item[0]]=feature_item
    print 'one fet:',g_feature_item[contribution_list[0][0]]
    for i in range(int(output_feature_num)*10000):
        file_handle.write('%d%s%s%s%d%s%d\n'%(g_feature_item[contribution_list[i][0]][0],delimiter_item,g_feature_item[contribution_list[i][0]][1],delimiter_item,g_feature_item[contribution_list[i][0]][2],delimiter_item,g_feature_item[contribution_list[i][0]][3]))
    file_handle.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],'db_name(in server01)' 
        sys.exit()

    db_name = sys.argv[1]
    g_feature=FetchFeature('nj02-sw-kvmserver01.nj02',db_name) 

    feature_list=compute_contribution(g_feature,black_num,white_num, output_feature_num)



