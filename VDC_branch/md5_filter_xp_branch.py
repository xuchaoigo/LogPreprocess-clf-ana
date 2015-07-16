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
        HTMLParser.HTMLParser.__init__(self)
        self.first=0
        self.second=0
        self.md5=0
        self.level=[]

    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.first=1
            self.md5=1
        if tag == 'td' and self.first ==1:
            self.second = 1
            self.first=0

    def handle_data(self, data):
        if self.md5:
            #print 'md5=',data
            self.level.append(data)
            self.md5=0
         
        if self.second: 
            HTMLParser.HTMLParser.handle_data(self, data)
            self.second=0
            #print 'level=',data
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

def get_md5_list(table_name,level):
    global MySqlCur
    md5_list=[]
    fetchcmd='select * from %s where Level = %d'%(table_name,level)
    print fetchcmd
    count=MySqlCur.execute(fetchcmd)
    results=MySqlCur.fetchmany(count)
    for r in results:
        md5_list.append((r[0],r[4]))
    return md5_list

def html_opener():
    cookie = cookielib.CookieJar()  
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    postdata=urllib.urlencode({  
        'username':'karlxu',
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
    for md5,distance in md5_list:
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

def get_distance_from_mysql_list(target_md5,mysql_list):
    for md5,distance in mysql_list:
        if md5 == target_md5:
            return float(distance)
    return 142857

def distance_large_enough(distance):
    if distance < -2:
        return True
    else:
        return False

def process(db_name):
    opener=html_opener()
    InitCursor()
    SelectDB(db_name)
    html_parser=MyParser()
    filter_num_lv100 = 0
    filter_num_lv200 = 0
    total_num=0
    md5_dict_lv100={}
    md5_dict_lv200={}
    filter_md5_dict_lv100={}
    filter_md5_dict_lv200={}
    mships_lv100 = 0
    mships_lv200 = 0
    vdc_white = 0
    vdc_black = 0
    vdc_lv200_pure = 0
    detected_black_num = 0
    detected_lv200_num = 0
    uniq_report_white = 0
    uniq_report_black = 0
    table_list=GetTableList(db_name)
    for table_name in table_list:
        md5_list_lv100=get_md5_list(table_name,100)
        md5_list_lv200=get_md5_list(table_name,200)
        mships_lv100 += len(md5_list_lv100)
        mships_lv200 += len(md5_list_lv200)
        md5_dict_lv100[table_name]=md5_list_lv100
        md5_dict_lv200[table_name]=md5_list_lv200
    UnInitCursor()

    print 'lv100=',mships_lv100
    print 'lv200=',mships_lv200
    print 'begin filtering lv100'
    for table_name in md5_dict_lv100:
        filter_md5_dict_lv100[table_name]=[]
        begin=0
        end=0
        table_md5_num=len(md5_dict_lv100[table_name])
        while begin < table_md5_num:
            end=min(end+20,table_md5_num)
            md5_list_lv100=md5_dict_lv100[table_name][begin:end]
            req=get_req(md5_list_lv100)
            query_result=opener.open(req)
            html_parser.feed(query_result.read())
            for i in range(end-begin):
                i_md5 = 2*i
                i_lv = 2*i+1    
                if html_parser.level[i_lv] == '170' or html_parser.level[i_lv] == '180' or html_parser.level[i_lv] == '190' or html_parser.level[i_lv] == '200': 
                    vdc_black +=1
                    filter_md5_dict_lv100[table_name].append([html_parser.level[i_md5],html_parser.level[i_lv]])
                    filter_num_lv200 += 1
                    print 'wrong md5 found ,md5=%s level=%s'%(html_parser.level[i_md5],html_parser.level[i_lv])
                if html_parser.level[i_lv] == '100' or html_parser.level[i_lv] == '110':
                    vdc_white +=1
                if html_parser.level[i_lv] == '200': 
                    vdc_lv200_pure +=1
                if html_parser.level[i_lv] == '150':
                    uniq_report_white +=1
            html_parser.level=[]
            total_num += (end-begin)
            if total_num%500 ==0:
                print 'total process %d'%total_num
            begin=end
    print 'mships lv100=%d, contains: vdc black=%d,vdc white=%d'%(mships_lv100,vdc_black,vdc_white)
    """
    filter_file='%s_filter'%db_name
    save_md5(filter_file,filter_md5_dict)
    """
    #md5_dict_lv200={}
    #md5_dict_lv200['aaa']=['00090c7f00db325d3634f3f2125b746b','00073218d7f8736bb09274b6eebb17ee','0211d43410fa627e7ea952d13ec7b65f']
    print 'begin filtering lv200'
    for table_name in md5_dict_lv200:
        filter_md5_dict_lv200[table_name]=[]
        begin=0
        end=0
        table_md5_num=len(md5_dict_lv200[table_name])
        while begin < table_md5_num:
            end=min(end+20,table_md5_num)
            md5_list_lv200=md5_dict_lv200[table_name][begin:end]
            req=get_req(md5_list_lv200)
            query_result=opener.open(req)
            html_parser.feed(query_result.read())
            for i in range(end-begin):
                i_md5 = 2*i
                i_lv = 2*i+1    
                #print 'md5=%s level=%s'%(html_parser.level[i_md5],html_parser.level[i_lv])
                distance = get_distance_from_mysql_list(html_parser.level[i_md5], md5_list_lv200)
                if distance ==142857:
                    print 'MD5 NOT FOUND!'
                if html_parser.level[i_lv] == '100' or html_parser.level[i_lv] == '110':
                    vdc_white +=1
                    if distance_large_enough(distance):
                        print 'distance=',distance
                        filter_md5_dict_lv200[table_name].append([html_parser.level[i_md5],html_parser.level[i_lv]])
                        filter_num_lv100 += 1
                        print 'wrong md5 found ,md5=%s level=%s'%(html_parser.level[i_md5],html_parser.level[i_lv])
                if html_parser.level[i_lv] == '170' or html_parser.level[i_lv] == '180' or html_parser.level[i_lv] == '190' or html_parser.level[i_lv] == '200': 
                    vdc_black +=1
                    if distance_large_enough(distance):
                        detected_black_num += 1
                if html_parser.level[i_lv] == '150':
                    if distance_large_enough(distance):
                        uniq_report_black +=1
                if html_parser.level[i_lv] == '200': 
                    vdc_lv200_pure +=1
                    if distance_large_enough(distance):
                        detected_lv200_num += 1
            html_parser.level=[]
            total_num += (end-begin)
            if total_num%500 ==0:
                print 'total process %d'%total_num
            begin=end

    print 'mships all=%d,contains: vdc_white=%d,vdc_black=%d'%(mships_lv200+mships_lv100,vdc_white,vdc_black)
    print 'total fp md5 is :%d'%filter_num_lv100
    print 'mships lv100 num =',mships_lv100
    print 'mships lv200 num =',mships_lv200
    print 'vdc white in mships lv200 num=',filter_num_lv100
    print 'vdc black in mships lv100 num=',filter_num_lv200
    print 'vdc white num =',vdc_white
    print 'vdc black num =',vdc_black
    print 'vdc lv200_pure num =',vdc_lv200_pure
    print 'detected_black_num=',detected_black_num
    print 'detected_lv200_num =',detected_lv200_num
    print 'uniq_report_black =',uniq_report_black
    print 'uniq_report_white =',uniq_report_white
    print 'fp%=',float(filter_num_lv100)/float(vdc_white)
    print 'fn%=',float(filter_num_lv200)/float(vdc_black)
    print 'detected%=',float(detected_black_num)/float(vdc_black)
    print 'trojan detected%=',float(detected_lv200_num)/float(vdc_lv200_pure)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' db_name'
        sys.exit()
    process(sys.argv[1])
