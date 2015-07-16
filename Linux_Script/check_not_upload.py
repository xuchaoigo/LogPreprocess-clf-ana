import paramiko
import sys
import time
import os

def _get_server_list():
    server_list = []
    #kvmserver
    for i in range(0,5):
        server_name = 'nj02-sw-kvmserver0%d.nj02'%i
        server_list.append(server_name)
    #kvmhost
    for i in range(1,21):
        if i==12 or i==17:\
            continue
        server_name = 'nj02-sw-kvm%02d.nj02'%i
        server_list.append(server_name)
    #cqhost
    for i in range(1,7):
        server_name = 'cq02-sw-kvm%02d.cq02'%i
        server_list.append(server_name)
    #more servers...
    
    return server_list

if __name__ == '__main__':
    server_list = _get_server_list()
    for server in server_list:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(server,port=22,username='sonachzhang',password='123456',timeout=4)
            print 'server = ', server
            stdin, stdout, stderr = ssh.exec_command("wc -l /home/sonachzhang/projects/preprocess/n-gram/m2v_Vector_cache/*")
            print stdout.readlines()
            print '\n'
            ssh.close()
        except:
            print 'can not connect to '+server
    
