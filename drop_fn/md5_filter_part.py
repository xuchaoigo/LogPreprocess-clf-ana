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
            for name,value in attrs:
                if name == 'href':
                    self.level.append(value[value.rfind('/')+1:])
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
    })

    req=urllib2.Request(
        url='http://cms.iyuntian.com:8000/zpadmin/security/file_multisearch',
        data=postdata
    )
    return req

def save_md5(filter_file,md5_list):
    file_handle=open(filter_file,'w')
    for md5 in md5_list:    
        file_handle.write('%s %s\n'%(md5[0],md5[1]))
    file_handle.close()

def get_database(db_name):
    InitCursor()
    SelectDB(db_name)
    table_list=GetTableList(db_name)
    root_dir='./white_md5'
    if os.path.exists(root_dir):
        return root_dir
    else:
        os.mkdir(root_dir)
    for table_name in table_list:
        table_file=os.path.join(root_dir,table_name)
        md5_list=get_md5_list(table_name)
        file_handle=open(table_file,'w')
        for md5 in md5_list:
            file_handle.write('%s\n'%md5)
        file_handle.close()
    return root_dir

def filter_table(old_file,new_file):
    opener=html_opener()
    html_parser=MyParser()
    old_md5_list=[]
    read_handle=open(old_file,'r')
    for md5 in read_handle:
        old_md5_list.append(md5.strip('\n'))
    read_handle.close()
    begin=0
    end=0
    md5_len=len(old_md5_list)
    print 'total md5 is %d'%md5_len
    filtered_md5={}
    while end<md5_len:
        end=min(end+20,md5_len)
        part_md5_list=old_md5_list[begin:end]
        req=get_req(part_md5_list) 
        query_result=opener.open(req)
        html_parser.feed(query_result.read())
        print html_parser.level
        for i in range((end-begin)/2):
            if html_parser.level[i*2+1] != '100':
                filtered_md5[html_parser.level[i*2]]=html_parser.level[i*2+1]  
        print filtered_md5
        begin=end
        html_parser.level=[]
    save_md5(new_file,filtered_md5_list)
        
def filter_md5(old_dir,new_dir):
    if not os.path.exists(new_dir):
        os.mkdir(new_dir)
    old_file_list=os.listdir(old_dir)
    new_file_list=os.listdir(new_dir)
    for file_name in old_file_list:
        if new_file_list.count(file_name)!=0:
            continue
        new_file=os.path.join(new_dir,file_name)
        old_file=os.path.join(old_dir,file_name)
        print 'process table %s'%file_name
        filter_table(old_file,new_file)
    print 'filter over'
    
def process(db_name,md5_dir):
    #md5_dir=get_database(db_name)
    filter_md5_dir='%s_filter'%md5_dir
    filter_md5(md5_dir,filter_md5_dir)
    

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],' db_name, md5_dir'
        sys.exit()
    process(sys.argv[1],sys.argv[2])
