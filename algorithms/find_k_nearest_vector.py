# -*- coding: cp936 -*-
import os
import sys
import time
import multiprocessing
from multiprocessing import Process,Pool
import numpy
from sklearn.neighbors import KDTree
from sklearn.datasets import load_svmlight_file
from sklearn.neighbors import NearestNeighbors

def find_knn((target_vec,target_label)):
    distances, indices = nbrs.kneighbors(target_vec)
    #print distances[i]
    #print indices[i]
    """
    print '(label,neighbor_index)='
    for x in xrange(1,num_neighbors):
        print '%d,%d'%(y_train[indices[i][x]],indices[i][x])
    """
    num_posi = 0
    num_nega = 0
    for x in xrange(1,num_neighbors):
        if y_train[indices[0][x]]==1:
            num_posi+=1
        elif y_train[indices[0][x]]==-1:
            num_nega+=1
    THRESHOLD = (num_neighbors-1)*0.1
    if target_label== -1 and num_nega <= THRESHOLD:
        #print 'self label=%d'%target_label
        #output_index_list.append(indices[0][x])
        os.system('touch index_knn_pool/%d.knn'%indices[0][0])
        """
        write_handle = open('index_knn/%d.knn'%indices[0][x],'w')
        write_handle.write('%d '%indices[0][x])
        write_handle.close()
        """
        #for x in xrange(1,num_neighbors):
        #    print '%d,%d'%(y_train[indices[0][x]],indices[0][x])
    
    if target_label== 1 and num_posi <= THRESHOLD:
        #print 'self label=%d'%target_label
        #output_index_list.append(indices[0][x])
        os.system('touch index_knn_pool/%d.knn'%indices[0][0])
        """
        write_handle = open('index_knn/%d.knn'%indices[0][x],'w')
        write_handle.write('%d '%indices[0][x])
        write_handle.close()
        """
        #for x in xrange(1,num_neighbors):
        #    print '%d,%d'%(y_train[indices[0][x]],indices[0][x])
    

def parallel_process_pool(X_train,y_train,num_tasks,nbrs,num_neighbors):
    print '%d vectors in X_train.'%X_train.shape[0]
    server = multiprocessing.Manager()
    vec_list = []
    label_list = []
    output_index_list = server.list()
    for i in xrange(X_train.shape[0]):
        vec_list.append(X_train[i])
        label_list.append(y_train[i])
        
    process_pool = Pool(processes=num_tasks)
    process_pool.map(find_knn,zip(vec_list,label_list))
    process_pool.close()    
    process_pool.join()    
    print 'len of output_index_list=',len(output_index_list)

if __name__ == '__main__':
    global nbrs
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],'train_vector_file'
        exit(-1)
    start_time = time.time()
    print 'loading train data...'
    train_vector = sys.argv[1]
    X_train, y_train = load_svmlight_file(train_vector)
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    load_time = time.time()
    print 'load_time=%fs'%(load_time-start_time)
    #kdt = KDTree(X_train.todense(), leaf_size=30, metric='euclidean')
    #print kdt.query(X_train.todense(), k=3, return_distance=True)  
    num_neighbors = 11
    num_procs = 11
    nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='kd_tree').fit(X_train)
    #target_vec = X_train[3]
    #target_label = y_train[3]
    #find_knn(target_vec,target_label, nbrs)
    parallel_process_pool(X_train,y_train,num_procs,nbrs,num_neighbors)
    end_time = time.time()
    print 'calc end,time=%fs'%(end_time-load_time)
    """
    read_h = open('index.knn','r')
    write_h = open('index.uniq.knn','w')
    line = read_h.readline()
    veclist = line.split(' ')
    vecset=set()
    for vec in veclist:
        vecset.add(vec)
    for vec_uniq in vecset:
        write_h.write('%s '%vec_uniq)
    """
