import os
import os.path
import sys
import multiprocessing
from multiprocessing import Process
import traceback

def cleanup_redundance(dir_to_handle):
    file_map = {}
    print 'generating file_map for dir: ',dir_to_handle
    for current_file in os.listdir(dir_to_handle):
        if len(current_file)!=36:
            print 'unexpected MD5 file: ',current_file
            continue
        file_path = os.path.join(dir_to_handle, current_file)
        #print 'processing file: ', file_path
        if os.path.isfile(file_path):
            #do redundance check
            file_size = os.path.getsize(file_path);
            file_lines = len(open(file_path).readlines())
            map_key = '%d' %file_size + '_' + '%d' %file_lines
            if(map_key in file_map):
                file_map[map_key].append(file_path)
                #print 'size_lines already exists'
            else:
                file_map[map_key] = [file_path];
                #print 'new size_line'
        else:
            print 'CleanupRedundance: not a file: ', file_path
            continue
        #end if
    #end for

    print 'deleting duplicated files for dir: ',dir_to_handle
    files_deleted = 0
    redundant_log_handle = open(dir_to_handle+r'/redundant_info.txt','w')
    for dict_key in file_map:
        #print dict_key,' : ',len(file_map[dict_key])
        if len(file_map[dict_key])>1:
            redundant_log_handle.write('1:'+file_map[dict_key][0]+'\n')
        for path_index in range(1, len(file_map[dict_key])):
            #print 'deleting file: ' , file_map[dict_key][path_index]
            os.remove(file_map[dict_key][path_index])
            redundant_log_handle.write('0:'+file_map[dict_key][path_index]+'\n')
        files_deleted += len(file_map[dict_key])-1

    print 'files_deleted = %d, process id = %d' %(files_deleted,os.getpid())
    redundant_log_handle.close()

def cleanup_redundance_worker(job_q,result_q):
    print 'one worker begins, process id=%d' %(os.getpid())
    job = ''
    while True:
        try:
            if job=='':
                job = job_q.get_nowait()
            cleanup_redundance(job)
            result_q.put(job)
            job = ''
        except Exception,e:
            if job_q.empty():
                print 'queue empty, will break, process id=%d'%(os.getpid())
                break
            else:
                print e
                print traceback.format_exc()
                continue

    print 'one worker exit, process id=%d'%(os.getpid())

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'Usage:'
        print '%s parent_dir_of_date num_procs'%sys.argv[0]
        exit(-1)
    parent_dir = sys.argv[1]
    num_procs = int(sys.argv[2])

    dir_list = []
    for current_dir in os.listdir(parent_dir):
        if len(current_dir)!=len('2014_03_21'):
            print 'warning: unexpected date_dir: ',current_dir
            continue
        date_dir = os.path.join(parent_dir, current_dir)
        if os.path.isdir(date_dir):
            dir_list.append(date_dir)
        else:
            print 'warning: not a dir: ', date_dir
            continue

    print 'will process %d directories:'%len(dir_list)
    print dir_list

    job_q = multiprocessing.Queue()
    result_q = multiprocessing.Queue()
    for dir_name in dir_list:
        job_q.put(dir_name)

    procs = []
    for i in range(num_procs):
        p = Process(target=cleanup_redundance_worker,args=(job_q, result_q))
        procs.append(p)
        p.start()

    jobs_processed = 0
    jobs_to_process=len(dir_list)
    while jobs_processed < jobs_to_process:
        processed_job = result_q.get()
        print '\njob processed: ',processed_job
        jobs_processed += 1

    print 'all jobs processed'
    for p in procs:
        p.join()

    print 'exit main.'
