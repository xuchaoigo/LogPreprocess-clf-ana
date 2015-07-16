import paramiko
import sys
import time
import os

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],'svm_ip_str'
        sys.exit()
    
    vm_ip = sys.argv[1]

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vm_ip,port=22,username='root',password='1234.asd',timeout=4)
    except:
        print 'can not connect to ',vm_ip

    print 'restore vm_ip = ',vm_ip
    stdin, stdout, stderr = ssh.exec_command('./restore_vmdisk.sh')
    
