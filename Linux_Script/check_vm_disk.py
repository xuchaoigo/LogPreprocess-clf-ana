import paramiko
import sys
import time
import os

if __name__ == '__main__':
    nj_ip_list=[\
        '10.205.34.15',\
        '10.205.34.17',\
        '10.205.34.18',\
        '10.205.34.19',\
        '10.205.34.16',\
        '10.205.33.56',\
        '10.205.33.55',\
        '10.205.33.57',\
        '10.205.33.54',\
        '10.205.33.53',\
        '10.205.27.15',\
        '10.205.27.13',\
        '10.205.27.12',\
        '10.205.27.11',\
        '10.206.196.12',\
        '10.206.196.14',\
        '10.206.196.15',\
        '10.206.196.16'\
        ]    

    for ip in nj_ip_list:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip,port=22,username='root',password='1234.asd',timeout=4)

                print 'ip = ',ip
                stdin, stdout, stderr = ssh.exec_command('hostname')
                outlist = stdout.readlines()
                for line in outlist:
                    print 'ssh root@'+line[0:].strip()
                stdin, stdout, stderr = ssh.exec_command('df -lh')
                outlist = stdout.readlines()
                for line in outlist:
                    if '1.3T' in line:
                        print line
            except:
                print 'can not connect to '+ip
    
