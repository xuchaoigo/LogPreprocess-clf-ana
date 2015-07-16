import urllib  
import urllib2
import cookielib
import HTMLParser
import os
import sys
import traceback

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
    #return True
    #if int(density_list[6]) <= 8:
    #    return False
    #if int(quality_list[1])-int(quality_list[0]) >= 20:
    #    return False

    if distance < -3:
        return True
    else:
        return False

def process(server_branch_result_file):
    filter_num_lv100 = 0
    total_num=0
    mships_lv100 = 0
    mships_lv200 = 0
    vdc_white = 0
    vdc_black = 0
    vdc_lv200_pure = 0
        
    md5_list_lv200=get_md5_list_from_file(server_branch_result_file,200)
    md5_list_lv100=get_md5_list_from_file(server_branch_result_file,100)
    vdc_white = len(md5_list_lv100)+len(md5_list_lv200)

    print 'begin filtering lv200'
    for i in range(len(md5_list_lv200)):
        distance,quality_string = float(md5_list_lv200[i][1]),md5_list_lv200[i][2]
        if distance_large_enough(distance,quality_string):
            print 'distance=',distance
            filter_num_lv100 += 1
            print 'wrong md5 found ,md5=%s'%(md5_list_lv200[i][0])
                
    print 'total fp md5 is :%d'%filter_num_lv100
    print 'vdc white in mships lv200 num=',filter_num_lv100
    print 'vdc white num =',vdc_white
    print 'fp%=',float(filter_num_lv100)/float(vdc_white)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' result_file(server_branch)'
        sys.exit()
    process(sys.argv[1])
