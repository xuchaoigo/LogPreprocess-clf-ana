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


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'sparse_train_vector_file sparse_test_vector_file'
        exit(-1)
    start_time = time.time()
    print 'loading train data...'
    train_vector = sys.argv[1]
    X_train, y_train = load_svmlight_file(train_vector)
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    test_vector = sys.argv[2]
    print 'loading test data...'
    X_test, y_test = load_svmlight_file(test_vector,n_features=X_train.shape[1])
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
