import sys
import paramiko
import traceback
import node_common
import time

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],' keyword username workdir'
        print 'keyword: PREPROCESS,MIST2VECTOR,MERGEFET,MERGETABLE'
        exit(-1)

    keyword = sys.argv[1]
    user_name = sys.argv[2]
    work_dir = sys.argv[3]

    if user_name == 'root':
        print 'It is dangerous to kill process using root! make sure!'
        exit(-1)
        
    full_node_list = node_common.get_full_node_list()
    keyword_node_list = node_common.get_node_list_by_keyword(full_node_list,keyword,user_name,sys.argv[0])
    
    print 'will kill process on %d nodes...'%len(keyword_node_list)
    for node in keyword_node_list:
        try:
            print 'handling node:', node
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(node,port=22,username=user_name,password='123456',timeout=4)

            cmd = 'cd %s; svn update; ./kill.sh %s'%(work_dir,keyword)
            print cmd
            stdin,stdout,stderr = ssh.exec_command(cmd)
            print 'execute remote command finished\n'
            ssh.close()
        except Exception,e:
            print 'can not connect to '+node
            print e
            print traceback.format_exc()
