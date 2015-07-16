import os
import ConfigParser
import MySQLdb
import time

User=''
Pwd=''
Port=0
timeout=0

TypeSize=0
TypeList=[]

delimiter_arg=''
delimiter_behavior=''
delimiter_target=''
delimiter_count=''
delimiter_table=''
delimiter_feature=''
delimiter_item =''
delimiter_table_name=''

ThresholdList=[]
g_sample_log='Sample/Log'
g_sample_fet='Sample/Fet'
g_auth_key=''
g_chunk_size=100
g_vector_dir='Vector'
g_feature_dir='Feature'
g_sample_table=''
g_server_password=''

MySqlCon=0
MySqlCur=0

# get configuration parameter from config file.

def GetConfig():
    global User
    global Pwd
    global Port
    global timeout

    global TypeSize
    global TypeList

    global delimiter_arg
    global delimiter_behavior
    global delimiter_target
    global delimiter_count
    global delimiter_table
    global delimiter_feature
    global delimiter_item
    global delimiter_table_name

    global ThresholdList

    global g_sample_log
    global g_sample_fet
    global g_auth_key
    global g_chunk_size
    global g_vector_dir
    global g_feature_dir
    global g_merged_fet_dir
    global g_sample_table
    global g_server_password	

    try:
        cf=ConfigParser.ConfigParser()
        ConfigPath=r'./Config.ini'
        cf.read(ConfigPath)

        TypeSize=cf.getint('Type','TypeSize')
        for i in range(1,TypeSize+1):
            TypeSeq='Type[%d]'%i
            temp=cf.get('Type',TypeSeq)
            TypeList.append(temp)

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
        delimiter_table_name=cf.get('Split','delimiter_table_name')
        print delimiter_behavior
        print delimiter_count
        print delimiter_table
        print delimiter_feature
        print delimiter_item

        ThresholdTemp=cf.get('Threshold','Threshold')
        for item in ThresholdTemp.split(','):
            ThresholdList.append(float(item))
        
        g_sample_log = cf.get('Cluster','sample_log')
        g_sample_fet = cf.get('Cluster','sample_fet')
        g_auth_key = cf.get('Cluster','auth_key')
        g_chunk_size = cf.getint('Cluster','chunk_size')
        g_vector_dir = cf.get('Cluster','vector_dir')
        g_feature_dir = cf.get('Cluster','feature_dir')
        g_sample_table = cf.get('Cluster','sample_table')
        g_server_password = cf.get('Cluster','server_password')

        print 'GetConfig success!'
    except:
        print('GetConfig error')
    

#Database operation

def InitCursor(db_ip):
    global MySqlCon
    global MySqlCur
    try:
            MySqlCon=MySQLdb.connect(host=db_ip,user=User,passwd=Pwd,port=Port)  
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

def DropDb(DBName):
    global MySqlCur
    MySqlCur.execute('drop database %s'%DBName)

def SelectTab(TabName):
    global MySqlCur
    cratetabcmd='create table if not exists %s(Feature_Index Int PRIMARY KEY,Target varchar(256)) character set = utf8'%TabName
    MySqlCur.execute(cratetabcmd)

def AddItemToDb(TabName,Feature_Index,Target):
    global MySqlCur
    if Target.count('"'):
        return
    SelectTab(TabName)
    addcmd='insert ignore into %s(Feature_Index,Target) values(%d,"%s")'%(TabName,Feature_Index,Target)
    MySqlCur.execute(addcmd)
    MySqlCon.commit()
 
def GetTableList(DBName):
    global MySqlCur
    cmd="select table_name from information_schema.tables where table_schema='%s'"%(DBName)
    count=MySqlCur.execute(cmd)
    results=MySqlCur.fetchmany(count)
    TableList=[]
    for item in results:
        TableList.append(item[0])
    return TableList 
    
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

def FetchFeature(db_ip,db_name):
    global MySqlCon
    global MySqlCur
    InitCursor(db_ip)
    g_feature_dict={}   
    SelectDB(db_name)
    TabList=GetTableList(db_name)
    print 'get %d tables'%len(TabList)
    cnt = 0
    for table in TabList:
        g_feature_dict[table]=[]
        fetchcmd='select * from %s'%table
        count=MySqlCur.execute(fetchcmd)
        results=MySqlCur.fetchmany(count)
        for r in results:
            cnt+=1
            FeatureTemp=[]
            FeatureTemp.append(r[0])
            FeatureTemp.append(r[1])
            FeatureTemp.append(r[2])
            FeatureTemp.append(r[3])
            g_feature_dict[table].append(FeatureTemp)   
    MySqlCon.commit()
    UnInitCursor()
    print 'Fetch %d Features'%cnt
    return g_feature_dict



# regular common operaton

def get_readable_time():
    return time.strftime('%m-%d %H:%M:%S',time.localtime(time.time()))
"""
#use in itr F.
def get_table_name(line):
    feature_list = line.split(delimiter_behavior)
    table_list=[]
    for item in feature_list:
        item_list=item.split(delimiter_target)
        table_name='%s_%s'%(item_list[0],item_list[1])
        arg_list=item_list[2].split(delimiter_arg)

        #xuc: partition large tables(REGISTRY/FILE) into small tables.
        if len(arg_list)>=2:
            if item_list[0]=='1':   #1_x, REGISTRY
                if 'REGISTRY'== arg_list[0]: 
                    if 'MACHINE' == arg_list[1]:
                        table_name_extend='MACHINE'
                    elif 'USER' == arg_list[1]:
                        table_name_extend='USER'
                    else:
                        table_name_extend='OTHERREG'
                else:
                    table_name_extend='STRANGEREG'
            elif item_list[0]=='2':  #2_x, FILE
                if 'Documents and Settings' == arg_list[0]:
                    table_name_extend='DOCUM'
                elif 'WINDOWS'== arg_list[0]:
                    table_name_extend='WIN'
                elif 'Program Files' == arg_list[0]:
                    table_name_extend='PROGRAM'
                else:
                    table_name_extend="OTHERFILE"
            else:
                table_name_extend="ALL"
        else:
            table_name_extend="ALL"

        #print 'table_name=',table_name
        #print 'table_name_ex=',table_name_extend
        table_name=table_name+"_"+table_name_extend
        table_list.append(table_name)
    table_name=table_list[0]
    for i in range(1,len(table_list)):
        table_name='%s%s%s'%(table_name,delimiter_table_name,table_list[i]) 
    return table_name 
"""
#use in itr G
def get_table_name(line):
    feature_list = line.split(delimiter_behavior)
    table_list=[]
    for item in feature_list:
        item_list=item.split(delimiter_target)
        table_name='%s_%s'%(item_list[0],item_list[1])
        arg_list=item_list[2].split(delimiter_arg)

        #xuc: partition large tables(REGISTRY/FILE) into small tables.
        if len(arg_list)>=5:
            if item_list[0]=='1':   #1_x, REGISTRY
                if 'REGISTRY'== arg_list[0]: 
                    if 'MACHINE' == arg_list[1]:
                        if 'SOFTWARE' == arg_list[2]:
                            if 'Classes' == arg_list[3]:
                                if 'CLSID' == arg_list[4]:
                                    table_name_extend='MSCC'
                                else:
                                    table_name_extend='MSCO'
                            elif 'Microsoft' == arg_list[3]:
                                table_name_extend='MSM'
                            else:
                                table_name_extend='MSO'
                        elif 'SYSTEM' == arg_list[2]:
                            table_name_extend='MY'
                        else:
                            table_name_extend='MO'
                    elif 'USER' == arg_list[1]:
                        table_name_extend='U'
                    else:
                        table_name_extend='O'
                else:
                    table_name_extend='X'
            elif item_list[0]=='2':  #2_x, FILE
                if 'Documents and Settings' == arg_list[0]:
                    if 'Local Settings'== arg_list[1]:
                        table_name_extend='DL'
                    else:
                        table_name_extend='DO'
                elif 'WINDOWS'== arg_list[0]:
                    table_name_extend='W'
                elif 'Program Files' == arg_list[0]:
                    table_name_extend='P'
                else:
                    table_name_extend="O"
            else:
                table_name_extend="A"
        else:
            table_name_extend="A"

        #print 'table_name=',table_name
        #print 'table_name_ex=',table_name_extend
        table_name=table_name+"_"+table_name_extend
        table_list.append(table_name)
    table_name=table_list[0]
    for i in range(1,len(table_list)):
        table_name='%s%s%s'%(table_name,delimiter_table_name,table_list[i]) 
    return table_name 

GetConfig()
