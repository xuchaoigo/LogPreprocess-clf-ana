#!/usr/bin/env python
# coding=utf-8
"""
@author     yangyang
@date       2013-7-11
@brief      protocol for head
            STX + SQPkgHead + SQAppendPkgHead + body + ETX
"""

import struct
import binascii

STX = 0x02
ETX = 0x03
class SQPkgHead(object):
    '''
        head protocol
    '''
    PROTO_LEN = 37
    
    def __init__(self):
        self.pkg_len = 0
        self.cmd = 0
        self.seq = 0
        self.pro_ver = 0
        self.type = 0
        self.src_ip = 0
        self.src_port = 0
        self.socket = 0
        self.reserved = ""
      
    def encode(self):
        body_fmt = "!HHIHBIHI16s"
        return struct.pack(body_fmt, self.pkg_len, self.cmd, self.seq, self.pro_ver, self.type, self.src_ip, self.src_port, self.socket, self.reserved)
    
    def decode(self, buffer):
        if len(buffer) != self.PROTO_LEN:
            return False
        
        try:
            body_fmt = "!HHIHBIHI16s"
            self.pkg_len, self.cmd, self.seq, self.pro_ver, self.type, self.src_ip, self.src_port, self.socket, self.reserved = struct.unpack(body_fmt, buffer)
        except:
            return False
        return True
    
    def toString(self):
        return "pkg_len=%d, cmd=%d, seq=%d, pro_ver=%d, type=%d, src_ip=%d, src_port=%d" % (self.pkg_len, self.cmd, self.seq, self.pro_ver, self.type, self.src_ip, self.src_port)

class SQAppendPkgHead(object):
    '''
        header append protocol
    '''
    
    def __init__(self):
        self.append_len = 0
        self.append_buf = ""
    
    def encode(self):
        body_fmt = "!H%ds" % self.append_len
        return struct.pack(body_fmt, self.append_len, self.append_buf)
        
    def decode(self, buffer):
        offset = 0
        try:
            append_len = struct.unpack("!H", buffer[0:2])[0]
            self.append_buf = buffer[2:2+append_len]
            offset = len(self.append_buf)+2
            return True,offset
        except:
            return False,offset
    def toString(self):
        return "append_len=%d" % self.append_len
        

class ProtoPkg(object):
    '''
        whole body decode or encode
    '''
    def __init__(self):
        pass
        
    @staticmethod
    def decode(buffer):
        start_ch = struct.unpack("!B", buffer[0])[0]
        end_ch = struct.unpack("!B", buffer[-1])[0]
    
        if start_ch != STX or end_ch != ETX:
            return False, None, None, None
        
        offset = 1
        head = SQPkgHead()
        ret = head.decode(buffer[offset:offset+head.PROTO_LEN])
        if not ret:
            return False, None, None, None
        
        offset += head.PROTO_LEN
        head_a = SQAppendPkgHead()
        ret, head_a_len = head_a.decode(buffer[offset:-1])
        if not ret:
            return False, None, None, None
        
        offset += head_a_len
        body = buffer[offset:-1]
        
        return True, head, head_a, body
    
    @staticmethod
    def encode(head, head_a, body):
        start_ch = struct.pack("!B", STX)
        end_ch = struct.pack("!B", ETX)
        head_a_str = head_a.encode()
        body_str = body.encode()
        
        head.pkg_len = 2 + 37 + len(head_a_str) + len(body_str)
        head_str = head.encode()
        
        
        return start_ch + head_str + head_a_str + body_str + end_ch
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
