# -*- coding: cp936 -*-
import os
import sys
import time
import multiprocessing
from multiprocessing import Process,Pool,Manager
import numpy as np
from sklearn.neighbors import KDTree
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file
from sklearn.neighbors import NearestNeighbors

def find_knn(X_sub,y_train,index_offset,error_list):
    print 'num_neighbors=',num_neighbors
    print 'X_sub.shape=',X_sub.shape
    print 'y_train.shape=',y_train.shape
    distances, indices = nbrs.kneighbors(X_sub)
    print 'knn finished,indices.shape=',indices.shape
    THRESHOLD = (num_neighbors-1)*0.1
    print 'THRESHOLD=',THRESHOLD
    for vec in xrange(X_sub.shape[0]):
            num_posi = 0
            num_nega = 0
            for x in xrange(1,num_neighbors):
                if y_train[indices[vec][x]]==1:
                    num_posi+=1
                elif y_train[indices[vec][x]]==-1:
                    num_nega+=1
            target_label = y_train[vec+index_offset]
            if target_label== -1 and num_nega <= THRESHOLD:
                #print 'self label=%d'%target_label
                #print 'self index=%d'%(vec+index_offset)
                #os.system('touch index_knn_chunk/%d.knn'%(vec+index_offset))
                error_list.append(vec+index_offset)
                #for x in xrange(1,num_neighbors):
                #    print '%d,%d'%(y_train[indices[vec][x]],indices[vec][x])
            
            if target_label== 1 and num_posi <= THRESHOLD:
                #print 'self label=%d'%target_label
                #print 'self index=%d'%(vec+index_offset)
                #os.system('touch index_knn_chunk/%d.knn'%(vec+index_offset))
                error_list.append(vec+index_offset)
                #for x in xrange(1,num_neighbors):
                #    print '%d,%d'%(y_train[indices[vec][x]],indices[vec][x])

def parallel_process_pool(X_train,y_train,num_tasks,nbrs,num_neighbors,error_list):
    print '%d vectors in X_train.'%X_train.shape[0]
    server = multiprocessing.Manager()
    vec_list = []
    label_list = []
    for i in xrange(X_train.shape[0]):
        vec_list.append(X_train[i])
        label_list.append(y_train[i])
 
    num_vecs = int(X_train.shape[0]/num_tasks)
    worker_list = []
    for task in range(0,num_tasks):
        current_vec_list = []
        if task < num_tasks - 1:
            print '[%d,%d],task %d'%(task*num_vecs, (task+1)*num_vecs,task)
            X_sub = X_train[task*num_vecs:(task+1)*num_vecs]
        else:
            print '[%d,%d],task %d'%(task*num_vecs, (task+1)*num_vecs,task)
            X_sub = X_train[task*num_vecs:]
        
        index_offset = task*num_vecs
        worker = Process(target=find_knn,args=(X_sub, y_train, index_offset,error_list))
        worker.start()
        worker_list.append(worker)
        print 'Task %d invoked.'%task    
    
    for worker in worker_list:
        worker.join()
        print 'one worker exit.'

if __name__ == '__main__':
    global nbrs
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'train_vector_file output_vec_file'
        exit(-1)
    start_time = time.time()
    print 'loading train data...'
    X_train, y_train = load_svmlight_file(sys.argv[1])
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    load_time = time.time()
    print 'load_time=%fs'%(load_time-start_time)
    num_neighbors = 11
    num_procs = 11
    nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='kd_tree').fit(X_train)
    object_manager = Manager()
    error_list = object_manager.list()
    parallel_process_pool(X_train,y_train,num_procs,nbrs,num_neighbors,error_list)
    end_time = time.time()
    print 'calc end,time=%fs'%(end_time-load_time)
    
    print 'len of error_list=',len(error_list)
    print error_list
    full_list=range(X_train.shape[0])
    reserve_list=list(set(full_list)-set(error_list))
    X_train_new = X_train[reserve_list]
    y_train_new = np.delete(y_train,error_list)
    dump_svmlight_file(X_train_new,y_train_new,sys.argv[2],zero_based=False)
    


