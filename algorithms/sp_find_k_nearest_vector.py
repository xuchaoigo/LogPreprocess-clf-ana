# -*- coding: cp936 -*-
import os
import sys
import time
import numpy
from sklearn.neighbors import KDTree
from sklearn.datasets import load_svmlight_file
from sklearn.neighbors import NearestNeighbors

def find_knn(target_vec, list_of_vec):
    if target_vec=="":
        print 'empty vec!'
        return
    print 'target=',target_vec
    
    return 

if __name__ == '__main__':
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
    nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='ball_tree').fit(X_train)
    distances, indices = nbrs.kneighbors(X_train)
    for vec in xrange(X_train.shape[0]):
            num_posi = 0
            num_nega = 0
            for x in xrange(1,num_neighbors):
                if y_train[indices[vec][x]]==1:
                    num_posi+=1
                elif y_train[indices[vec][x]]==-1:
                    num_nega+=1
            target_label = y_train[vec]
            THRESHOLD = (num_neighbors-1)*0.1
            if target_label== -1 and num_nega <= THRESHOLD:
                print 'self label=%d'%target_label
                os.system('touch index_knn_sp/%d.knn'%vec)
                #write_handle = open('./sp_index.knn','a')
                #write_handle.write('%d\n'%indices[vec][x])
                #write_handle.close()
                #for x in xrange(1,num_neighbors):
                #    print '%d,%d'%(y_train[indices[vec][x]],indices[vec][x])
            
            if target_label== 1 and num_posi <= THRESHOLD:
                print 'self label=%d'%target_label
                os.system('touch index_knn_sp/%d.knn'%vec)
                #write_handle = open('./sp_index.knn','a')
                #write_handle.write('%d\n'%indices[vec][x])
                #write_handle.close()
                #for x in xrange(1,num_neighbors):
                #    print '%d,%d'%(y_train[indices[vec][x]],indices[vec][x])
    end_time = time.time()
    print 'calc end,time=%fs'%(end_time-load_time)
    
    """
    read_h = open('sp_index.knn','r')
    write_h = open('sp_index.knn.uniq','w')
    lines = read_h.readlines()
    vecset=set()
    for vec in lines:
        vecset.add(vec)
    for vec_uniq in vecset:
        write_h.write('%s'%vec_uniq)
    """
