# -*- coding: cp936 -*-
import os
import sys
import time
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import StratifiedKFold


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],'sparse_vector_file'
        exit(-1)
    print 'loading data...'
    sparse_vector = sys.argv[1]
    X_train, y_train = load_svmlight_file(sparse_vector)
    print 'data loaded.'
    
    start_time = time.clock() 
    print 'cv start,print cm:'
    clf = svm.LinearSVC()
    fold = 10
    cv = StratifiedKFold(y_train, fold)
    all_tpr = []
    fp=0.0
    fn=0.0
    all_positive = 0.0
    all_negative = 0.0

    for i, (train, test) in enumerate(cv):
        y_pred = clf.fit(X_train[train], y_train[train]).predict(X_train[test])
        print 'fold ',i
        print 'y_train=',y_train[test].shape
        print 'y_pred=',y_pred.shape
        cm=confusion_matrix(y_train[test], y_pred)
        print cm
        fp+=cm[1][0]
        fn+=cm[0][1]
        all_positive += (cm[0][0]+cm[0][1])
        all_negative += (cm[1][0]+cm[1][1])
        print 'fp_percent=%f,fn_percent=%f'%(fp/all_negative*100,fn/all_positive*100)

    pred_time = time.clock()
    print 'predict end,time=%fs'%(pred_time-start_time)
