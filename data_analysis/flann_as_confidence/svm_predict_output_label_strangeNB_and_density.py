# -*- coding: cp936 -*-
import os
import sys
import time
import numpy
from numpy import *
from numpy.random import * 
import numpy as np 
from sklearn.decomposition import TruncatedSVD 
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from pyflann import *

def split_md5_vector(md5_vector_file):
    suffix=md5_vector_file#[0:md5_vector_file.find('md5')-1]
    vector_file='%s.vector'%suffix
    print vector_file
    md5_list=[]
    md5_vector_handle=open(md5_vector_file,'r')
    vector_handle=open(vector_file,'w')
    cnt = 0
    for line in md5_vector_handle:
        cnt +=1
        line=line.strip('\n')
        medium=line.find(' ')
        md5=line[0:medium]
        vector=line[medium+1:]
        vector_handle.write('%s\n'%vector)
        md5_list.append(md5)
    print 'process %d vecs'%cnt
    return vector_file,md5_list

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],'train_vector_file  test_vector_file  num_neighbor'
        print 'train_vec_file does NOT contain md5!'
        print 'test_vec_file does contain md5!'
        print 'num_neighbor = 20 is good'
        exit(-1)
    if int(sys.argv[3])>100:
        print 'we think num>100 is meaningless'
        exit(1)
    test_vec_file_without_md5,md5_list = split_md5_vector(sys.argv[2])

    start_time = time.time()
    print 'loading train data...'
    X_train, y_train = load_svmlight_file(sys.argv[1] )
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    print 'loading test data...'
    X_test, y_test = load_svmlight_file(test_vec_file_without_md5,n_features=X_train.shape[1])
    print 'X_test.shape=',X_test.shape
    print 'y_test.shape=',y_test.shape
    print 'test data loaded.'
    
    clf = svm.LinearSVC()
    y_pred = clf.fit(X_train, y_train).predict(X_test)
    print 'y_pred.shape=',y_pred.shape   
    print y_pred
    distance = clf.decision_function(X_test)
    print 'distance.shape=',distance.shape   
    
    ##########################
    print 'start find neighbor...'
    print 'SVD input train_set shape:',X_train.shape
    print 'SVD input test_set shape:',X_test.shape
    svd = TruncatedSVD(n_components=500, random_state=42)
    svd.fit(X_train) 
    TruncatedSVD(algorithm='randomized', n_components=500, n_iter=5,
            random_state=42, tol=0.0)
    print 'SVD var percent=',(svd.explained_variance_ratio_.sum())
    X_train_svd = svd.transform(X_train)
    X_test_svd = svd.transform(X_test)
    print 'SVD output train shape:',X_train_svd.shape
    print 'SVD output test shape:',X_test_svd.shape
    
    num_neighbors = int(sys.argv[3])+1
    if num_neighbors%10 != 1:
        print 'invalid num_neighbors'
    density_num_neighbors = 101
    threshold_neighbourhood_list = [0.0001,0.001,0.01,0.1,1,10,100,1000,10000,100000]
    print 'num_neighbors=',num_neighbors
    print 'density_num_neighbors=',density_num_neighbors
    print 'threshold_neighbourhood=',threshold_neighbourhood_list

    flann = FLANN()
    indices,dists = flann.nn(X_train_svd,X_test_svd,density_num_neighbors,algorithm="kmeans",target_precision=0.999,
branching=32, iterations=7, checks=16);
    print indices
    print 'indices shape=',indices.shape
    print dists
    print 'dists shape=',dists.shape
    y_strangeNB=[]
    y_density=[]
    for vec in xrange(X_test_svd.shape[0]):
            num_posi = 0
            num_nega = 0
            if vec%5000 == 0:
                print 'prcess %d vec'%vec
            
            #calc density
            num_list = []
            for one_threshold in threshold_neighbourhood_list:
                num_in_this_neighborhood = 0
                for x in xrange(1,density_num_neighbors):
                    if dists[vec][x] < one_threshold:
                        num_in_this_neighborhood+=1
                    else:
                        break         
                num_list.append(num_in_this_neighborhood)       
            y_density.append(num_list)
            #calc strange neighbor
            for x in xrange(1,num_neighbors):
                if y_train[indices[vec][x]]==1:
                    num_posi+=1
                elif y_train[indices[vec][x]]==-1:
                    num_nega+=1
            target_label = int(y_pred[vec])
            if target_label== -1:
                y_strangeNB.append(num_posi)
            if target_label== 1:
                y_strangeNB.append(num_nega)
    print 'y_strangeNB len=',len(y_strangeNB)

    result_file_handle=open('%s.density.%d'%(sys.argv[2],num_neighbors),'w')
    for i in xrange(y_test.shape[0]):    
        if int(y_pred[i])==1:
            orig_level = 100
        elif int(y_pred[i])==-1:        
            orig_level = 200
        result_file_handle.write('%s,%d,%f,%d,'%(md5_list[i],orig_level,float(distance[i]),y_strangeNB[i]))
        for num_in_this_neighborhood in y_density[i]:
            result_file_handle.write('%d '%num_in_this_neighborhood)
        result_file_handle.write('\n')
    #file 2 mysql
    """
    result_file_handle=open('%s.result'%sys.argv[2],'r')    
    result_list =[]
    for line in result_file_handle:
        md5,level = line.split(',')
        result_list.append((md5,level))
    set_predict_result(result_list)          
    """
    pred_time = time.time()
    print 'predict end,time=%fs'%(pred_time-start_time)
