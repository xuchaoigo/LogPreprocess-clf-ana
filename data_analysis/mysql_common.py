import sys
import os
import string 
#import httplib2
import HTMLParser
import MySQLdb
from  datetime  import  *
import  time
import struct
import binascii
import shutil
import socket
import csv

Ip='nj02-sw-kvmserver01.nj02'
User='root'
Pwd='123456'
Port=3306
DB_NAME='VDC_sample'

def InitDb():
    global MySqlCon
    global MySqlCur
    while 1:
        try:
            MySqlCon=MySQLdb.connect(host=Ip,user=User,passwd=Pwd,port=Port)  
            MySqlCur=MySqlCon.cursor()
            print "connect to db!"
            break
        except MySQLdb.Error,e: 
            print "failed to connect to db!"

def UnInitDb():
        global MySqlCon
        global MySqlCur
        MySqlCur.close()
        MySqlCon.commit()
        MySqlCon.close()

def SelectDb(name):
    global MySqlCon
    global MySqlCur
    createdbcmd='create database if not exists %s'%(name)
    try:
        MySqlCur.execute(createdbcmd)
        MySqlCon.select_db(name)
        #print '###SeleteDb done,cmd=',createdbcmd
    except MySQLdb.Error,e:
        print '###SeleteDb failed,cmd=',createdbcmd

def GetTabName(TimeStamp):
    x=time.localtime(TimeStamp)
    TabName=time.strftime('%Y_%m_%d',x)
    return TabName

def GetTableList(DBName):
    global MySqlCur
    cmd="select table_name from information_schema.tables where table_schema='%s'"%(DBName)
    count=MySqlCur.execute(cmd)
    results=MySqlCur.fetchmany(count)
    TableList=[]
    for item in results:
        TableList.append(item[0])
    return TableList

def AddDbTab(TimeStamp):
    global MySqlCur
    global MySqlTab
    TabName=GetTabName(TimeStamp)
    MySqlTab=TabName
    createtabcmd='create table if not exists %s(Md5 varchar(32) primary key, HandleVersion INT, CanDownload BOOL, Level INT)'%MySqlTab
    try:
        MySqlCur.execute(createtabcmd)
        MySqlCon.commit()
        #print '###AddDbTab done,cmd=',createtabcmd
    except MySQLdb.Error,e:
        print '###AddDbTab failed,cmd=',createtabcmd

def AddItemtoDb(MD5):
    global MySqlCur
    global MySqlTab
    addcmd='insert ignore into %s values(%%s,%%s,%%s,%%s)'%(MySqlTab)
    value=[MD5,0,0,200]
    try:
        MySqlCur.execute(addcmd,value)
        MySqlCon.commit()
        #print '###AddItemtoDb done,cmd=',addcmd
    except MySQLdb.Error,e:
        print '###AddItemtoDb failed,cmd=',addcmd
    
def insert_one_md5(md5):
    AddDbTab(time.time())
    AddItemtoDb(md5)    

def query_one_md5(md5,table_list):
    for table in table_list:
        cmd_query="select * from %s where Md5 = '%s'"%(table,md5)
        count=MySqlCur.execute(cmd_query)
        if count >0:
            result = MySqlCur.fetchone()
            return result[0],result[3]        
        
def insert_to_mysql(md5list):
    InitDb()
    cnt = 0
    SelectDb(DB_NAME)
    for md5 in md5list:
        cnt += 1
        if cnt%1000 == 0:
            print "cnt=  ",(cnt)
        insert_one_md5(md5)
    UnInitDb()
    return

def fetch_from_mysql(md5list):
    InitDb()
    cnt = 0
    result_list=[]
    SelectDb(DB_NAME)
    table_list = GetTableList(DB_NAME)
    print 'table_list = ',table_list
    for md5 in md5list:
        cnt += 1 
        if cnt%1000 == 0:
            print "cnt=  ",(cnt)
        md5, result = query_one_md5(md5,table_list)
        result_list.append((md5,result))
    UnInitDb()
    return result_list
    
def set_predict_result(result_list):
    InitDb()
    SelectDb(DB_NAME)
    table_list = GetTableList(DB_NAME)
    print 'update %d results..'%(len(result_list))
    for md5,level in result_list:
        for table in table_list:
            cmd_update="update %s set Level = %s where Md5 = '%s'"%(table,level,md5)
            count=MySqlCur.execute(cmd_update)
            MySqlCon.commit()




