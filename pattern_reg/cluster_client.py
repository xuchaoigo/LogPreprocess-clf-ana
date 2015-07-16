import sys
import os
import uuid
import preprocess_single
import Mist2Vector_single
import MergeFile_single
import MergeTable_single
import paramiko
import common
import time
import shutil
from multiprocessing.managers import BaseManager,SyncManager
from multiprocessing import Queue,Process
import traceback

OP_PREPROCESS = 'PREPROCESS'
OP_MIST2VECTOR = 'MIST2VECTOR'
OP_MERGEFET = 'MERGEFET'
OP_MERGETABLE = 'MERGETABLE'
OP_REMAINTABLE = 'REMAINTABLE'

LOG_CACHE_DIR = './preprocess_Log_cache/'
FET_CACHE_DIR = './preprocess_Fet_cache/'
M2V_FET_CACHE_DIR = './m2v_Fet_cache/'
M2V_VECTOR_CACHE_DIR = './m2v_Vector_cache/'
MERGE_FET_FEATURE_CACHE_DIR = './mergefet_Feature_cache/'
MERGE_FET_FET_CACHE_DIR = './mergefet_Fet_cache/'
MERGE_TABLE_CACHE_DIR = './mergetable_cache/'

class ServerQueueManager(SyncManager):
        pass

def make_client_manager(ip,port,auth_key):
    """ Create a manager for a client. This manager connects to a server on the
        given address and exposes the get_job_q and get_result_q methods for
        accessing the shared queues from the server.
        Return a manager object.
    """
    
    ServerQueueManager.register('get_job_q')
    ServerQueueManager.register('get_result_q')
    
    manager = ServerQueueManager(address=(ip,port),authkey=auth_key)
    manager.connect()
    
    print 'Client connected to %s:%s' % (ip, port)
    return manager

def robust_sftp(sftp,remote,local,get_flag):
    try_counts = 0
    while try_counts < 3:
        try_counts += 1
        try:
            if get_flag==True:
                sftp.get(remote, local)
            else:
                sftp.put(local,remote)        
            return True
        except Exception,e:
            print e
            print traceback.format_exc()

    return False

def do_remaintable(server_ip,user_name):
    print 'do_remaintable start ...'
    scp = paramiko.Transport((server_ip,22))
    scp.connect(username=user_name,password=common.g_server_password)
    sftp = paramiko.SFTPClient.from_transport(scp)

    try:
        local_output_table = MergeTable_single.parallel_merge_tables(MERGE_TABLE_CACHE_DIR)
        print '-->local_output_table=',local_output_table
        output_filename = local_output_table[local_output_table.rfind('/')+1:]
        remote_output_table = '/home/%s/%s'%(user_name,output_filename)
        print 'remote_output_table=',remote_output_table
        sftp.put(local_output_table,remote_output_table)
        os.remove(local_output_table)
    except Exception,e:
        print e
        print traceback.format_exc()

def do_mergetable(job_q,result_q,server_ip,user_name):
    print 'do_mergetable start ...'
    scp = paramiko.Transport((server_ip,22))
    scp.connect(username=user_name,password=common.g_server_password)
    sftp = paramiko.SFTPClient.from_transport(scp)
    
    while True:
        try:
            remote_input_table_list = job_q.get_nowait()
    
            for remote_input_table in remote_input_table_list:
                filename = remote_input_table[remote_input_table.rfind('/')+1:]
                local_input_table = MERGE_TABLE_CACHE_DIR + filename
                #sftp.get(remote_input_table,local_input_table)
                robust_sftp(sftp,remote_input_table,local_input_table,True)
        
            local_output_table = MergeTable_single.parallel_merge_tables(MERGE_TABLE_CACHE_DIR)
            print '-->local_output_table=',local_output_table
            output_filename = local_output_table[local_output_table.rfind('/')+1:]
            remote_output_table = remote_input_table[:remote_input_table.rfind('/')+1]+output_filename
            print 'remote_output_table=',remote_output_table
            #sftp.put(local_output_table,remote_output_table)
            if robust_sftp(sftp,remote_output_table,local_output_table,False):
                os.remove(local_output_table)
            result_q.put(1)
        except Exception,e:
            if job_q.empty():
                print 'Queue.Empty, will exit loop. pid=%d'%(os.getpid())
                break
            else:
                print 'Is not job_q.empty() exception, pid=%d'%(os.getpid())
                print e
                print traceback.format_exc()
    scp.close()

def do_preprocess_worker(job_q,result_q,sftp,ngram):
    print 'process %d start working...'%(os.getpid())
    #time.sleep(2)
    while True:
        try:
            job = job_q.get_nowait()
            print 'will process %d jobs...,pid=%d'%(len(job),os.getpid())
            for log_file in job:
                fet_file = log_file.replace(common.g_sample_log, common.g_sample_fet)
                md5_file = log_file[log_file.rfind('/')+1:len(log_file)]
                local_log = LOG_CACHE_DIR + md5_file
                local_fet = FET_CACHE_DIR + md5_file
                #print 'remote log_file=',log_file
                #print 'local_log=',local_log
                #sftp.get(log_file,local_log)
                if robust_sftp(sftp,log_file,local_log,True)==False:
                    continue

                try:
                    preprocess_single.process_file(local_log,local_fet,ngram)
                    robust_sftp(sftp,fet_file,local_fet,False)
                    os.remove(local_log)
                    os.remove(local_fet)
                except Exception,ex:
                    print ex
                    print traceback.format_exc()
                #sftp.put(local_fet,fet_file)
                
            result_q.put(len(job))
        except Exception,e:
            if job_q.empty():
                print 'Queue.Empty, will exit loop. pid=%d'%(os.getpid())
                break
            else:
                print 'Is not job_q.empty() exception, pid=%d'%(os.getpid())
                print e
                print traceback.format_exc()
            
    print 'process %d exit.'%(os.getpid())

def do_mist2vector_worker(job_q,result_q,sftp,db_ip,db_name):
    print 'process %d start working...'%(os.getpid())
    #time.sleep(2)
    feature_dict = common.FetchFeature(db_ip,db_name)
    #construct vector file name base on MAC address and process id
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    vector_file_name = 'vector_%s_%d.vec' %(mac,os.getpid())
    local_vector_file = M2V_VECTOR_CACHE_DIR + vector_file_name
    vector_handle = open(local_vector_file,'w')
    remote_vector_file = ''
    
    while True:
        try:
            job = job_q.get_nowait()
            print 'will process %d jobs...,pid=%d'%(len(job),os.getpid())
            for remote_fet_file in job:
                if remote_vector_file == '':
                    remote_vector_file = remote_fet_file[:remote_fet_file.find(common.g_sample_fet)]
                    if remote_vector_file[-1] != '/':
                        remote_vector_file += '/'
                    remote_vector_file += common.g_vector_dir
                    remote_vector_file += '/'
                    remote_vector_file += vector_file_name
                md5_file = remote_fet_file[remote_fet_file.rfind('/')+1 : len(remote_fet_file)]
                local_fet_file = M2V_FET_CACHE_DIR + md5_file
                
                result_sftp = robust_sftp(sftp,remote_fet_file,local_fet_file,True)
                if result_sftp == False:
                    continue
                is_white = True
                if remote_fet_file.find('White') >= 0:
                    is_white = True
                else:
                    is_white = False
                
                try:
                    Mist2Vector_single.Mist2Vector(feature_dict,local_fet_file,vector_handle,is_white)
                except Exception,ex:
                    print ex
                    print traceback.format_exc()

                os.remove(local_fet_file)
            result_q.put(len(job))
        except Exception,e:
            if job_q.empty():
                print 'Queue.Empty, will exit loop. pid=%d'%(os.getpid())
                break
            else:
                print 'Is not job_q.empty() exception, pid=%d'%(os.getpid())
                print e
                print traceback.format_exc() 
    vector_handle.close()
    print 'local_vector_file is: ',local_vector_file
    print 'remote_vector_file is: ', remote_vector_file
    if remote_vector_file != '':
        if robust_sftp(sftp,remote_vector_file,local_vector_file,False):
            os.remove(local_vector_file)
    print 'process %d exit.'%(os.getpid())

def do_mergefet_worker(job_q, result_q, sftp):
    print 'process %d start working...'%(os.getpid())
    #construct feature file name base on MAC address and process id
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    feature_file_name = 'feature_%s_%d.tbl' %(mac,os.getpid())
    remote_feature_file = ''
    task_feature = {}
    while True:
        try:
            job = job_q.get_nowait()
            print 'will process %d jobs...,pid=%d'%(len(job),os.getpid())
            for remote_fet_file in job:
                if remote_feature_file == '':
                    remote_feature_file = remote_fet_file[:remote_fet_file.find(common.g_sample_fet)]
                    if remote_feature_file[-1] != '/':
                        remote_feature_file += '/'
                    remote_feature_file += common.g_feature_dir
                    remote_feature_file += '/'
                    remote_feature_file += feature_file_name
                md5_file = remote_fet_file[remote_fet_file.rfind('/')+1 : len(remote_fet_file)]
                local_fet_file = MERGE_FET_FET_CACHE_DIR + md5_file
                #sftp.get(remote_fet_file, local_fet_file)
                if robust_sftp(sftp,remote_fet_file,local_fet_file,True) == False:
                    continue
                try:
                    MergeFile_single.merge_fet_file(task_feature,local_fet_file)
                except Exception,ex:
                    print ex
                    print traceback.format_exc()

                os.remove(local_fet_file)
            result_q.put(len(job))
        except Exception,e:
            if job_q.empty():
                print 'Queue.Empty, will exit loop. pid=%d'%(os.getpid())
                break
            else:
                print 'Is not job_q.empty() exception, pid=%d'%(os.getpid())
                print e
                print traceback.format_exc()
    
    if len(task_feature) > 0:
        local_feature_file = MERGE_FET_FEATURE_CACHE_DIR + feature_file_name
        MergeFile_single.write_feature_file(task_feature, local_feature_file)
        if remote_feature_file != '':
            robust_sftp(sftp,remote_feature_file,local_feature_file,False)
            #sftp.put(local_feature_file,remote_feature_file)
        print 'local_feature_file is: ',local_feature_file
        print 'remote_feature_file is: ', remote_feature_file
        os.remove(local_feature_file)
    
    print 'process %d exit.'%(os.getpid())

def process_file_worker(job_q, result_q, server_ip, operation, user_name, db_ip, db_name, ngram):
    """ A worker function to be launched in a separate process. Takes jobs from
        job_q - each job is a list of files(one chunk of files) to process. When the job is done,
        the result (number of files processed) is placed into
        result_q. Runs until job_q is empty.
    """
    scp = paramiko.Transport((server_ip,22))
    scp.connect(username=user_name,password=common.g_server_password)
    sftp = paramiko.SFTPClient.from_transport(scp)

    if operation == OP_PREPROCESS:
        do_preprocess_worker(job_q,result_q,sftp,ngram)
    elif operation == OP_MIST2VECTOR:
        do_mist2vector_worker(job_q,result_q,sftp,db_ip,db_name) 
    elif operation == OP_MERGEFET:
        do_mergefet_worker(job_q,result_q,sftp) 
    scp.close()

def mp_process_file(shared_job_q, shared_result_q, server_ip, nprocs,operation,user_name,db_ip,db_name,ngram):
    """ Split the work with jobs in shared_job_q and results in
        shared_result_q into several processes. Launch each process with
        process_file_worker as the worker function, and wait until all are
        finished.
    """
    procs = []
    for i in range(nprocs):
        p = Process(
                target=process_file_worker,
                args=(shared_job_q, shared_result_q, server_ip,operation, user_name, db_ip, db_name, ngram))
        procs.append(p)
        p.start()

    for p in procs:
        p.join()
        print 'successfully joined: %d'%(p.pid)

    print 'exit mp_process_file'

def run_client():
    if len(sys.argv) != 9:
        print 'Usage:'
        print sys.argv[0],' operation server_ip listen_port num_procs user_name,db_ip,db_name,ngram'
        print 'supported operations: PREPROCESS,MIST2VECTOR,MERGEFET,MERGETABLE(ingore num_procs!),REMAINTABLE'
        sys.exit()
    operation = sys.argv[1]
    server_ip = sys.argv[2]
    if operation != OP_REMAINTABLE:
        listen_port = int(sys.argv[3])
        manager = make_client_manager(server_ip,listen_port,common.g_auth_key)
        job_q = manager.get_job_q()
        result_q = manager.get_result_q()

    num_procs = int(sys.argv[4])
    user_name = sys.argv[5] 
    db_ip = sys.argv[6]
    db_name = sys.argv[7] 
    ngram = int(sys.argv[8])
    print 'server_ip=',server_ip,' operation=',operation,' user_name=',user_name,' db_ip=',db_ip,' db_name=',db_name,' ngram=%d'%ngram
    if operation == OP_PREPROCESS:
        if not os.path.exists(LOG_CACHE_DIR):
            os.mkdir(LOG_CACHE_DIR) 
        if not os.path.exists(FET_CACHE_DIR):
            os.mkdir(FET_CACHE_DIR)      
        mp_process_file(job_q,result_q,server_ip,num_procs,operation,user_name,db_ip,db_name,ngram)
        try:
            os.rmdir(LOG_CACHE_DIR) 
            os.rmdir(FET_CACHE_DIR)
        except:
            pass
    elif operation == OP_MIST2VECTOR:
        if not os.path.exists(M2V_FET_CACHE_DIR):
            os.mkdir(M2V_FET_CACHE_DIR)
        if not os.path.exists(M2V_VECTOR_CACHE_DIR):
            os.mkdir(M2V_VECTOR_CACHE_DIR)
        mp_process_file(job_q,result_q,server_ip,num_procs,operation,user_name,db_ip,db_name,ngram)
        try:
            os.rmdir(M2V_FET_CACHE_DIR)
            os.rmdir(M2V_VECTOR_CACHE_DIR)
        except:
            pass
    elif operation == OP_MERGEFET:
        if not os.path.exists(MERGE_FET_FET_CACHE_DIR):
            os.mkdir(MERGE_FET_FET_CACHE_DIR)
        if not os.path.exists(MERGE_FET_FEATURE_CACHE_DIR):
            os.mkdir(MERGE_FET_FEATURE_CACHE_DIR)
        mp_process_file(job_q,result_q,server_ip,num_procs,operation,user_name,db_ip,db_name,ngram)
        try:
            os.rmdir(MERGE_FET_FET_CACHE_DIR)
            os.rmdir(MERGE_FET_FEATURE_CACHE_DIR)
        except:
            pass
    elif operation == OP_MERGETABLE:
        if not os.path.exists(MERGE_TABLE_CACHE_DIR):
            os.mkdir(MERGE_TABLE_CACHE_DIR)
        do_mergetable(job_q,result_q,server_ip,user_name)
        try:
            os.rmdir(MERGE_TABLE_CACHE_DIR)
        except:
            pass
    elif operation == OP_REMAINTABLE:
        if not os.path.exists(MERGE_TABLE_CACHE_DIR):
            print '%s not exists, no need to do anything.'%(MERGE_TABLE_CACHE_DIR)
        else:
            do_remaintable(server_ip,user_name)
            os.rmdir(MERGE_TABLE_CACHE_DIR)
    else:
        print 'unexpected operation: ',operation
        sys.exit()
    
    print 'client exit.'

if __name__ == '__main__':
    run_client()            
