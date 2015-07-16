import sys
import paramiko
import traceback
import node_common
import time

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],' username workdir'
        exit(-1)

    user_name = sys.argv[1]
    work_dir = sys.argv[2]

    if user_name == 'root':
        print 'It is dangerous to run commands using root! make sure!'
        exit(-1)
        
    full_node_list = node_common.get_full_node_list()
    
    print 'will run commands on %d nodes...'%len(full_node_list)
    for node in full_node_list:
        try:
            print 'handling node:', node
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(node,port=22,username=user_name,password='123456',timeout=5)

            #cmd = 'cd %s; svn update'%(work_dir)
            cmd = 'cd %s; ls pattern_reg'%(work_dir)
            print cmd
            stdin,stdout,stderr = ssh.exec_command(cmd)
            print 'execute remote command finished,stdout is:\n'
            print stdout.readlines()
            ssh.close()
        except Exception,e:
            print 'can not connect to '+node
            print e
            print traceback.format_exc()
