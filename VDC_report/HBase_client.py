"""

  Licensed to the Apache Software Foundation (ASF) under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  The ASF licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
"""
# Instructions:
# 1. Run Thrift to generate the python module hbase
#    thrift --gen py ../../../../../hbase-server/src/main/resources/org/apache/hadoop \
#      /hbase/thrift2/hbase.thrift
# 2. Create a directory of your choosing that contains:
#     a. This file (DemoClient.py).
#     b. The directory gen-py/hbase (generated by instruction step 1).
# 3. pip install thrift==0.9.0
# 4. Create a table call "example", with a family called "family1" using the hbase shell.
# 5. Start the hbase thrift2 server
#    bin/hbase thrift2 start
# 6. Execute {python DemoClient.py}.
import sys
import os
import time
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol
from hbase import THBaseService
from hbase.ttypes import *
import re

#judge if the md5 in valid
"""
def _parse_result(result_list,md5_list):
    if len(result_list)!= len(md5_list):
        return None
    #for r in result_list:
    #    print '2-',r
    cur_selected_list=[]
    for i in xrange(len(md5_list)):
        str = '%s'%result_list[i]
        #print str
        
        #some md5 is not in hbase. pass
        if md5_list[i] not in str:
            #cur_selected_list.append(md5_list[i])
            continue
        try:
            #p_os = str.rindex('os_version')
            p_type = str.rindex('type_id')
            p_file = str.rindex('file_subtype')
            #pv_os_s = str.rindex('value=',0,p_os)+7#len('value=\'')
            pv_type_s = str.rindex('value=',0,p_type)+7
            pv_file_s = str.rindex('value=',0,p_file)+7
            #pv_os_e = str.index('\'',pv_os_s)
            pv_type_e = str.index('\'',pv_type_s)
            pv_file_e = str.index('\'',pv_file_s)
        except Exception,e:
            #cur_selected_list.append(md5_list[i])
            continue #weird result 

        #os_version = str[pv_os_s:pv_os_e]
        type_id = str[pv_type_s:pv_type_e]
        file_subtype = str[pv_file_s:pv_file_e]
        #print '%s %s %s %s'%(md5_list[i],os_version,type_id,file_subtype)
        print '%s %s %s'%(md5_list[i],type_id,file_subtype)
        #if os_version=='5.1.32' and type_id=='1' and file_subtype=='0':
        if type_id=='1' and file_subtype=='0':
            cur_selected_list.append(md5_list[i])
    return cur_selected_list
"""

def __parse_result(result_list,md5_list):
    if len(result_list)!= len(md5_list):
        return None
    cur_selected_list=[]
    for i in xrange(len(md5_list)):
        str = '%s'%result_list[i]
        #print str
        #some md5 is not in hbase. pass
        if md5_list[i] not in str:
            #cur_selected_list.append(md5_list[i])
            continue
        try:
            re_ret = re.findall(r'(?<=value=\').+?(?=\', qualifier)',str)
            file_subtype = re_ret[0]
            type_id = re_ret[1]
        except Exception,e:
            #cur_selected_list.append(md5_list[i])
            continue #weird result 
        
        #print '%s %s %s'%(md5_list[i],type_id,file_subtype)
        if type_id=='1' and file_subtype=='0':
            cur_selected_list.append(md5_list[i])
    return cur_selected_list


def hbase_query(md5_list):
# Add path for local "gen-py/hbase" for the pre-generated module
    gen_py_path = os.path.abspath('gen-py')
    sys.path.append(gen_py_path)
    host = "nj02-sw-hds05.nj02.baidu.com"
    port = 9090
    framed = False
    socket = TSocket.TSocket(host, port)
    socket.setTimeout(5000)#5s
    if framed:
        transport = TTransport.TFramedTransport(socket)
    else:
        transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = THBaseService.Client(protocol)
    transport.open()
    table = "vdc_info"

    #start query
    md5_num = len(md5_list)
    QUERY_NUM = 50
    head = 0
    tail = 0
    selected_list=[]
    MAX_TIMES = 3

    while head<md5_num:
        tail = min(md5_num,head+QUERY_NUM)
        cur_md5_list = md5_list[head:tail]
        #print 'cur_md5_list=',cur_md5_list
        get_list = []
        for md5 in cur_md5_list:
            get_list.append(\
            TGet(row=md5,columns=[\
            #TColumnValue(family="props",qualifier="os_version"),\
            TColumnValue(family="props",qualifier="type_id"),\
            TColumnValue(family="props",qualifier="file_subtype"),])\
            )
        result_list = None
        cnt = 0
        while result_list == None:
            cnt += 1
            try:
                #print 'getMultiple:',len(get_list),' md5s'
                result_list = client.getMultiple(table, get_list)
                #print 'getMultiple out:',len(result_list),' md5s'
            except Exception,e:
                print e
                print 'cnt=',cnt
                if cnt == MAX_TIMES:
                    break
        #for r in result_list:
        #    print '1-',r
        head = tail
        if cnt == MAX_TIMES:
            print 'reach %d,continue'%MAX_TIMES
            continue
        #print '__parse_result:',len(result_list),' md5s'
        cur_selected_list = __parse_result(result_list,cur_md5_list)
        #print '__parse_result:',len(cur_selected_list),' md5s'
        if cur_selected_list == None:
            print 'parse query result ERROR!!!len(md5)=%d,len(result)=%d'%(len(cur_md5_list),len(result_list))
            #print cur_md5_list
            #print result_list
            #sys.exit(1)
            continue
        selected_list += cur_selected_list
        #print 'selected_list=',selected_list
    
    transport.close()
    return selected_list

#list = ['f9f8e216aead75f625c74ccd12adbe5f','cee633a00e23a7baff016a36f8cabef8','cea2952b530bf073143fe4bfc69bedf4','fcfc9730daabff9b0556544f89f8acc5','c53f2f7ced02b7cf05c1754b755fd574','fe5cedcf20fcf79417ded7e7b6b9a08a','fe6a7f24b9533e0253a4a25b0c1384c8','fe4458d59e0c7a30a1048d999c9c1abb','f7f42a9dab71fafab18f0fce95364427','f7aed06a8efad0a9674122164a2518ba','fdab2b93945e9f4d88bd4d00cb25dff9','f480d8b5462f4e3ecc60dad806ae71ee','f9ab23c0ab7c8f9842abe1a3202ba9ce','fda876b7b2ffc21e627e535e2edb755f','fa19c5cc6985b610cea3a75102a44e55','fdca447bc8d18284bde7fc1f4428e7b6','fdca6c38b2c517def15c48225a7e2219']
list=['cdad9a5549ade0697552ff777f7a382d', '4a5fd6ba0d1deef622ebcde9e0b2f796', '75dedcd197715d6847030bc3b244587c', '3c67cf7f17cf74da9a5730db9f348e95', '264abe0edc7180d95552aecebfb6d4fb', 'e1a2be219b706108b213b8f46e5abc99', 'c455802f18a57051634c37b1df8936ec', '0d71e37996b135311f86c1ace9a1a976', 'ebc94c4f4244e748c4cd93f43b1a4a62', '22213cfb7660edf61b58ba9fccafeaa5', '0f5bb25b185f00f171942ffa09480f75', '94831504dcfc8d9e1343a4e3c9d0bfa2', 'be7eee6b3a5e5523834cb60c144cff64', '434a4ecbbcd8c99783be3d7a1db4069b', '07735c3acd50810ab62ccfc95d90b61c', '6146fcbc905fe3ade5f7499e7dfd4e14', '428e2005234a08c10dda154e32c62442', 'da5a7d97d5f10a3e24bb83313c05947d', '9c676e737606b5d37a7c42a1b11dd5f5', '1313654d58353513756c07aca90a2121', '131731a49496f735df89cd2b707866ac', 'f8c2e845c83a399edbe82126f9b6c14e', '31af8c123d35d0c7ff85230af651f687', '75096414a93bea83156b97de2e90f7d4', '06fc96d83a9a2c11e8f6e2d20dd22d7b', 'd077572e94f6b6d1056ece35ae41cf7a', '8703dacf520cda087a398a55f8ff60d9', '75ef4dbc533364149ceb58818b8f22f7', '2314d94741cdce984a0207aac45afb35', '936ed49a77517d124ad7d056c48ec7f8', '15ada26b363a8dad479d948d55e85646', '603add296da3c6a45ae576f9ca2d4f2d', '527fd05a2da12d1af3b903416d56fd38', '661adf4b2de4de46f843812d13e313d3', '43b6acbc397805201448b93673f8f85c', 'b4a0406616eec97341430ff054993f1c']
#hbase_query(list)
