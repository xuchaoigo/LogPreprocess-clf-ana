# -*- coding: cp936 -*-
import os
import sys
import string
import os,time
import MySQLdb

MySqlCon=0
MySqlCur=0
Ip='127.0.0.1'
User='root'
Pwd='gfhjkm'
Port=3306
timeout=30
DBName=''

def InitCursor():
    global MySqlCon
    global MySqlCur
    try:
            MySqlCon=MySQLdb.connect(host=Ip,user=User,passwd=Pwd,port=Port)  
            MySqlCur=MySqlCon.cursor()
            return True
    except MySQLdb.Error,e:
            return False
def UnInitCursor():
    global MySqlCon
    global MySqlCur
    MySqlCur.close()
    MySqlCon.commit()
    MySqlCon.close()

def SelectDB(DBName):
    global MySqlCon
    global MySqlCur
    MySqlCon.select_db(DBName)	

def GetTablist(DBName):
    global MySqlCon
    global MySqlCur    
    cmd="select table_name from information_schema.tables where table_schema='%s'"%(DBName)
    count=MySqlCur.execute(cmd)
    results=MySqlCur.fetchmany(count)
    TableList=[]
    for item in results:
        TableList.append(item[0])
    return TableList


def GetFet():
    DBName='GlobalFeature5'
    
    InitCursor()
    SelectDB(DBName)
    TabList=GetTablist(DBName)
    Input=[3,4,5,6,7,8,9,10,11,12,13,14,15,16,20,21,26,28,39,140,945,946,947,948,1292,1293,1294,1295,1296,1297,1298,1299,1300,1301,1306,1308,1314,2454,2455,2456,2457,2459,2460,2462,2465,2466,2467,2468,2470,2475,2479,2480,2482,2490,2535,2566,2635,2636,3636,15016,15017,15018,15020,15023,15027,15028,15030,15036,15043,15052,18454,18455,18456,18457,18458,18461,18465,18466,18467,18468,18473,18476,18479,18480,18484,18488,18501,18510,18555,18600,18650,18699,18700,19942,32007,32009,32012,32019,32023,32025,32041,32042,32186,36657,36659,36662,36669,36673,36675,36676,36692,36693,36836,41337,41342,41349,41350,41362,43182,43183,43184,43185,43186,43187,43188,43196,43197,43797,43798,43801,43802,43804,43805,43822,43869,44007,62087,62088,62092,62093,62321,62322,62323,62324,62329,62333,62344,75524,75525,75528,75529,75643,75644,75647,75648,75651,75652,78270,78272,78277,80529,80530,86405,94789,94790,94791,94792,94793,95503,95504,95505,95506,95507,96262,96263,96269,96270,96833,96835,96836,96838,97004,97008,97239,97245];
    print 'num=',len(Input)
    for index in Input:
        for TabName in TabList:
            cmd="select * from %s where Feature_Index=%d"%(TabName,index)
            ret=MySqlCur.execute(cmd)
            if ret!=0:
                result=MySqlCur.fetchmany(1)
                #old mysql item format
                #print '->  %s#%s'%(TabName.replace('_','#'),result[0][0])
                print '->  %s#%s (%d,%d)'%(TabName.replace('_','#'),result[0][1][:-1],result[0][2],result[0][3])
                break

    UnInitCursor()   


GetFet()
