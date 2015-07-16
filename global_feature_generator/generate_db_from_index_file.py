from __future__ import division
import os
import sys
from common import *

def insert_to_selected(target, index):
    try:
        table_name = get_table_name(target)
        AddItemToDb(table_name, int(index), target)
    except Exception,e:
        print 'AddItemToDb Failed! omit.'
        print target

def generate_selected_db(g_feature,index_set,selected_db_name):
    num = 0
    select_num = 0
    InitCursor('nj02-sw-kvmserver01.nj02')
    SelectDB(selected_db_name)
    fet_file = open('feature_file_%s.txt'%selected_db_name,'w')
    for table_name in g_feature:
        for feature_item in g_feature[table_name]:
            num +=1 
            if num%10000==0:
                print 'feature processd:%d'%num
            if int(feature_item[0]) in index_set:
                select_num +=1
                if select_num%1000==0:
                    print 'feature selected:%d'%select_num
                insert_to_selected(feature_item[1], select_num)
                fet_file.write('%d%s%s%s%s%s%s\n'%(int(feature_item[0]),delimiter_item,feature_item[1],delimiter_item,feature_item[2],delimiter_item,feature_item[3]))

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],'src_db_name selected_db_name selected_index_file' 
        print 'NOTE:all DB default in server01'
        sys.exit()

    g_feature=FetchFeature('nj02-sw-kvmserver01.nj02',sys.argv[1])
    selected_index_file = open( sys.argv[3],'r')
    index_set=set() 
    for index in selected_index_file:
        if index.strip() != '':
            index_set.add(int(index))  
    #print index_set
    print 'start to generate'
    generate_selected_db(g_feature,index_set,sys.argv[2])
    

