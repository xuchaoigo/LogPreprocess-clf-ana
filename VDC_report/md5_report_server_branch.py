import os
import sys
import traceback
from  vdcclient import *

def get_md5_list_from_file(server_branch_result_file,target_level):
    md5_list=[]
    handle = open(server_branch_result_file,'r')
    for line in handle:
        line = line.strip()
        #md5,level,distance,strangeNB,density(list shaped string)
        arg_list = line.split(',')
        if int(arg_list[1]) == target_level:
            md5_list.append((arg_list[0],arg_list[2],arg_list[3]))
    return md5_list

def get_param_from_mysql_list(target_md5,mysql_list):
    for param in mysql_list:
        if param[0] == target_md5:
            return float(param[1]),param[2]
    return 142857

def distance_large_enough(distance,quality_string):
    quality_list= quality_string.split('/')
    #if int(density_list[6]) <= 8:
    #    return False
    if int(quality_list[1])-int(quality_list[0]) >= 12:
        return False

    if distance < -1:
        return True
    else:
        return False

def process(server_branch_result_file):
    filter_num_lv100 = 0
    filter_num_lv200 = 0
    total_num=0
    md5_dict_lv100={}
    md5_dict_lv200={}
    mships_lv100 = 0
    mships_lv200 = 0
    table_list = ['dontcare']
    md5_result_list = []
    for table_name in table_list:
        md5_list_lv100=get_md5_list_from_file(server_branch_result_file,100)
        md5_list_lv200=get_md5_list_from_file(server_branch_result_file,200)
        mships_lv100 += len(md5_list_lv100)
        mships_lv200 += len(md5_list_lv200)
        md5_dict_lv100[table_name]=md5_list_lv100
        md5_dict_lv200[table_name]=md5_list_lv200

    print 'mships_lv100=',mships_lv100
    print 'mships_lv200=',mships_lv200
    print 'begin filtering lv100'
    for table_name in md5_dict_lv100:
        for md5info in md5_dict_lv100[table_name]:
        #('ff225be5f75071e9fd77a522e85f38ee', '0.643585', '3/11')
            md5_result_list.append((md5info[0],100))    
    print 'begin filtering lv200'
    for table_name in md5_dict_lv200:
        for md5info in md5_dict_lv200[table_name]:
            distance = float(md5info[1])
            quality_string = md5info[2]
            if distance_large_enough(distance,quality_string):
                md5_result_list.append((md5info[0],200))    
            else:
                md5_result_list.append((md5info[0],100))    
    
    ip = '10.52.176.32'
    request_port = 20069
    report_port = 23611
    timeout = 10
    client = VDCClient()
    print 'start commit, %d md5 result'%(len(md5_result_list))
    cnt = 1
    for md5info in md5_result_list:
    #('ff784c063a6b7780e2ad4f87a23f52cd', 100)
        if cnt%500==0:
            print 'commit %d md5'%cnt
        if int(md5info[1])==200:
            client.send_response(ip,report_port,timeout, md5info[0], 200, 'trojan')
        elif int(md5info[1])==100:
            client.send_response(ip,report_port,timeout, md5info[0], 100, 'white')
        else:
            print '\n\nERROR!\n',md5info       
        cnt+=1       

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' result_file(server_branch)'
        sys.exit()
    process(sys.argv[1])
