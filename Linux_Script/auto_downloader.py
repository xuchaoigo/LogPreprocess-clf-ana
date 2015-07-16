import sys
import os
from os.path import join, getsize 
import string
import MySQLdb
from datetime import *
import time
import struct
import binascii
import shutil
import urllib2
import ConfigParser
import random
import statvfs
import multiprocessing
from multiprocessing import Process
import traceback

def InitCursor(db_server_ip,db_name):
    try:
        MySqlCon=MySQLdb.connect(host=db_server_ip,user='root',passwd='123456',port=3306)  
        MySqlCon.select_db(db_name)
        MySqlCur=MySqlCon.cursor()
        return [MySqlCon,MySqlCur]
    except MySQLdb.Error,e:
        return [0,0]

def UnInitCursor(MySqlCon,MySqlCur):
    MySqlCur.close()
    MySqlCon.commit()
    MySqlCon.close()

def _get_table_list(MySqlCur,DBName):
    cmd="select table_name from information_schema.tables where table_schema='%s'"%(DBName)
    count=MySqlCur.execute(cmd)
    results=MySqlCur.fetchmany(count)
    TableList=[]
    for item in results:
        TableList.append(item[0])
    return TableList 
 
def GetNoDealedMd5s(MySqlCur,TabNameDate):
    limit_num = 50
    cmdqr='select * from %s where CanDownload = 0 limit %d' %(TabNameDate, limit_num) 
    #print cmdqr
    counts = MySqlCur.execute(cmdqr)
    print 'count of nodealed md5s is : ',counts
    current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print current_time
    fetch_count = 50
    if counts < fetch_count:
        fetch_count = counts
    results=MySqlCur.fetchmany(fetch_count)
    md5list = []
    for r in results:
        md5list.append(r[0])
    return md5list
        
def UpdateDownLoadResultToDb(MySqlCon,MySqlCur,TabNameDate,md5,bCanDownLoad,pid):
    starttime = time.clock()
    cmdupdate='update %s set CanDownload = %s where Md5 = \'%s\''%(TabNameDate, bCanDownLoad, md5)
    #print cmdupdate
    MySqlCur.execute(cmdupdate)
    MySqlCon.commit()
    endtime = time.clock()
    print '%d_updat,%s'%(pid,md5)
    #print 'return, update time=',(endtime-starttime)
    
def Downloader(url,SamplePath,md5,pid):
    #pros=["10.52.174.11", "10.52.174.12", "10.52.174.13", "10.52.174.14", "10.52.174.15", "10.52.173.73", "10.52.173.74", "10.52.173.75", "10.52.173.76", "10.52.164.38"]
    pros=["10.52.174.11", "10.52.174.12", "10.52.174.13", "10.52.174.14",  "10.52.173.73", "10.52.173.74", "10.52.173.75", "10.52.164.38"]
    try:
        st = time.time()
        print '%d_httpin,%s,%s'%(pid,md5,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(st)))
        i=random.randint(0, len(pros)-1)
        proxy=pros[i] + ':8081'
        opener = urllib2.build_opener(urllib2.ProxyHandler({'http':proxy}))
        urllib2.install_opener(opener)
        data = urllib2.urlopen(url,timeout=60).read()
        f=file(SamplePath,'wb')
        f.write(data)
        f.close()
        et = time.time()
        print '%d_httpout,%s,%s,%ds,%s'%(pid,md5,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(et)),et-st,pros[i])
    #except urllib2.HTTPError, e:
    except Exception,e:
        et = time.time()
        print '--%d,%s,%s,%s,%ds,%s'%(pid,md5,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(et)),e,et-st,pros[i])
        return
        
def GetBucketName2(md5):
    s = binascii.a2b_hex(md5)
    v = struct.unpack('@IIII', s)
    a = v[0]^v[1]^v[2]^v[3]
    return(a%4000+1)
    
def GetDownLoadUrl(md5):
    buckName=GetBucketName2(md5)
    url='http://bj.bs.bae.baidu.com/sw-sample-%04d/%s'%(buckName,md5)
    return url

def delete_md5(MySqlCon,MySqlCur,table_name,md5,pid):
    del_cmd="delete from %s where Md5='%s'"%(table_name,md5)
    print(del_cmd)
    count=MySqlCur.execute(del_cmd)
    MySqlCon.commit()
    print '%d_delete,%s'%(pid,md5)
        
def download_sample_by_table(table_name,store_dir,db_server_ip,db_name):
    mysql_conn,mysql_cursor= InitCursor(db_server_ip,db_name)
    print 'get sample from %s'%(table_name)
    sample_dir=os.path.join(store_dir,table_name)
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
     
    try:
            max_download_num = 1000
            currect_download_num = 0
            pid = os.getpid()
            while True:
                listmd5s = GetNoDealedMd5s(mysql_cursor,table_name)
                if(len(listmd5s)) <= 0:
                    break
                #xuc: to solve the strange connection lost problem
                #print 'proc %d cur_download_num=%d'%(os.getpid(),currect_download_num)
                currect_download_num += len(listmd5s)
                if currect_download_num >= max_download_num:
                    print 'reset connection,cur_download_num=',currect_download_num
                    currect_download_num = 0
                    UnInitCursor(mysql_conn,mysql_cursor)
                    time.sleep(1)
                    mysql_conn,mysql_cursor = InitCursor(db_server_ip,db_name)            
                    time.sleep(1)

                for md5 in listmd5s:
                    url = GetDownLoadUrl(md5)
                    sample_path =os.path.join(sample_dir,md5) 
                    print '%d_md5=%s'%(pid,md5)
                    Downloader(url, sample_path, md5,pid)
                    if os.path.exists(sample_path):
                        UpdateDownLoadResultToDb(mysql_conn,mysql_cursor,table_name, md5, 1,pid)
                    else:
                        pass
                        #delete_md5(mysql_conn,mysql_cursor,table_name,md5,pid)
                    while True:
                        vfs=os.statvfs('/home')
                        available=vfs[statvfs.F_BAVAIL]*vfs[statvfs.F_BSIZE]/(1024*1024*1024)
                        if(available<20):
                            print 'disk left only %dGB,sleep'%available
                            time.sleep(10*60)
                        else:
                            break
    except Exception,e:
        #UnInitCursor(mysql_conn,mysql_cursor)
        #time.sleep(1)
        #mysql_conn,mysql_cursor = InitCursor(db_server_ip,db_name)
        #time.sleep(1)
        print e
        print traceback.format_exc()
                   
    print 'get sample from %s finished'%table_name 
    UnInitCursor(mysql_conn,mysql_cursor)
    
def download_sample_worker(job_q,result_q,db_server_ip,db_name,store_dir):
    print 'one download_sample_worker begins, process id=%d' %(os.getpid())
    job = ''
    max_print_count = 100
    cur_print_count = 0
    while True:
        try:
            if job=='':
                job = job_q.get_nowait()
            download_sample_by_table(job,store_dir,db_server_ip,db_name)
            result_q.put(job)
            job = ''
        except Exception,e:
            if job_q.empty():
                print 'queue empty, will break'
                break
            else:
                if cur_print_count < max_print_count:
                    cur_print_count += 1
                    print e
                    print traceback.format_exc()
                continue
    print 'one download_sample_worker exit, process id=%d'%(os.getpid())

def run_download_sample(db_server_ip,db_name,nprocs):
    mysql_conn,mysql_cursor = InitCursor(db_server_ip,db_name)
    table_list = _get_table_list(mysql_cursor,db_name)
    UnInitCursor(mysql_conn,mysql_cursor)

    job_q = multiprocessing.Queue()
    result_q = multiprocessing.Queue()
    for table_name in table_list:
        job_q.put(table_name)
    print 'will process %d tables...'%len(table_list)

    store_dir=r'/home/hips/FileServer/download/%s'%db_name
    if not os.path.exists(store_dir):
        os.makedirs(store_dir)
    
    procs = []
    for i in range(nprocs):
        p = Process(target=download_sample_worker,args=(job_q, result_q, db_server_ip, db_name, store_dir))
        procs.append(p)
        p.start()

    jobs_processed = 0
    jobs_to_process=len(table_list)
    while jobs_processed < jobs_to_process:
        processed_job = result_q.get()
        print 'job processed: ',processed_job
        jobs_processed += 1

    print 'all jobs processed'
    for p in procs:
        p.join()
 
    
if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'Usage:%s db_server_ip db_name num_procs'%sys.argv[0]
        sys.exit()
    db_server_ip=sys.argv[1]
    db_name=sys.argv[2]
    num_procs=int(sys.argv[3])
     
    run_download_sample(db_server_ip,db_name,num_procs)
    
