from __future__ import division  
import os
import ConfigParser
import MySQLdb
import time

Ip=''
User=''
Pwd=''
Port=0
timeout=0
DBName=''

TypeSize=0
TypeList=[]

delimiter_arg=''
delimiter_behavior=''
delimiter_target=''
delimiter_count=''
delimiter_table=''
delimiter_feature=''
delimiter_item=''

ThresholdList=[]
Ngram=0
g_sample_log='Sample/Log'
g_sample_fet='Sample/Fet'
g_sample_table='global'
g_auth_key=''
g_chunk_size=1000
g_vector_dir='Vector'
g_feature_dir='Feature'

MySqlCon=0
MySqlCur=0

# get configuration parameter from config file.

def GetConfig():
    global Ip
    global User
    global Pwd
    global Port
    global timeout
    global DBName

    global TypeSize
    global TypeList

    global delimiter_arg
    global delimiter_behavior
    global delimiter_target
    global delimiter_count
    global delimiter_table
    global delimiter_feature
    global delimiter_item

    global ThresholdList
    global Ngram

    global g_sample_log
    global g_sample_fet
    global g_sample_table
    global g_auth_key
    global g_chunk_size
    global g_vector_dir
    global g_feature_dir

    try:
        cf=ConfigParser.ConfigParser()
        ConfigPath=r'./Config.ini'
        cf.read(ConfigPath)

        TypeSize=cf.getint('Type','TypeSize')
        for i in range(1,TypeSize+1):
            TypeSeq='Type[%d]'%i
            temp=cf.get('Type',TypeSeq)
            TypeList.append(temp)

        DBName=cf.get('Database','DBName')
        Ip=cf.get('SQL','Ip')
        User=cf.get('SQL','User')
        Pwd=cf.get('SQL','Pwd')
        Port=cf.getint('SQL','Port')
        timeout=cf.getint('SQL','timeout')

        delimiter_arg = cf.get('Split','delimiter_arg')
        delimiter_behavior=cf.get('Split','delimiter_behavior')
        delimiter_target=cf.get('Split','delimiter_target')
        delimiter_count=cf.get('Split','delimiter_count')
        delimiter_table=cf.get('Split','delimiter_table')
        delimiter_feature=cf.get('Split','delimiter_feature')
        delimiter_item=cf.get('Split','delimiter_item')

        ThresholdTemp=cf.get('Threshold','Threshold')
        for item in ThresholdTemp.split(','):
            ThresholdList.append(float(item))
        Ngram=cf.getint('Gram','Ngram')
        
        g_sample_log = cf.get('Cluster','sample_log')
        g_sample_fet = cf.get('Cluster','sample_fet')
        g_sample_table = cf.get('Cluster','sample_table')
        g_auth_key = cf.get('Cluster','auth_key')
        g_chunk_size = cf.getint('Cluster','chunk_size')
        g_vector_dir = cf.get('Cluster','vector_dir')
        g_feature_dir = cf.get('Cluster','feature_dir')

        print 'GetConfig success!'
    except:
        print('GetConfig error')
    

#Database operation

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

def SelectDB(database_name):
    global MySqlCon
    global MySqlCur
    MySqlCur.execute('create database if not exists %s'%database_name)
    MySqlCon.select_db(database_name)

def DropDb(database_name):
    global MySqlCur
    MySqlCur.execute('drop database %s'%database_name)

def SelectTab(table_name):
    global MySqlCur
    cratetabcmd='create table if not exists %s(Feature_Index Int,Target varchar(256),BlackHot Int,WhiteHot Int,BlackWidth Int,WhiteWidth Int) character set = utf8'%table_name
    MySqlCur.execute(cratetabcmd)

def AddItemToDb(table_name,feature_index,feature):
    global MySqlCur
    if feature[0].count('"'):
        return
    SelectTab(table_name)
    addcmd='insert ignore into %s(Feature_Index,Target,BlackHot,WhiteHot,BlackWidth,WhiteWidth) values(%d,"%s",%d,%d,%d,%d)'%(table_name,feature_index,feature[0],feature[1],feature[2],feature[3],feature[4])
    MySqlCur.execute(addcmd)
##xuc test start 
def AddIndexToTable_test(table_name):
    global MySqlCur
    cmd='ALTER TABLE %s ADD INDEX index_name1(Md5)'%(table_name)
    MySqlCur.execute(cmd)    

def delete_all_used_md5(table_name):
    global MySqlCur
    global MySqlCon
    
    clean_cnt11=0    
    while 1:
            cmd_query='select * from %s where CanDownLoad=1 and HandleVersion = 0 limit 100'%table_name
            cmd_del='DELETE FROM %s where Md5 = \"%%s\"'%table_name

            count=MySqlCur.execute(cmd_query)
            if count <=0:
                break
            results=MySqlCur.fetchmany(count)
            clean_cnt11+=count
            for r in results:
                cmd_del_real = cmd_del%r[0]
                MySqlCur.execute(cmd_del_real)
                #md5list.append(r[0])
            MySqlCon.commit()
    print 'table:%s  clean 11=%d'%(table_name,clean_cnt11)

"""
    clean_01=0    
    while 1:
            cmd_query='select * from %s where CanDownLoad=1 and HandleVersion = 0 limit 100'%table_name
            cmd_del='DELETE FROM %s where Md5 = \"%%s\"'%table_name

            count=MySqlCur.execute(cmdquery)
            if count <=0:
                break
            results=MySqlCur.fetchmany(count)
            clean_01+=count
            for r in results:
                cmd_del_real = cmd_del%r[0]
                MySqlCur.execute(cmd_del_real)
                #md5list.append(r[0])
            MySqlCon.commit()
    print 'table:%s  clean 11='%(table_name,clean_01)
"""
def delete_table_if_empty(table_name):
    global MySqlCur
    cmd_query='select * from %s'%table_name
    count=MySqlCur.execute(cmd_query)
    if count <=10:
        MySqlCur.execute('drop table %s'%table_name)
        print 'num is %d,drop table %s\n'%(count,table_name)
        return
    print 'num is %d,pass %s\n'%(count,table_name)

def check_table_status(table_name):
    global MySqlCur
    cmd_query_d_and_r='select * from %s where CanDownLoad=1 and HandleVersion = 1'%table_name
    cmd_query_not_run='select * from %s where CanDownLoad=1 and HandleVersion = 0'%table_name
    cmd_query_not_download='select * from %s where CanDownLoad=0 and HandleVersion = 0'%table_name
    cmd_query_all='select * from %s'%table_name
    count_d_and_r=MySqlCur.execute(cmd_query_d_and_r)
    count_not_run=MySqlCur.execute(cmd_query_not_run)
    count_not_download=MySqlCur.execute(cmd_query_not_download)
    count_all=MySqlCur.execute(cmd_query_all)
    return count_d_and_r,count_not_run,count_not_download,count_all

def get_all_db():
    global MySqlCur
    system_db_list=['information_schema','performance_schema','mysql']
    db_list=[]
    db_cmd='show databases'
    count=MySqlCur.execute(db_cmd)
    results=MySqlCur.fetchmany(count)
    for item in results:
        for new_item in item:
            if new_item not in system_db_list:
                db_list.append(new_item)
    return db_list

def get_table_all_num(table_name):
    global MySqlCur
    cmd_query_d_and_r='select * from %s'%table_name
    count_all=MySqlCur.execute(cmd_query_d_and_r)
    return count_all

def just_SelectDB(database_name):
    global MySqlCon
    global MySqlCur
    MySqlCon.select_db(database_name)


##xuc test end
def GetTableList(database_name):
    global MySqlCur
    cmd="select table_name from information_schema.tables where table_schema='%s'"%(database_name)
    count=MySqlCur.execute(cmd)
    results=MySqlCur.fetchmany(count)
    table_list=[]
    for item in results:
        table_list.append(item[0])
    return table_list 
    
def GetAllFet(TabName):
    global MySqlCur
    cmdqr='select * from %s for update'%TabName
    count=MySqlCur.execute(cmdqr)
    results=MySqlCur.fetchmany(count)
    fet_list = []
    for fet in results:
        fet_list.append(fet)
    MySqlCon.commit()
    return fet_list

def SetHandled(TabName):
    global MySqlCon
    global MySqlCur
    cmdupdate='update %s set HandleVersion = 1'%TabName
    MySqlCur.execute(cmdupdate)
    MySqlCon.commit()

def FetchFeature():
    global MySqlCon
    global MySqlCur
    InitCursor()
    g_feature_dict={}   
    SelectDB(DBName)
    TabList=GetTableList(DBName)
    for table in TabList:
        g_feature_dict[table]=[]
        fetchcmd='select * from %s'%table
        count=MySqlCur.execute(fetchcmd)
        results=MySqlCur.fetchmany(count)
        for r in results:
            FeatureTemp=[]
            FeatureTemp.append(r[0])
            FeatureTemp.append(r[1])
            black_width=int(r[4])
            white_width=int(r[5])
            weight=max(black_width,white_width)/(max(min(black_width,white_width),1)) 
            FeatureTemp.append(weight)
            g_feature_dict[table].append(FeatureTemp)   
    MySqlCon.commit()
    UnInitCursor()
    return g_feature_dict



# regular common operaton

def get_readable_time():
    return time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))

def get_table_name(line):
    feature_list = line.split(delimiter_behavior)
    table_list=[]
    for item in feature_list:
        item_list=item.split(delimiter_target)
        table_name='%s_%s'%(item_list[0],item_list[1])
        table_list.append(table_name)
    table_name=table_list[0]
    for i in range(1,len(table_list)):
        table_name='%s$%s'%(table_name,table_list[i]) 
    return table_name 

GetConfig()
