import urllib  
import urllib2
import cookielib
import MySQLdb
import HTMLParser
import os
import sys

global MySqlCon
global MySqlCur

class MyParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.first=0
        self.second=0
        self.level=[]
        HTMLParser.HTMLParser.__init__(self)

    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.first=1
        if tag == 'td' and self.first ==1:
            self.second = 1
            self.first=0

    def handle_data(self, data):  
        if self.second: 
            HTMLParser.HTMLParser.handle_data(self, data)
            self.second=0
            self.level.append(data)

def InitCursor():
    global MySqlCon
    global MySqlCur
    db_ip='nj02-sw-kvmserver01.nj02'
    User='root'
    Pwd='123456'
    Port=3306
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

def SelectTab(TabName):
    global MySqlCur
    cratetabcmd='create table if not exists %s(Feature_Index Int,Target varchar(256)) character set = utf8'%TabName
    MySqlCur.execute(cratetabcmd)

def AddItemToDb(TabName,Feature_Index,Target):
    global MySqlCur
    if Target.count('"'):
        return
    SelectTab(TabName)
    addcmd='insert ignore into %s(Feature_Index,Target) values(%d,"%s")'%(TabName,Feature_Index,Target)
    if Feature_Index%500==0:
        print 'insert:',Feature_Index
    
    MySqlCur.execute(addcmd)
 
def GetTableList(DBName):
    global MySqlCur
    cmd="select table_name from information_schema.tables where table_schema='%s'"%(DBName)
    count=MySqlCur.execute(cmd)
    results=MySqlCur.fetchmany(count)
    TableList=[]
    for item in results:
        TableList.append(item[0])
    return TableList

def get_md5_list(table_name):
    global MySqlCur
    md5_list=[]
    fetchcmd='select * from %s'%table_name
    count=MySqlCur.execute(fetchcmd)
    results=MySqlCur.fetchmany(count)
    for r in results:
        md5_list.append(r[0])
    return md5_list

def html_opener():
    cookie = cookielib.CookieJar()  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    postdata=urllib.urlencode({  
        'username':'i_tigerlu',
        'password':'123@ABC',
        'login_type':'domain',
        'url':'',
        'headto':'0'
    })
    req = urllib2.Request(  
        url = 'http://cms.iyuntian.com:8000/zpadmin/admin/login_info',  
        data = postdata
    )

    opener.open(req)
    return opener
    
def get_req(md5_list):
    md5_string=''
    for md5 in md5_list:
        md5_string='%s\n%s'%(md5_string,md5)
    postdata=urllib.urlencode({
        'opt':'0',
        'md5':md5_string,
        'attr[main_level]':'main_level',
        'attr[digi_sign]':'digi_sign'
    })

    req=urllib2.Request(
        url='http://cms.iyuntian.com:8000/zpadmin/security/file_multisearch',
        data=postdata
    )
    return req

def save_md5(filter_file,md5_dict):
    file_handle=open(filter_file,'w')
    for table_name in md5_dict:
        file_handle.write('[%s]\n'%table_name)
        for md5 in md5_dict[table_name]:
            file_handle.write('%s %s\n'%(md5[0],md5[1]))
    file_handle.close()

def process(db_name):
    opener=html_opener()
    html_parser=MyParser()
    InitCursor()
    SelectDB(db_name)
    table_list=GetTableList(db_name)
    filter_num = 0
    total_num=0
    md5_dict={}
    filter_md5_dict={}
    for table_name in table_list:
        md5_list=get_md5_list(table_name)
        md5_dict[table_name]=md5_list
    UnInitCursor()

    print 'begin filtering md5'
    for table_name in md5_dict:
        filter_md5_dict[table_name]=[]
        begin=0
        end=0
        table_md5_num=len(md5_dict[table_name])
        while begin < table_md5_num:
            end=min(end+20,table_md5_num)
            md5_list=md5_dict[table_name][begin:end]
            bad_md5_list=[]
            req=get_req(md5_list)
            query_result=opener.open(req)
            html_parser.feed(query_result.read())
            for i in range(end-begin):
                if html_parser.level[i] != '100':
                    filter_md5_dict[table_name].append([md5_list[i],html_parser.level[i]])
                    filter_num += 1
                    print 'wrong md5 found ,md5=%s level=%s'%(md5_list[i],html_parser.level[i])
            html_parser.level=[]
            total_num += (end-begin)
            if total_num%500 ==0:
                print 'total process %d'%total_num
            begin=end

    print 'total filtered md5 is :%d'%filter_num
    filter_file='%s_filter'%db_name
    save_md5(filter_file,filter_md5_dict)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' db_name'
        sys.exit()
    process(sys.argv[1])
