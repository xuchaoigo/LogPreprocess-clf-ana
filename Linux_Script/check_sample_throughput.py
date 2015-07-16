import os
import os.path
import time
import traceback
import MySQLdb

g_throughput_dbserver = 'nj02-sw-kvmserver01.nj02'
g_throughput_dbname = 'throughput'
g_result_dir = './throughput_result/'

def _get_table_list():
    mysql_conn = MySQLdb.connect(host=g_throughput_dbserver,user='root',passwd='123456',db=g_throughput_dbname,port=3306)
    mysql_cursor = mysql_conn.cursor()
    sql_cmd = "select table_name from information_schema.tables where table_schema='%s'"%(g_throughput_dbname)
    count = mysql_cursor.execute(sql_cmd)
    results = mysql_cursor.fetchmany(count)
    table_list = []
    for item in results:
        table_list.append(item[0])
    mysql_cursor.close()
    mysql_conn.close()
    return table_list

def check_abnormal(table,logs_list,samples_list,time_list):
    if len(logs_list) <= 1:
        return
    inc_logs_list = []
    inc_samples_list = []
    for i in range(0,len(logs_list)-1):
        inc_logs_list.append(logs_list[i]-logs_list[i+1])
        inc_samples_list.append(samples_list[i]-samples_list[i+1])
    
    inc_info_path = os.path.join(g_result_dir,'inc_num_%s'%table)
    inc_info_handle = open(inc_info_path,'w')
    for i in range(0,len(inc_logs_list)):
        inc_info_handle.write('[%s] INC_LOGS=%d INC_SAMPLES=%d\n'%(time_list[i],inc_logs_list[i],inc_samples_list[i]))
    inc_info_handle.close()

    if len(logs_list) <= 2:
        return

    logs_estimate = sum(inc_logs_list[1:])/(len(inc_logs_list)-1)
    samples_estimate = sum(inc_samples_list[1:])/(len(inc_samples_list)-1)
    if inc_logs_list[0] < logs_estimate/3: 
        alarm_handle = open(g_result_dir+'alarm_throughput.log','a+')
        alarm_string = '[%s] %s abnormal inc logs: %d'%(time_list[0],table,inc_logs_list[0])
        alarm_handle.write('%s\n'%alarm_string)
        print alarm_string
        alarm_handle.close()
    else:
        print 'normal inc logs'

    if inc_samples_list[0] < samples_estimate/3: 
        alarm_handle = open(g_result_dir+'alarm_throughput.log','a+')
        alarm_string = '[%s] %s abnormal inc samples: %d'%(time_list[0],table,inc_samples_list[0])
        alarm_handle.write('%s\n'%alarm_string)
        print alarm_string
        alarm_handle.close()
    else:
        print 'normal inc samples'
   

if __name__ == '__main__':
    table_list = _get_table_list()
    print 'checking tables:'
    print table_list

    if not os.path.exists(g_result_dir):
        os.mkdir(g_result_dir)
    while True:
        try:
            mysql_conn = MySQLdb.connect(host=g_throughput_dbserver,user='root',passwd='123456',db=g_throughput_dbname, port=3306)
            mysql_cursor = mysql_conn.cursor()
            for table in table_list:
                sql_cmd = "select num_total_logs,num_total_samples,report_time from %s order by report_time desc limit 288"%(table)
                print sql_cmd
                count = mysql_cursor.execute(sql_cmd)
                results = mysql_cursor.fetchmany(count)
                num_logs_list = []
                num_samples_list = []
                time_list = []
                for item in results:
                    num_logs_list.append(item[0])
                    num_samples_list.append(item[1])
                    time_list.append(item[2])
                check_abnormal(table,num_logs_list,num_samples_list,time_list)
            mysql_cursor.close()
            mysql_conn.close()
        except Exception,e:
            print e
            print traceback.format_exc()

        time.sleep(720)
            
