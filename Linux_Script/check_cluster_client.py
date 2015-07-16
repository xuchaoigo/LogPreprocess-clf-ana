import paramiko
import sys
import time
import os
import node_common

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'Usage:'
        print sys.argv[0],'username operation'
        print 'supported operation: PREPROCESS MERGEFET MIST2VECTOR MERGETABLE MERGEFET_INC'
        exit(-1)
    user_name = sys.argv[1]
    operation = sys.argv[2]
    server_list = node_common.get_full_node_list()
    for server in server_list:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server,port=22,username=user_name,password='123456',timeout=4)
            print 'ssh karlxu@%s'%server.strip(' ')
            cmd = "ps aux | grep cluster_client.py | grep %s | grep %s"%(operation,user_name)
            #cmd = "ps aux | grep 'defunct'"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            outlist = stdout.readlines()
            num_procs = 0
            pid_list = []
            for line in outlist:
                if 'python' not in line:
                    continue
                #print line
                #print pid, convenient to kill
                line_params = line.split(' ')
                for param in line_params:
                    if param != user_name and param != '' and param != ' ':
                        pid_list.append(int(param))
                        break
                num_procs += 1 
            print '%d processes is running cluster_client.'%(num_procs)
            if len(pid_list)!=0:
                print 'kill -9 ',
                for pid in pid_list:
                    print pid,
            print '\n'

        except Exception,e:
            print e
            print 'can not connect to '+server
    
