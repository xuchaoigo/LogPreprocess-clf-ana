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
    DBName='GlobalFeature7'
    
    if len(sys.argv)!=2:
        print 'usage: python  G.py  fet_index'
        return  
    InitCursor()
    SelectDB(DBName)
    TabList=GetTablist(DBName)
    #print TabList
    for TabName in TabList:
        cmd="select * from %s where Feature_Index=%d"%(TabName,int(sys.argv[1]))
        #print cmd
        ret=MySqlCur.execute(cmd)
        #print 'ret=',ret
        
        if ret!=0:
            result=MySqlCur.fetchmany(1)
            print '->  -%s#%s-'%(TabName.replace('_','#'),result[0][0])
            break

    UnInitCursor()   


GetFet()
