# -*- coding: cp936 -*-
import os
import sys
import time
import numpy as np
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'sparse_train_vector_file selected_index_file'
        exit(-1)
    start_time = time.time()
    print 'loading train data...'
    train_vector = sys.argv[1]
    X_train, y_train = load_svmlight_file(train_vector)
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    fs = SelectKBest(chi2, k=50000)
    #fs = LinearSVC(C=1, penalty="l1", dual=False, class_weight='auto')
    X_train_new = fs.fit_transform(X_train, y_train)
    print 'X_new.shape=',X_train_new.shape
    selected_feature = fs.get_support(indices=True)
    print selected_feature
    handle = open(sys.argv[2], 'w')
    for index in selected_feature:
        handle.write('%d\n'%index)
    print 'write selected index to:',sys.argv[2]
    #dump_svmlight_file(X_train_new,y_train,sys.argv[2],zero_based=False)

    pred_time = time.time()
    print 'predict end,time=%fs'%(pred_time-start_time)
