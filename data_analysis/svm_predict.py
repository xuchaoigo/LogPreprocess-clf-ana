# -*- coding: cp936 -*-
import os
import sys
import time
import numpy
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import StratifiedKFold

def split_md5_vector(md5_vector_file):
    suffix=md5_vector_file#[0:md5_vector_file.find('md5')-1]
    md5_file='%s.md5'%suffix
    print md5_file
    vector_file='%s.vector'%suffix
    print vector_file
    md5_vector_handle=open(md5_vector_file,'r')
    md5_handle=open(md5_file,'w')
    vector_handle=open(vector_file,'w')
    cnt = 0
    for line in md5_vector_handle:
        cnt +=1
        line=line.strip('\n')
        medium=line.find(' ')
        md5=line[0:medium]
        vector=line[medium+1:]
        md5_handle.write('%s\n'%md5)
        vector_handle.write('%s\n'%vector)
    print 'process %d vecs'%cnt
    return vector_file,md5_file


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'sparse_train_vector_file sparse_test_vector_file'
        exit(-1)
    start_time = time.time()
    test_vec_file_without_md5,md5_file = split_md5_vector(sys.argv[2])
    print 'loading train data...'
    train_vector = sys.argv[1]
    X_train, y_train = load_svmlight_file(train_vector)
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    print 'loading test data...'
    X_test, y_test = load_svmlight_file(test_vec_file_without_md5,n_features=X_train.shape[1])
    print 'X_test.shape=',X_test.shape
    print 'y_test.shape=',y_test.shape
    print 'test data loaded.'
    
    clf = svm.LinearSVC()
    fp=0.0
    fn=0.0
    all_positive = 0.0
    all_negative = 0.0

    y_pred = clf.fit(X_train, y_train).predict(X_test)
    cm=confusion_matrix(y_test, y_pred)
    print cm
    fp+=cm[1][0]
    fn+=cm[0][1]
    all_positive += (cm[0][0]+cm[0][1])
    all_negative += (cm[1][0]+cm[1][1])
    
    if all_positive == 0 and all_negative != 0:
        print 'fp_percent=%f'%(fp/all_negative*100)
    elif all_positive != 0 and all_negative == 0:
        print 'fn_percent=%f'%(fn/all_positive*100)
    else:
        print 'fp_percent=%f,fn_percent=%f'%(fp/all_negative*100,fn/all_positive*100)

    pred_time = time.time()
    print 'predict end,time=%fs'%(pred_time-start_time)
