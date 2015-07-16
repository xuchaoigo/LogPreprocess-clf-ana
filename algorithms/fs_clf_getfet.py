# -*- coding: cp936 -*-
import os
import sys
import string
import numpy as np
import scipy as sp
from sklearn import svm
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn import tree
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import TruncatedSVD
from sklearn.random_projection import sparse_random_matrix

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectPercentile,f_classif

import time

def do():
    print 'loading data'
    #X_train, y_train = load_svmlight_file("sparse_input.log")    
    #X_train, y_train = load_svmlight_file("GetDict_80w_new_input.txt")    
    X_train, y_train = load_svmlight_file("GetUniq_100w_new_input.txt")    
    #X_test, y_test = load_svmlight_file("svm_test.log", n_features=X_train.shape[1])

    startime= time.clock()
    print 'fs start'
    _tree='''
    print 'tree start'
    print '1:',X_train.shape
    clf_tree = ExtraTreesClassifier()
    X_train = clf_tree.fit(X_train.toarray(), y_train).transform(X_train)
    print '2:',X_train.shape
    #X_train_tree = sp.sparse.csr_matrix(X_new_tree)
    #'''
    
    #_threshold='''
    th=0.99
    print 'v start,threshold=',th
    print '1:',X_train.shape

    sel = VarianceThreshold(threshold=(th * (1 - th)))
    X_train=sel.fit_transform(X_train)
    print '2:',X_train.shape
    X_train=X_train.toarray()
    #print sel.variances_

    fet_got = sel.get_support(True)
    print type(fet_got)
    str=''
    for it in fet_got:
        str+='%d,'%it 
    print str
    return
    #'''
    _Kbest='''
    num=180
    print '_Kbest,',num
    print X_train.shape
    X_train = SelectKBest(chi2, k=num).fit_transform(X_train, y_train)
    print X_train.shape
    X_train=X_train.toarray()
    #'''
    _Kper='''
    print X_train.shape
    X_train = SelectPercentile(f_classif, percentile=10).fit_transform(X_train, y_train)
    print X_train.shape
    
    #'''

    _svd='''
    print 'PCA+RF 1:',X_train.shape
    svd = TruncatedSVD(n_components=500, random_state=42)
    svd.fit(X_train) 
    TruncatedSVD(algorithm='randomized', n_components=500, n_iter=5,
            random_state=42, tol=0.0)
    print 'var percent=',(svd.explained_variance_ratio_.sum())

    X_train = svd.transform(X_train)
    #X_test = svd.transform(X_test)
    
    print '2:',X_train.shape
    #print '2:',X_test.shape
    #'''
    
    fstime = time.clock()
    print 'fs end,time=%fs'%(fstime-startime)
  
    #_cv='''
    print 'cv start,LSVM'
    #clf = svm.SVC()
    #clf = svm.LinearSVC()
    #clf = tree.DecisionTreeClassifier()
    clf = RandomForestClassifier(n_estimators=10)
    scores=cross_validation.cross_val_score(clf,X_train,y_train,cv=5,scoring="accuracy")
    print(scores,scores.mean())
    #cv end
    #'''

    _svm='''
    print 'SVM trainning start'
    clf = svm.SVC()
    clf.fit(X_train, y_train)
    print 'SVM predicting start'

    y_pred = clf.predict(X_train)
    print y_pred
    print y_train
    print 'SVM predict end'
    print "Accuracy", np.mean(y_pred == y_train)
    #'''

    _dtm='''
    print 'DTM train start'
    clf = tree.DecisionTreeClassifier()
    #pca出来的是dense的，否则X.toarray()
    clf.fit(X_train, y_train)
    print 'DTM predict start'
    traintime = time.clock()
    print 'trainning end, time=%fs'%(traintime-startime)
    y_pred = clf.predict(X_train)
    #print y_pred
    print 'DTM predict end'
    print "Accuracy", np.mean(y_pred == y_train)
   # '''
    
    predtime = time.clock()
    print 'predict end,time=%fs'%(predtime-startime)
    
do()
