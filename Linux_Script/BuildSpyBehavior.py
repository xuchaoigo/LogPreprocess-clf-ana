# -*- coding: cp936 -*-
from __future__ import division  
import os
import sys
import string
import os,time
import MySQLdb
import time
#from common import *

g_Ip='127.0.0.1'
g_User='root'
g_Pwd='gfhjkm'
g_Port=3306
g_NewDB='GlobalFeature5Test'
MySqlCon=0
MySqlCur=0

def InitCursor():
    global MySqlCon
    global MySqlCur
    try:
            MySqlCon=MySQLdb.connect(host=g_Ip,user=g_User,passwd=g_Pwd,port=g_Port)  
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
    MySqlCur.execute('create database if not exists %s'%DBName)
    MySqlCon.select_db(DBName)


def GetTableList(DBName):
        global MySqlCon
        global MySqlCur
        cmd="select table_name from information_schema.tables where table_schema='%s'"%(DBName)
        #print(cmd)
        count=MySqlCur.execute(cmd)
        results=MySqlCur.fetchmany(count)
        TableList=[]
        for item in results:
                TableList.append(item[0])
        return TableList

def FetchFeature():
        global MySqlCon
        global MySqlCur
        WriteHandle=open('spy_behavior.log','w')
        SelectDB(g_NewDB)
        TabList=GetTableList(g_NewDB)
        for table in TabList:
                fetchcmd='select * from %s'%table
                count=MySqlCur.execute(fetchcmd)
                results=MySqlCur.fetchmany(count)
                for r in results:
                        if (r[3]>0 and r[2]>500 and r[2]/r[3]>80):
                                spy_behavior = table+'#'+r[1]
                                spy_behavior = spy_behavior.replace('_','#')
                                #WriteHandle.write('%s %s %d %d\n'%(table,r[1],r[2],r[3]))
                                WriteHandle.write(spy_behavior)
        MySqlCon.commit()
        WriteHandle.close()


def Process():
    InitCursor()
    FetchFeature()
    UnInitCursor()

Process()
