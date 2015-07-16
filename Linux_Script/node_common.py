import paramiko
import traceback

NJ02_SERVER = 'nj02-sw-kvmserver'
NJ02_VMHOST = 'nj02-sw-kvm'
CQ02_VMHOST = 'cq02-sw-kvm'

def get_full_node_list():
    node_list = []
    #kvmnode
    for i in range(0,5):
        if i==1 or i==2:
            continue
        node_name = '%s0%d.nj02'%(NJ02_SERVER,i)
        node_list.append(node_name)
    #kvmhost
    for i in range(1,21):
        if i==12 or i==17:\
            continue
        node_name = '%s%02d.nj02'%(NJ02_VMHOST,i)
        node_list.append(node_name)
    #cqhost
    for i in range(1,14):
        if i==7 or i==8 or i==9:
            continue
        node_name = '%s%02d.cq02'%(CQ02_VMHOST,i)
        node_list.append(node_name)
    #more nodes...
    #node_list.append('cq02-backup314.cq02')
    node_list.append('cq02-swvm-kernel00.cq02')
    node_list.append('cq02-swvm-kernel01.cq02')
    node_list.append('cq02-vm-kernel02.cq02')

    return node_list

def get_node_list_by_keyword(client_list, keyword, user_name, exclude):
    print 'checking nodes by keyword... num_nodes=%d'%len(client_list)
    keyword_nodes = []
    for client in client_list:
        try:
            print 'checking node: ', client, '...'
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(client,port=22,username=user_name,password='123456',timeout=4)

            cmd = "ps -ef | grep %s | grep -v \"grep\" | grep -v \"%s\""%(keyword,exclude)
            #cmd = "ps ef | grep %s"%keyword
            #print cmd
            stdin, stdout, stderr = ssh.exec_command(cmd)
            outlist = stdout.readlines()
            #print outlist
            num_procs = 0
            for line in outlist:
                if 'python' not in line:
                    continue
                num_procs += 1
            #print '%d processes is running cluster_client.'%(num_procs)
            if num_procs >= 1:
                keyword_nodes.append(client)
                print '%d commands with keyword found.'%num_procs

            ssh.close()
        except Exception,e:
            print e
            print traceback.format_exc()
    return keyword_nodes
