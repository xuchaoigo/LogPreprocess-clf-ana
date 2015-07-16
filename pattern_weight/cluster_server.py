import os
import sys
import time
import shutil
import common
from multiprocessing.managers import BaseManager,SyncManager
from multiprocessing import Process, Queue

g_process_start_time=0
g_process_start_readable_time=''

OP_PREPROCESS = 'PREPROCESS'
OP_MIST2VECTOR = 'MIST2VECTOR'
OP_MERGEFET = 'MERGEFET'
OP_MERGETABLE = 'MERGETABLE'

def _get_samplename_list():
    name_list = []
    name_list.append('White')
    name_list.append('Trojan')
    name_list.append('Adware')
    name_list.append('Backdoor')
    name_list.append('Dropper')
    name_list.append('Packed')
    name_list.append('Risk')
    name_list.append('Rootkit')
    name_list.append('Virus')
    name_list.append('Win32')
    name_list.append('Worm')
    return name_list

class JobQueueManager(SyncManager):
    pass

def do_process(shared_job_q,shared_result_q,top_src_dir,top_dst_dir,operation):
    global g_process_start_time
    global g_process_start_readable_time
    file_list = []
    name_list = _get_samplename_list()
    print 'begin collecting file information...'
    for root,dirs,files in os.walk(top_src_dir):
        for name in files:
            src_file = os.path.join(root,name)
            file_list.append(src_file)
            
            if operation == OP_PREPROCESS:
                tail_path = src_file[len(top_src_dir):]
                if top_dst_dir[-1] != '/':
                    fet_file = top_dst_dir+'/'+tail_path
                else:
                    fet_file = top_dst_dir + tail_path
                fet_dir = fet_file[0:fet_file.rfind('/')]
                if not os.path.exists(fet_dir):
                    os.makedirs(fet_dir)
            elif operation == OP_MIST2VECTOR or operation == OP_MERGEFET:
                name_found = False
                for name in name_list:
                    if src_file.find(name)>=0:
                        name_found = True
                        break
                if not name_found:
                    print 'expect Sample name in full path: ', src_file
                    sys.exit()
            elif operation == OP_MERGETABLE:
                pass
            else:
                print 'unexpected operation: ',operation
                sys.exit()

    print '%d files to process...'%len(file_list)  
        
    if operation == OP_MERGETABLE:
        table_dict = {}
        for sub_table_file in file_list:
            pos = sub_table_file.rfind('.')
            if pos!=-1:
                table_name = sub_table_file[pos+1:]
            if table_dict.has_key(table_name):
                table_dict[table_name].append(sub_table_file)
            else:
                table_dict[table_name]=[sub_table_file]
        #chunk_size here is an average size
        num_files = len(file_list)
        num_jobs = len(table_dict)
        chunk_size = int(num_files/num_jobs)
        for (k,v) in table_dict.items():
            shared_job_q.put(v)
        print 'chunk_size=%d, num_jobs=%d,job_q size=%d' %(chunk_size,num_jobs,shared_job_q.qsize())
        if(shared_job_q.qsize() < 10):
            print 'job_q size is too small so unnecessary to run cluster. maybe something wrong??? check it:)'
            #sys.exit()
        chunk_processed = 0
        while chunk_processed < num_jobs:
            chunk_processed += shared_result_q.get()
            if g_process_start_time == 0:
                print 'setting process_start_time...'
                g_process_start_time = time.time()
                g_process_start_readable_time = common.get_readable_time()
            print 'chunk processed: ',chunk_processed
        print 'all chunks processed!'
        return
   
    chunk_size = common.g_chunk_size
    num_files = len(file_list)
    num_jobs = int(num_files/chunk_size);
    for i in range(0,num_jobs):
        shared_job_q.put(file_list[i*chunk_size:(i+1)*chunk_size])
    if num_jobs*chunk_size < num_files:
        shared_job_q.put(file_list[num_jobs*chunk_size:num_files])

    print 'chunk_size=%d, num_jobs=%d,job_q size=%d' %(chunk_size,num_jobs,shared_job_q.qsize())
    if(shared_job_q.qsize() < 10):
        print 'job_q size is too small so unnecessary to run cluster. maybe something wrong??? check it:)'
        sys.exit()
    
    files_processed = 0
    while files_processed < num_files:
        files_processed += shared_result_q.get()
        if g_process_start_time == 0:
            print 'setting process_start_time...'
            g_process_start_time = time.time()
            g_process_start_readable_time = common.get_readable_time()
        print '[%s] files processed: %d'%(common.get_readable_time(),files_processed)
    print 'all files processed!'
      
def make_server_manager(port,auth_key):
    """ Create a manager for the server, listening on the given port.
        Return a manager object with get_job_q and get_result_q methods.
    """
    job_q = Queue()
    result_q = Queue()
    # This is based on the examples in the official docs of multiprocessing.
    # get_{job|result}_q return synchronized proxies for the actual Queue
    # objects.
        
    JobQueueManager.register('get_job_q', callable=lambda: job_q)
    JobQueueManager.register('get_result_q', callable=lambda: result_q)
    manager = JobQueueManager(address=('',port), authkey=auth_key)
    manager.start()
    print 'Server started at port %s' %port
    return manager
 
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage:'
        print sys.argv[0], ' operation[%s|%s|%s|%s], ...'%(OP_PREPROCESS,OP_MIST2VECTOR,OP_MERGEFET,OP_MERGETABLE)
        sys.exit()
  
    #common.GetConfig() 
    operation = sys.argv[1]
    if operation == OP_PREPROCESS:
        if len(sys.argv) != 5:
            print 'Usage:'
            print sys.argv[0],' PREPROCESS dir_of_log dir_of_fet listen_port'
            print 'dir_of_log: must be FULL directory, and contains ',common.g_sample_log,'!'
            print 'dir_of_fet: must be FULL directory, and contains ',common.g_sample_log,'!'
            sys.exit()
    elif operation == OP_MIST2VECTOR:
        if len(sys.argv) != 5:
            print 'Usage:'
            print sys.argv[0],' MIST2VECTOR dir_of_fet dir_of_vector listen_port'
            print 'dir_of_fet: must be FULL directory, and contains ',common.g_sample_fet,'!'
            print 'dir_of_vector: must be FULL directory, stores seperate vector files generatored by clients.'
            sys.exit()
    elif operation == OP_MERGEFET:
        if len(sys.argv) != 5:
            print 'Usage:'
            print sys.argv[0],' MERGEFET dir_of_fet dir_of_feature listen_port'
            print 'dir_of_fet: must be FULL directory, and contains ',common.g_sample_fet,'!'
            print 'dir_of_feture: must be FULL directory, stores seperate feature files generatored by clients.'
            sys.exit()
    elif operation == OP_MERGETABLE:
        if len(sys.argv) != 5:
            print 'Usage:'
            print sys.argv[0],' MERGETABLE dir_of_splited_tables dir_of_target(NULL) listen_port'
            print 'dir_of_splited_tables: must be FULL directory, and contains ',common.g_sample_table,'!'
            print 'dir_of_target(NULL): must be FULL directory, and contains ',common.g_sample_table,'!'
            sys.exit()
    else:
        print 'unexpected operation: ',operation

    dir_of_source = sys.argv[2]
    dir_of_target = sys.argv[3]
    if dir_of_source[0]!='/' or dir_of_source[0]!='/':
        print 'directories must be full path:'
        print 'dir_of_source=',dir_of_source
        print 'dir_of_target=',dir_of_target
        sys.exit()

    listen_port = int(sys.argv[4])
    print 'command line:'
    print operation,' ',dir_of_source,' ',dir_of_target,' ',listen_port

        
    if operation==OP_PREPROCESS:
        if dir_of_source.find(common.g_sample_log) == -1:
            print 'invalid dir_of_log: ',dir_of_source,' must contains ', common.g_sample_log
            sys.exit()
        if dir_of_target.find(common.g_sample_fet) == -1:
            print 'invalid dir_of_fet: ',dir_of_target,' must contains ', common.g_sample_fet
            sys.exit()
        if dir_of_source[:dir_of_source.find(common.g_sample_log)]!=dir_of_target[:dir_of_target.find(common.g_sample_fet)]:
            print 'dir_of_log and dir_of_fet must share the sample parent directory!'
            sys.exit()
    elif operation==OP_MIST2VECTOR:
        if dir_of_source.find(common.g_sample_fet) == -1:
            print 'invalid dir_of_fet: ',dir_of_source,' must contains ', common.g_sample_fet
            sys.exit()
        if dir_of_target.find(common.g_vector_dir) == -1:
            print 'invalid dir_of_vector: ',dir_of_target, ' must contains ', common.g_vector_dir
            sys.exit()
        if dir_of_source[:dir_of_source.find(common.g_sample_fet)] != dir_of_target[:dir_of_target.find(common.g_vector_dir)]:
            print 'dir_of_fet and dir_of_vector must share the same parent directory!'
            sys.exit()
        if os.path.exists(dir_of_target):
            try:
                os.rmdir(dir_of_target)
            except:
                print 'remove directory failed, any files in it? make sure. dir=',dir_of_target
                exit(-1)
        os.mkdir(dir_of_target)
    elif operation==OP_MERGEFET:
        if dir_of_source.find(common.g_sample_fet) == -1:
            print 'invalid dir_of_fet: ',dir_of_source,' must contains ', common.g_sample_fet
            sys.exit()
        if dir_of_target.find(common.g_feature_dir) == -1:
            print 'invalid dir_of_feture: ',dir_of_target, ' must contains ', common.g_feature_dir
            sys.exit()
        if dir_of_source[:dir_of_source.find(common.g_sample_fet)] != dir_of_target[:dir_of_target.find(common.g_feature_dir)]:
            print 'dir_of_fet and dir_of_feature must share the same parent directory!'
            sys.exit()
        if os.path.exists(dir_of_target):
            try:
                os.rmdir(dir_of_target)
            except:
                print 'remove directory failed, any files in it? make sure. dir=',dir_of_target
                exit(-1)
        os.mkdir(dir_of_target)
    elif operation==OP_MERGETABLE:
        if dir_of_source.find(common.g_sample_table) == -1:
            print 'invalid dir_of_table: ',dir_of_source,' must contains ', common.g_sample_table
            sys.exit()
        if dir_of_target.find(common.g_sample_table) == -1:
            print 'invalid dir_of_target: ',dir_of_target, ' must contains ', common.g_sample_table
            sys.exit()
        if os.path.exists(dir_of_target): 
            try:
                os.rmdir(dir_of_target)
            except:
                print 'remove directory failed, any files in it? make sure. dir=',dir_of_target
                exit(-1)
        os.mkdir(dir_of_target)
    else:
        print 'unexpected operation: ',operation
        sys.exit()

    manager = make_server_manager(listen_port,common.g_auth_key)
    shared_job_q = manager.get_job_q()
    shared_result_q = manager.get_result_q()

    do_process(shared_job_q,shared_result_q,dir_of_source,dir_of_target,operation)

    process_stop_time = time.time()
    print 'process time = %d'%(process_stop_time-g_process_start_time)
    print 'process started at ',g_process_start_readable_time,' stop at ',common.get_readable_time()
    time.sleep(1)
    print 'server shutting down...'
    manager.shutdown()
        

   
