import paramiko
import sys
import time
import os
import traceback
import node_common

def _get_usable_client_list(client_list, operation, user_name):
    print 'checking usable clients... num_clients=%d'%len(client_list)
    usable_clients = []
    for client in client_list:
        try:
            print 'cluster_client = ', client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(client,port=22,username=user_name,password='123456',timeout=4)

            cmd = "ps aux | grep cluster_client.py | grep %s | grep %s | grep -v 'grep'"%(operation,user_name)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            outlist = stdout.readlines()
            #print outlist
            num_procs = len(outlist)
            if num_procs >= 1:
                print 'already running cluster_client, skip this machine!'
            else:
                usable_clients.append(client)

            ssh.close()
        except Exception,e:
            print e
            print traceback.format_exc()
    return usable_clients

if __name__ == '__main__':
    if len(sys.argv) != 10:
        print 'Usage:'
        print sys.argv[0],' operation cluster_server listen_port num_procs client_working_dir user_name database_server database_name ngram'
        print 'supported operations: PREPROCESS,MIST2VECTOR,MERGEFET,MERGETABLE,MERGEFET_INC'
        print 'PREPROCESS ignores: database_server, database_name'
        print 'MERGEFET ignores: database_server, database_name'
        print 'MERGEFET_INC needs all the arguments'
        print 'MERGETABLE ignores: num_procs, database_server, database_name'
        print 'MIST2VECTOR needs all the arguments'
        print 'examples: '
        print sys.argv[0], ' MIST2VECTOR nj02-sw-kvmserver03.nj02 12340 8 /home/CURRENT_USER/projects/preprocess/n-gram CURRENT_USER nj02-sw-kvmserver01.nj02 test_database 2' 
        print sys.argv[0], ' MERGEFET_INC cq02-sw-kvm06.cq02 8100 12 /home/karlxu/preprocess/n-gram karlxu nj02-sw-kvmserver01.nj02 iter_i_2gram 2' 
        exit(-1)
    
    operation = sys.argv[1]
    cluster_server = sys.argv[2]
    listen_port = int(sys.argv[3])
    num_procs = int(sys.argv[4])
    work_dir = sys.argv[5]
    user_name = sys.argv[6]
    database_server = sys.argv[7]
    database_name = sys.argv[8]
    ngram = int(sys.argv[9])
    print 'command line:'
    print '%s %s %d %d %s %s %s %s %d'%(operation,cluster_server,listen_port,num_procs,work_dir,user_name,database_server,database_name,ngram)

    orig_client_list = node_common.get_full_node_list()
    #orig_client_list = ['nj02-sw-kvmserver00.nj02']
    client_list = _get_usable_client_list(orig_client_list,operation,user_name)
    
    print '\n'
    print 'executing remote command... num_clients=%d'%len(client_list)
    for client in client_list:
        try:
            print 'cluster_client = ', client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(client,port=22,username=user_name,password='123456',timeout=4)
            real_num_procs = num_procs
            #if node_common.NJ02_VMHOST in client:
            #    real_num_procs = num_procs/2
                         
            cmd = 'cd %s; svn update; nohup python -u cluster_client.py %s %s %d %d %s %s %s %d > %s_client.log &'\
                %(work_dir,operation,cluster_server,listen_port,real_num_procs,user_name,database_server,database_name,ngram,operation)
            print cmd
            stdin,stdout,stderr = ssh.exec_command(cmd)
            #print 'stdout:'
            #print stdout
            #print 'stderr:'
            #print stderr
            print 'execute remote command finished\n'
            ssh.close()
        except Exception,e:
            print e
            print traceback.format_exc()
    
