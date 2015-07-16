# -*- coding: cp936 -*-
import os
import sys
import string
import numpy as np
import scipy as sp
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.feature_selection import VarianceThreshold
from sklearn.random_projection import sparse_random_matrix
from sklearn.metrics import confusion_matrix
import time
from sklearn.cross_validation import StratifiedKFold

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'svm_train_vec svm_output_vec'
        print 'svm_train_vec and svm_train_vec_dir MUST be corresponding'
        exit(-1)
    print 'loading data'
    X_train, y_train = load_svmlight_file(sys.argv[1])    
    #X_test, y_test = load_svmlight_file("iterB_2Gram_Weight_1w.log.uniq.final")    
    #X_test, y_test = load_svmlight_file("svm_train_mships_fp_batch2.log",n_features=X_train.shape[1])

    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'
    startime= time.clock()
    print 'fs start'
    fstime = time.clock()
    print 'fs end,time=%fs'%(fstime-startime)
  
    _cv='''
    print 'cv start,print cm:'
    #clf = svm.SVC()
    #clf = joblib.load('iterB_2Gram_Weight_1w.log.uniq.final.model') 
    clf = svm.LinearSVC()
    #clf = tree.DecisionTreeClassifier()
    #clf = RandomForestClassifier(n_estimators=10)
 
    fold=5
    cv = StratifiedKFold(y_train, fold)
    all_tpr = []
    fp=0.0;
    fn=0.0;
    for i, (train, test) in enumerate(cv):
        y_pred = clf.fit(X_train[train], y_train[train]).predict(X_train[test])
    # Compute confusion matrix
        print 'fold ',i
        print type(y_pred)
        print 'y_train=',y_train[test].shape
        print 'y_pred=',y_pred.shape
        cm=confusion_matrix(y_train[test], y_pred)
        print cm
        fp+=cm[1][0]
        fn+=cm[0][1]
        print '%d,%d'%(fp,fn)
    fp=fp/fold
    fn=fn/fold
    print 'fp=',(fp/len(y_pred))
    print 'fn=',(fn/len(y_pred))
    print 'accur=',1-(fp/len(y_pred))-(fn/len(y_pred))
    

    #scores=cross_validation.cross_val_score(clf,X_train,y_train,cv=5,scoring="accuracy")
    #print(scores,scores.mean())
    #cv end
    #'''

    #_svm='''
    print 'SVM trainning start'
    clf = svm.LinearSVC()
    clf.fit(X_train, y_train)
    print 'SVM predicting start'

    num_tp=0.0
    num_tn=0.0
    num_fp=0.0
    num_fn=0.0
    cnt = 0
    THRESHOLD = 2
    write_retrain_vec = open(sys.argv[2], 'w')

    X_test, y_test = load_svmlight_file(sys.argv[1],n_features=X_train.shape[1])
    print 'X_test.shape=',X_test.shape
    print 'Y_test.shape=',y_test.shape
    print 'test data loaded.'

    y_pred = clf.predict(X_test)
    distance = clf.decision_function(X_test)
    print 'y_pred.shape=',y_pred.shape
    print 'distance.shape=',distance.shape

    
    error_list=[]    
    vec_size = y_pred.size    
    print 'size=',vec_size
    for i in xrange (0,vec_size):     
        flag_wrong_result = False
        resultr = '%dto%d'%(y_test[i], y_pred[i]) 
        if resultr == '1to1':
            num_tn+=1            
        elif resultr == '1to-1':
            num_fp+=1
            flag_wrong_result = True            
        elif resultr == '-1to-1':
            num_tp+=1            
        elif resultr == '-1to1':
            num_fn+=1            
            flag_wrong_result = True            
        #print '%dto%d, cnt=%d'%(y_test[i], y_pred[i],cnt)
        cnt+=1
        if cnt%10000 ==0:
            print 'predict:',cnt
        if flag_wrong_result == True:
            if abs(distance[i]) > THRESHOLD:
                error_list.append(i)

    print 'len of error_list=',len(error_list)
    full_list=range(X_train.shape[0])
    reserve_list=list(set(full_list)-set(error_list))
    X_train_new = X_train[reserve_list]
    y_train_new = np.delete(y_train,error_list)

    print 'X_train_new.shape=',X_train_new.shape
    print 'len of error_list=',len(error_list)
    dump_svmlight_file(X_train_new,y_train_new,sys.argv[2],zero_based=False)
    print '----> vector predict end!'
    print 'tn=',num_tn
    print 'fp=',num_fp
    print 'tp=',num_tp
    print 'fn=',num_fn

    #print y_pred
    #print y_test
    print 'SVM predict end'
    print 'fp per=%f'%(num_fp/(num_fp+num_tn))
    print 'fn per=%f'%(num_fn/(num_fn+num_tp))
    #print "Accuracy", np.mean(y_pred == y_test)
    
    predtime = time.clock()
    print 'predict end,time=%fs'%(predtime-startime)
    
