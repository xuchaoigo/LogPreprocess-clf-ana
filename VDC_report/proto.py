#!/usr/bin/env python
# coding=utf-8
"""
@author     yangyang
@date       2013-7-11
@brief      protocol for dispatcher and collector 
"""

import struct
import binascii

class EngineTaskReqBody(object):
    '''
        file_info_vdc -> dispatcher
    '''
    
    PROTO_LEN = 523
    
    
    def __init__(self):
        self.task_num = 0
        self.engine_name_len = 0
        self.engine_name = ""
        self.platform_name_len = 0
        self.platform_name = ""
        self.prev_get_time = 0
        
    def encode(self):
        return struct.pack("!BB256sB256sQ", self.task_num, self.engine_name_len, self.engine_name, self.platform_name_len, self.platform_name, self.prev_get_time)
      
    def toString(self):
        return "task_num=%d, engine_name=%s, platform_name=%s, prev_get_time=%d" % (self.task_num, self.engine_name, self.platform_name, self.prev_get_time)

class EngineTask(object):
    '''
        dispatch to Engine Item task
    '''
    PROTO_LEN = 64
    
    
    def __init__(self):
        self.seq = 0
        self.md5 = ""
        self.md5_type = 0
        self.file_size = 0
        self.app_id = 0
        self.sub_app_id = 0
        self.scan_src_id = 0
        self.recv_time = 0
        self.disp_time = 0
        self.new_upload = 0
        self.reserved = ""
    
    def decode(self,buffer):
        if len(buffer) != self.PROTO_LEN:
            return False
        
        try:
            body_fmt = "!I16sBIHHHQQB16s"
            self.seq, self.md5, self.md5_type, self.file_size, self.app_id, self.sub_app_id, self.scan_src_id, self.recv_time, self.disp_time, self.new_upload, self.reserved = struct.unpack(body_fmt, buffer)
        except:
            return False
        
        return True
            
    def toString(self):
        vis_md5 = binascii.b2a_hex(self.md5)
        return "seq=%d, md5=%s, md5_type=%d, file_size=%d, app_id=%d, sub_app_id=%d, scan_src_id=%d, recv_time=%d, disp_time=%d, new_upload=%d" % (self.seq, vis_md5, self.md5_type, self.file_size, self.app_id, self.sub_app_id, self.scan_src_id, self.recv_time, self.disp_time, self.new_upload)
        
class EngineTaskRespBody(object):
    '''
        file_info_vdc <- dispatcher
    '''
    
    
    def __init__(self):
        self.task_num = 0
        self.task_info = []
        
    def decode(self, buffer):
        try:
            self.task_num = struct.unpack("!B", buffer[0])[0]
        except:
            return False
        offset = 1
        item_len = 64
        for idx in range(self.task_num):
            tmp_info = EngineTask()
            item_buf = buffer[idx*item_len+offset:(idx+1)*item_len + offset]
            if not tmp_info.decode(item_buf):
                return False
            else:
                self.task_info.append(tmp_info)
        return True
    def toString(self):
        content = str(self.task_num) + "\n"
        for item in self.task_info:
            content += item.toString() + "\n"
        return content

class EngineResultBody(object):
    '''
        file_info_vdc -> collector
    '''  
    
   
    def __init__(self):
        self.seq = 0
        self.recv_time = 0
        self.disp_time = 0
        self.md5 = ""
        self.result = 0
        self.md5_type = 0
        self.file_size = 0
        self.app_id = 0
        self.sub_app_id = 0
        self.scan_src_id = 0

        self.engine_name_len = 0
        self.engine_name = ""
        self.platform_name_len = 0
        self.platform_name = ""
        self.v_name_len = 0
        self.v_name = ""
        self.engine_detect_result = 0
        self.new_upload = 0
        self.reserved = ""
        '''
        self.path_len = 0
        self.path = ""
        self.describe_len = 0
        self.describe = ""
        self.product_name_len = 0
        self.product_name = ""
        self.source = 0
        '''
    
    def encode(self):
        '''change by xiaojing 编码的时候，路径、描述等有长度的按照实际的长度写入，reserved字段写入16个字节'''
        body_fmt = "!IQQ16sBBIHHHB" + str(self.engine_name_len) +  "sB" + str(self.platform_name_len) + "sB" + str(self.v_name_len) + "siB" + "16s"
            #str(self.path_len) + "sB" + str(self.describe_len) + "sB" + str(self.product_name_len) + "sI"
        return struct.pack(body_fmt, self.seq, self.recv_time, self.disp_time, self.md5, self.result, self.md5_type, self.file_size, self.app_id, self.sub_app_id, self.scan_src_id, self.engine_name_len, self.engine_name, self.platform_name_len, self.platform_name, self.v_name_len, self.v_name, self.engine_detect_result, self.new_upload, self.reserved)#, self.path_len, self.path, self.describe_len, self.describe, self.product_name_len, self.product_name, self.source)
              
    def toString(self):
        vis_md5 = binascii.b2a_hex(self.md5)
        return "seq=%d, recv_time=%d, disp_time=%d, md5=%s, result=%d, md5_type=%d, file_size=%d, app_id=%d, sub_app_id=%d, scan_src_id=%d, engine_name_len=%d, engine_name=%s, platform_name_len=%d, platform_name=%s, v_name_len=%d, v_name=%s, engine_detect_result=%d, new_upload=%d " % (self.seq, self.recv_time, self.disp_time, vis_md5, self.result, self.md5_type, self.file_size, self.app_id, self.sub_app_id, self.scan_src_id, self.engine_name_len, self.engine_name, self.platform_name_len, self.platform_name, self.v_name_len, self.v_name, self.engine_detect_result, self.new_upload)
        #return "seq=%d, recv_time=%d, disp_time=%d, md5=%s, result=%d, md5_type=%d, file_size=%d, app_id=%d, sub_app_id=%d, scan_src_id=%d, engine_name_len=%d, engine_name=%s, platform_name_len=%d, platform_name=%s, v_name_len=%d, v_name=%s, engine_detect_result=%d, new_upload=%d, path=%s, path_len=%d, describe=%s, describe_len=%d, product_name=%s, product_name_len=%d, source=%d" % (self.seq, self.recv_time, self.disp_time, vis_md5, self.result, self.md5_type, self.file_size, self.app_id, self.sub_app_id, self.scan_src_id, self.engine_name_len, self.engine_name, self.platform_name_len, self.platform_name, self.v_name_len, self.v_name, self.engine_detect_result, self.new_upload, self.path, self.path_len, self.describe, self.describe_len, self.product_name, self.product_name_len, self.source)
 
class EngineResultRespBody(object):
    '''
        file_info_vdc <- collector
    '''
    PROTO_LEN = 22
    
    
    def __init__(self):
        self.seq = 0
        self.md5 = ""
        self.md5_type = 0
        self.result = 0
    
    def decode(self, buffer):
        if len(buffer) != self.PROTO_LEN:
            return False
        
        try:
            body_fmt = "!I16sBB"
            self.seq, self.md5, self.md5_type, self.result = struct.unpack(body_fmt, buffer)
        except:
            return False
        return True
        
    def toString(self):
        vis_md5 = binascii.b2a_hex(self.md5)
        return "seq=%d, md5=%s, md5_type=%d, result=%d" % (self.seq, vis_md5, self.md5_type, self.result)
