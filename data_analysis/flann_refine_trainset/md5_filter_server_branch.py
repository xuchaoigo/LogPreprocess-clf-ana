import urllib  
import urllib2
import cookielib
import HTMLParser
import os
import sys

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
        
def get_md5_list_from_file(server_branch_result_file,target_level):
    md5_list=[]
    handle = open(server_branch_result_file,'r')
    for line in handle:
        line = line.strip()
        #md5,level,distance
        arg_list = line.split(',')
        if int(arg_list[1]) == target_level:
            md5_list.append((arg_list[0],arg_list[2]))
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

def process(server_branch_result_file):
    opener=html_opener()
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
    vdc_lv100 = 0
    vdc_lv200 = 0
    detected_num = 0
    uniq_report_num = 0
    table_list = ['2015_01_29']
    for table_name in table_list:
        md5_list_lv100=get_md5_list_from_file(server_branch_result_file,100)
        md5_list_lv200=get_md5_list_from_file(server_branch_result_file,200)
        mships_lv100 += len(md5_list_lv100)
        mships_lv200 += len(md5_list_lv200)
        md5_dict_lv100[table_name]=md5_list_lv100
        md5_dict_lv200[table_name]=md5_list_lv200

    print 'mships_lv100=',mships_lv100
    print 'mships_lv200=',mships_lv200
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
                try:
                        i_md5 = 2*i
                        i_lv = 2*i+1    
                        if html_parser.level[i_lv] == '200':
                            filter_md5_dict_lv100[table_name].append([html_parser.level[i_md5],html_parser.level[i_lv]])
                            filter_num_lv200 += 1
                            print 'wrong md5 found ,md5=%s level=%s'%(html_parser.level[i_md5],html_parser.level[i_lv])
                        if html_parser.level[i_lv] == '100' or html_parser.level[i_lv] == '110':
                            vdc_lv100 +=1
                        if html_parser.level[i_lv] == '170' or html_parser.level[i_lv] == '180' or html_parser.level[i_lv] == '190' or html_parser.level[i_lv] == '200': 
                            vdc_lv200 +=1
                        if html_parser.level[i_lv] == '150':
                            uniq_report_num +=1
                except Exception,e:
                    print e
                    print 'i_md5=%d,i_lv=%d'%(i_md5,i_lv)
                    pass
            html_parser.level=[]
            total_num += (end-begin)
            if total_num%500 ==0:
                print 'total process %d'%total_num
            begin=end
    print 'mships lv100=%d,vdc200=%d,vdc100=%d'%(mships_lv100,vdc_lv200,vdc_lv100)
    """
    filter_file='%s_filter'%db_name
    save_md5(filter_file,filter_md5_dict)
    """
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
                try:
                        i_md5 = 2*i
                        i_lv = 2*i+1    
                        #print 'md5=%s level=%s'%(html_parser.level[i_md5],html_parser.level[i_lv])
                        distance = get_distance_from_mysql_list(html_parser.level[i_md5], md5_list_lv200)
                        distance = int(distance)
                        if distance ==142857:
                            print 'MD5 NOT FOUND!'
                        if html_parser.level[i_lv] == '100':
                            if distance != 0 and distance != -1:
                                print 'distance=',distance
                                filter_md5_dict_lv200[table_name].append([html_parser.level[i_md5],html_parser.level[i_lv]])
                                filter_num_lv100 += 1
                                print 'wrong md5 found ,md5=%s level=%s'%(html_parser.level[i_md5],html_parser.level[i_lv])
                        if html_parser.level[i_lv] == '100' or html_parser.level[i_lv] == '110':
                            vdc_lv100 +=1
                        if html_parser.level[i_lv] == '170' or html_parser.level[i_lv] == '180' or html_parser.level[i_lv] == '190' or html_parser.level[i_lv] == '200': 
                            vdc_lv200 +=1
                            if distance != 0 and distance != -1:
                                detected_num += 1
                        if html_parser.level[i_lv] == '150':
                            uniq_report_num +=1
                except Exception,e:
                    print e
                    print 'i_md5=%d,i_lv=%d'%(i_md5,i_lv)
                    pass
            html_parser.level=[]
            total_num += (end-begin)
            if total_num%500 ==0:
                print 'total process %d'%total_num
            begin=end
    print 'mships all=%d,vdc100=%d,vdc200=%d'%(mships_lv200+mships_lv100,vdc_lv100,vdc_lv200)
    
    print 'total fp md5 is :%d'%filter_num_lv100
    print 'mships lv100 num =',mships_lv100
    print 'mships lv200 num =',mships_lv200
    print 'vdc lv100 in mships lv200 num=',filter_num_lv100
    print 'vdc lv200 in mships lv100 num=',filter_num_lv200
    print 'vdc lv100 num =',vdc_lv100
    print 'vdc lv200 num =',vdc_lv200
    print 'detected_num =',detected_num
    print 'uniq_report_num =',uniq_report_num
    print 'fp%=',float(filter_num_lv100)/float(vdc_lv100)
    print 'fn%=',float(filter_num_lv200)/float(vdc_lv200)
    print 'detected%=',float(detected_num)/float(vdc_lv200)
    #print 'fp%=',float(filter_num_lv100)/float(mships_lv200)
    #print 'fn%=',float(filter_num_lv200)/float(mships_lv100)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' result_file(server_branch)'
        sys.exit()
    process(sys.argv[1])
