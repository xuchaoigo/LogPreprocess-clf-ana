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
from sklearn.metrics import confusion_matrix
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectPercentile,f_classif

import time

from scipy import interp
#import pylab as pl
#from pylab import *
#from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import StratifiedKFold


def do():
    print 'loading data'
    #X_train, y_train = load_svmlight_file("sparse_input.log")    
    #X_train, y_train = load_svmlight_file("svm_train_17w.log")    
    #X_train, y_train = load_svmlight_file("sparse_input_100w.log")    
    #X_train, y_train = load_svmlight_file("GetUniq_100w_new_input.txt")    
    X_train, y_train = load_svmlight_file("vec_itr_f_multi_1230.log.uniq.final")
    #X_test, y_test = load_svmlight_file("svm_test.log", n_features=X_train.shape[1])

    startime= time.clock()
    print 'fs start'
   
    ''' 
    th=0.7
    print 'v start,',th
    print '1:',X_train.shape

    sel = VarianceThreshold(threshold=(th * (1 - th)))
    X_train=sel.fit_transform(X_train)
    print '2:',X_train.shape
    X_train=X_train.toarray()
    
    fstime = time.clock()
    print 'fs end,time=%fs'%(fstime-startime)
    '''
  
    print 'cv start,print cm:'

    clf = svm.LinearSVC()
    #clf = tree.DecisionTreeClassifier()
    #clf = RandomForestClassifier(n_estimators=10)

    fold=10
    cv = StratifiedKFold(y_train, fold)
    all_tpr = []
    fp=0.0
    fn=0.0

    for i, (train, test) in enumerate(cv):
        y_pred = clf.fit(X_train[train], y_train[train]).predict(X_train[test])
        print 'fold ',i
        print type(y_pred)
        print 'y_train=',y_train[test].shape
        print 'y_pred=',y_pred.shape
        cm=confusion_matrix(y_train[test], y_pred)
        print cm
        #fp+=cm[1][0]
        #fn+=cm[0][1]
        #print '%d,%d'%(fp,fn)
    #fp=fp/fold
    #fn=fn/fold

    predtime = time.clock()
    print 'predict end,time=%fs'%(predtime-startime)
    
do()
