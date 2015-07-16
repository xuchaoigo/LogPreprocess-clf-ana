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
    nbrs = NearestNeighbors(n_neighbors=num_neighbors, algorithm='kd_tree').fit(X_train)
    distances, indices = nbrs.kneighbors(X_train)
    i=0
    print distances[i]
    print indices[i]
    print '(label,neighbor_index)='
    for x in xrange(1,num_neighbors):
        print '%d,%d'%(y_train[indices[i][x]],indices[i][x])

    end_time = time.time()
    print 'calc end,time=%fs'%(end_time-load_time)
    
