#!/bin/env python
#coding=utf8
import sys
import os
import time 
import socket
import traceback
from optparse import OptionParser
import binascii
from proto_head import *
from proto import *
from mysql_common import *
import redis

import urllib  
import urllib2
import cookielib
import HTMLParser

ENGINE_NAME='HIPS'
PLATFORM_NAME='windows'
HIPS_LEVEL_WHITE=100
HIPS_LEVEL_BLACK=200
HIPS_LEVEL_NOT_HANDLE=0
VDC_LEVEL_WHITE=100
VDC_LEVEL_BLACK=200
VDC_LEVEL_GRAY=150

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

def get_req(md5):
    #print 'get_req:',md5
    req=urllib2.Request(
        url='http://cms.iyuntian.com:8000/zpadmin/security/file_list/%s'%md5,
    )
    return req

class VDCClient(object):

    CMD_VDC_ENGINE = 176 #dispatch pull task
    CMD_FC_SCAN_REPORT = 171 #detect report result

    def __init__(self,):
        #self.cache = easyDB.get_redis_handler(settings.CacheServer)
        self.cache = redis.Redis(host='localhost', port=6379, db=1)               

    def _build_dispatch_request_packet(self, last_get_time,task_num):
        pkg = EngineTaskReqBody()                        
        ######################
        pkg.task_num = int(task_num)#settings.VDCClient.request_task_num
        
        pkg.engine_name = ENGINE_NAME# settings.VDCClient.engine_name
        pkg.engine_name_len = len(pkg.engine_name)#len(settings.VDCClient.engine_name)

        pkg.platform_name = PLATFORM_NAME#settings.VDCClient.platform_name
        pkg.platform_name_len = len(pkg.platform_name)#len(settings.VDCClient.platform_name)

        pkg.prev_get_time = last_get_time
        ###########################
        head_pkg = SQPkgHead() 
        head_pkg.cmd = VDCClient.CMD_VDC_ENGINE

        head_a_pkg = SQAppendPkgHead()

        return ProtoPkg.encode(head_pkg, head_a_pkg, pkg)

    def _send_and_recv(self, ip, port, timeout, send_buf):
        if send_buf is None:
            return None
        #print ("_send_and_recv")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)       
        s.settimeout(int(timeout))
        try:
            s.sendto(send_buf, (ip, port))
            #print("sendto vdc: ip=%s, len=%d" % (ip, len(send_buf)))
            recv_buf, addr = s.recvfrom(65536)
            #print("recv from vdc: addr=%s, len=%d" % (str(addr), len(recv_buf)))
            return recv_buf
        except socket.timeout:    
            print("recv timeout,",timeout)
            return None

        return None

    def _parse_task_response(self, response):
        _time = time.time()
        task_list = []
        if 0 == response.task_num:
            print("vdc has no task now.")
            return _time, task_list

        for task in response.task_info:
            md5 = binascii.b2a_hex(task.md5)
            task_list.append(md5)

            key = self._get_key_of_md5_info(md5)
            val = struct.pack("!I16sBIHHHQQB16s", task.seq, task.md5, task.md5_type, task.file_size, task.app_id, task.sub_app_id, task.scan_src_id, task.recv_time, task.disp_time, task.new_upload, task.reserved)
            self.cache.set(key, val) 
            #print 'set:',md5           
            #NOTE: TEST STAGE, no expiration 
            #self.cache.expire(key, settings.Dispatcher.vdc_server_timeout * 2)

        return _time, task_list

    def request_task(self, last_get_time,task_host,task_port,timeout,batch_size):
        request_buf = self._build_dispatch_request_packet(last_get_time,batch_size)
        print("request to vdc: %s:%d last_get_time=%s" %(task_host,task_port, last_get_time))
        response_buf = self._send_and_recv(task_host,\
                                            task_port,\
                                            timeout,\
                                            request_buf)

        if response_buf is None:
            print("vdc request fail.")
            return None
        
        ret, head, head_a, body = ProtoPkg.decode(response_buf)
        if not ret:
            print("vdc response parse fail.")
            return None
        
        resp = EngineTaskRespBody()
        ret = resp.decode(body)
        if not ret:
            print("task response parse fail.")
            return None
        
        _time, task_list =  self._parse_task_response(resp)

        print("get task from vdc: task_num=%d, last_get_time=%s" % (resp.task_num, last_get_time))

        return _time, task_list

    def _build_collector_report_packet_new(self, file_info, md5, level, virus_name):
        pkg = EngineResultBody()
        pkg.seq = file_info.seq
        pkg.recv_time = file_info.recv_time
        pkg.disp_time = file_info.disp_time
        pkg.md5 = file_info.md5
        pkg.md5_type = file_info.md5_type
        pkg.file_size = file_info.file_size
        pkg.app_id = file_info.app_id
        pkg.sub_app_id = file_info.sub_app_id
        pkg.scan_src_id = file_info.scan_src_id
        pkg.result = 1 #

        pkg.engine_name_len = len(ENGINE_NAME)
        pkg.engine_name = ENGINE_NAME
        pkg.platform_name_len = len(PLATFORM_NAME)
        pkg.platform_name = PLATFORM_NAME

        if level == HIPS_LEVEL_WHITE:
            pkg.engine_detect_result = VDC_LEVEL_WHITE
            pkg.v_name = "Baidu.HIPS.%s.White" % virus_name
        elif level == HIPS_LEVEL_BLACK:
            pkg.engine_detect_result = VDC_LEVEL_BLACK
            pkg.v_name = "Win32.Trojan.HIPS-%s.Gen" % virus_name
        elif level == HIPS_LEVEL_NOT_HANDLE:
            pkg.engine_detect_result = VDC_LEVEL_GRAY
            pkg.v_name = ""
        else:
            pkg.engine_detect_result = VDC_LEVEL_GRAY
            pkg.v_name = ""

        pkg.v_name_len = len(pkg.v_name)

        pkg.new_upload = file_info.new_upload
        pkg.reserved = ""

        head_pkg = SQPkgHead()
        head_pkg.cmd = VDCClient.CMD_FC_SCAN_REPORT
        head_a_pkg = SQAppendPkgHead()
        #print head_pkg.toString()

        return ProtoPkg.encode(head_pkg, head_a_pkg, pkg)

    def _get_key_of_md5_info(self, md5):
        return "%s_vdc_info" % md5

    def send_response(self, ip, port,timeout, md5, level, virus_name):
        ret = self.cache.get(self._get_key_of_md5_info(md5))
        if ret is None:
            print 'md5 not in Redis, check it.'
            return 1
        task = EngineTask()
        task.decode(ret)

        request_buf = self._build_collector_report_packet_new(task, md5, level, virus_name)
        response_buf = self._send_and_recv(ip,\
                                            port,\
                                            timeout,\
                                            request_buf)

        if response_buf is None:
            return 2
        
        ret, head, head_a, body = ProtoPkg.decode(response_buf)
        if not ret:
            return 3
        
        resp = EngineResultRespBody()
        ret = resp.decode(body)
        if not ret or resp.result != 1:
            return 4

        return 0

    def cache_task(self, time_flag, md5_list):
        if not md5_list:
            return

        time_flag = float(time_flag)
        cur_time = time.time()
        for md5 in md5_list:
            print("fetch task: md5=%s, time=%s, spend=%.3f" %(md5, time_flag, cur_time - time_flag))
            self.cache.rpush(settings.VDCClient.task_queue, "%s,%s" % (md5, time_flag))
        dot.dot_pull_task(len(md5_list))

if __name__ == "__main__":
    if len(sys.argv)!=2:
        print 'Usage:'
        print '%s num'%sys.argv[0]
        exit(-1)
    opener=html_opener()

    request_md5_num = int(sys.argv[1])
    ip = '10.52.176.32'
    request_port = 20069
    report_port = 23611
    timeout = 10
    batch_size = 200

    client = VDCClient()
    last_get_time = int(time.time() * 1000)
    #ret_time,md5_list = client.request_task(last_get_time,ip,request_port,timeout,batch_size)
    """
    md5_list=['ff22166f5406c09c8189cb6f1d1d7f89']
    for md5 in md5_list:
        client.send_response(ip,report_port,timeout, md5, 200, 'trojan')
    exit(1)
    """
    while request_md5_num >0:
        last_get_time = int(time.time() * 1000)
        ret = client.request_task(last_get_time,ip,request_port,timeout,batch_size)
        if ret==None:
            continue
        else:
            md5_list = ret[1]
        print time.strftime("%Y-%m-%d %X", time.localtime())

        #check if is exe, if not then drop it
        exe_list=[]
        for md5 in md5_list:
            req=get_req(md5)
            query_result=opener.open(req)
            result_str = query_result.read()
            ascii_result_str = repr(result_str.decode('utf-8'))            
            ascii_type_str = '\u6587\u4ef6\u7c7b\u578b'
            pos1 = ascii_result_str.find(ascii_type_str)
            pos2 = ascii_result_str.find('</td>',pos1)           
            if 'exe' in ascii_result_str[pos1:pos2]:
                exe_list.append(md5)
        print md5_list
        print 'exe ratio = %d/%d'%(len(exe_list),len(md5_list))
        print exe_list
        real_md5_num = len(exe_list)
        if real_md5_num > 0:        
            insert_to_mysql(exe_list)
        request_md5_num -= real_md5_num
        #time.sleep(1)



