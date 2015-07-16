import sys
import os
import time
import traceback
import MySQLdb

g_throughput_dbserver = 'nj02-sw-kvmserver01.nj02'
g_throughput_dbname = 'throughput'
g_upload_path = '/home/hips/FileServer/upload/'
g_download_path = '/home/hips/FileServer/download/'

def type_throughput(type_list):
    #create table Trojan(report_time DATETIME,num_total_logs INT,num_total_samples INT);    
    while True:
        try:
            mysql_conn = MySQLdb.connect(host=g_throughput_dbserver,user='root',passwd='123456',db=g_throughput_dbname, port=3306)
            mysql_cursor = mysql_conn.cursor()
            for sample_type in type_list:
                create_cmd='create table if not exists %s(report_time DATETIME,num_total_logs INT,num_total_samples INT)'%sample_type
                mysql_cursor.execute(create_cmd)
           
                current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
                
                log_path = os.path.join(g_upload_path,sample_type)
                shell_command = 'ls %s -lR | wc -l'%log_path
                num_logs = int(os.popen(shell_command).read())
                sample_path = os.path.join(g_download_path,sample_type)
                shell_command = 'ls %s -lR | wc -l'%sample_path
                num_samples = int(os.popen(shell_command).read())

                sql_cmd = 'insert into %s(report_time,num_total_logs,num_total_samples) VALUES(\'%s\',%d,%d)' %(sample_type,current_time,num_logs,num_samples)
                print sql_cmd
                mysql_cursor.execute(sql_cmd)
                mysql_conn.commit()
            mysql_cursor.close()
            mysql_conn.close()
        except Exception,e:
            print e
            print traceback.format_exc()

        time.sleep(600)       

if __name__ == '__main__':
    if len(sys.argv)<2:
        print 'Usage: '
        print sys.argv[0],' sample_type1 sample_type2 ... sample_typeN'
        print 'number of sample_type(N) >= 1'
        print 'for example: python ',sys.argv[0],' Trojan Adware'
        exit(-1)
    
    type_list = []
    for i in range(1,len(sys.argv)):
        type_list.append(sys.argv[i])

    print type_list

    type_throughput(type_list)

    
