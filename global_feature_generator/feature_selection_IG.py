from __future__ import division
import os
from common import *
import sys
import math

def entropy(p,q):
    if p==0:
        entropy=-q*math.log(q,2)
    elif q==0:
        entropy=-p*math.log(p,2)
    else:    
        entropy=(-p*math.log(p,2)-q*math.log(q,2))
    return entropy

def contribution_value(feature,black_num,white_num):
    black_in=float(int(feature[2]))
    white_in=float(int(feature[3]))
    black_num = float(black_num)
    white_num = float(white_num)
    if black_in>black_num:
        black_in = black_num
    if white_in>white_num:
        white_in = white_num
    black_out= float(black_num-black_in)
    white_out= float(white_num-white_in)
    all_num = float(black_num+white_num)
    all_in = float(black_in+white_in)
    all_out = float(black_out+white_out)
    try:
            system_entropy = -(black_num/all_num)*math.log(black_num/all_num,2)-(white_num/all_num)*math.log(white_num/all_num,2)
            conditional_entropy = entropy(black_in/all_in,white_in/all_in)*all_in+entropy(black_out/all_out,white_out/all_out)*all_out
    except Exception,e:
        print 'black_in=',black_in    
        print 'black_out=',black_out
        print 'white_in=',white_in
        print 'white_out=',white_out
        print 'black_num=',black_num
        print 'white_num=',white_num 

    return system_entropy-conditional_entropy/all_num
    
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
    file_handle=open('feature_file_ig_%s_%s.log'% (output_feature_num,db_name),'w')
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
    #iter h
    #white_num = 1700000
    #black_num = 6410000
    print 'count num done, black=%d,white=%d'%(black_num,white_num)
    g_feature=FetchFeature('nj02-sw-kvmserver01.nj02',db_name) 
    feature_list=compute_contribution(g_feature,db_name,black_num,white_num, output_feature_num)


