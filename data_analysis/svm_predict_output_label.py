# -*- coding: cp936 -*-
import os
import sys
import time
import numpy
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file

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
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'train_vector_file test_vector_file'
        print 'train_vec_file does NOT contain md5!'
        print 'test_vec_file does contain md5!'
        exit(-1)
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
    
    result_file_handle=open('%s.result'%sys.argv[2],'w')
    #output md5 and it's level
    for i in xrange(y_test.shape[0]):    
        if int(y_pred[i])==1:
            result_file_handle.write('%s,%d,%f\n'%(md5_list[i],100,float(distance[i])))        
        elif int(y_pred[i])==-1:        
            result_file_handle.write('%s,%d,%f\n'%(md5_list[i],200,float(distance[i])))
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
