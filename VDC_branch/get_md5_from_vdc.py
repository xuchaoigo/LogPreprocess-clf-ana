import sys
import const
import struct
import traceback
#import sample_task_pb2
#import result_task_pb2
#import inner_header_pb2
import vdc_message_pb2
from struct import pack
import socket
from mysql_common import *

def build_inner_header(cmd_id, sub_cmd_id):
    '''
        build inner header
    '''
    header = vdc_message_pb2.InnerHeader()
    header.cmd = cmd_id
    header.subcmd = sub_cmd_id
    header.seq = 0
    header.protoversion = 1
    header_buf = header.SerializeToString()
    header_all = pack("!IH", len(header_buf), const.TYPE_INNERHEADER) + header_buf
    return header_all

def _parse_request(data):
    '''
        packet = dwTotalLen + dwInnerHeaderLen + wType + InnerHeader + dwBodyTotalLen + wType + Info
    '''
    try:
        h = data[0:4]
        total_len = struct.unpack("!I", h)[0]
        h = data[4:]
        cur_len = 0
        inner_header_len, w_type = struct.unpack("!IH", h[cur_len : cur_len + 6])
        cur_len += 6
        
        inner_header_buf = h[cur_len:cur_len+inner_header_len]
        cur_len += inner_header_len
        
        tmp_len, tmp_type= struct.unpack("!IH", h[cur_len : cur_len + 6])
        cur_len += 6
        body_info = h[cur_len:]
        return inner_header_buf, body_info
    except Exception,e:
        print e
        print traceback.format_exc()        
        #logger_e.error("recv&parse packet failed: %s" % traceback.format_exc())
        return None, None

def request_md5list(request_num,ip,port):
    task_request = vdc_message_pb2.SampleTaskReq()
    task_request.file_cnt = request_num
    task_request_buf = task_request.SerializeToString()
    #print 'len of task_quest_buf=',len(task_request_buf)
     
    body = pack("!IH", len(task_request_buf), const.TYPE_BODY) + task_request_buf
    header = build_inner_header(const.IN_CMD_DEFENCE, const.IN_SUBCMD_IN)
    total_buf = pack("!I", len(header)+len(body)+4) + header + body
    #print 'len of total_buf=',len(total_buf)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'request %d md5,server %s:%d'%(request_num,ip,port)
    sock.sendto(total_buf, (ip,port))
    data = sock.recvfrom(request_num*40)
    
    #print data[0]
    #print 'recv data len=',len(data[0])
    print 'recv reply from %s:%d'%(ip,port)
    inner_header_buf, info_buf = _parse_request(data[0])
    task_reply = vdc_message_pb2.SampleTaskRep()
    task_reply.ParseFromString(info_buf)
    print 'recv md5list len=',task_reply.result_cnt   
    
    md5_list=[]
    for md5 in task_reply.md5:
        #print md5
        md5_list.append(md5)
    return md5_list

def reply_mships_result(result_list,ip,port):
    task_request = vdc_message_pb2.ResultTaskReq()
    print 'result cnt=',len(result_list)
    task_request.reply_cnt = len(result_list)
    for md5,result in result_list:
        #print '%s , %d'%(md5,result)
        md5_info = task_request.result_info.add()   
        md5_info.md5 = md5        
        md5_info.level = result
    task_request_buf = task_request.SerializeToString()
    print 'len of task_quest_buf=',len(task_request_buf)

    body = pack("!IH", len(task_request_buf), const.TYPE_BODY) + task_request_buf
    header = build_inner_header(const.IN_CMD_DEFENCE_RES, const.IN_SUBCMD_IN)
    total_buf = pack("!I", len(header)+len(body)+4) + header + body
    print 'len of total_buf=',len(total_buf)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'reply %d results,server %s:%d'%(len(result_list),ip,port)
    sock.sendto(total_buf, (ip,port))
    
    data = sock.recvfrom(len(result_list)*40)
    print 'recv data len=',len(data[0])
    print 'recv reply from %s:%d'%(ip,port)
    inner_header_buf, info_buf = _parse_request(data[0])
    task_reply = vdc_message_pb2.ResultTaskRep()
    task_reply.ParseFromString(info_buf)
    print 'send %d results success'%task_reply.result_cnt   
    md5_list=[]
    for md5 in task_reply.md5:
        #print md5
        md5_list.append(md5)
    return   

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print '%s num'%sys.argv[0]
        exit(-1)
    
    ip = '10.58.189.39'
    port = 55620
    request_md5_num = int(sys.argv[1])
    batch_size = 200
    while request_md5_num >0:
        md5_list = request_md5list(batch_size, ip, port)      
        insert_to_mysql(md5_list)
        request_md5_num -=batch_size     

    print 'Main process exit.'
