from __future__ import division
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
import pylab as pl
from pylab import *
from sklearn.metrics import roc_curve, auc
from sklearn.cross_validation import StratifiedKFold


def cross_n_validation(vector_file,result_file,n_fold):
    print 'loading data'
    X_train, y_train = load_svmlight_file(vector_file)

    startime= time.clock()
    print 'cv start,print cm:'
    clf = svm.LinearSVC()

    fold=n_fold
    cv = StratifiedKFold(y_train, fold)
    all_tpr = []
    fp=0
    fn=0
    total_white = 0
    total_black = 0
    for i, (train, test) in enumerate(cv):
        y_pred = clf.fit(X_train[train], y_train[train]).predict(X_train[test])
        print 'fold ',i
        print type(y_pred)
        print 'y_train=',y_train[test].shape
        print 'y_pred=',y_pred.shape
        cm=confusion_matrix(y_train[test], y_pred)
        print cm
        total_black += cm[0][0]
        total_black += cm[0][1] 
        total_white += cm[1][0]
        total_white += cm[1][1]
        fp+=cm[1][0]
        fn+=cm[0][1]
        print '%d,%d'%(fp,fn)

    result_handle=open(result_file,'w')
    result_handle.write('fp=%d,fn=%d\n'%(fp,fn))
    result_handle.write('wubao=%f,loubao=%f'%(fp/total_white,fn/total_black))
    result_handle.close()
    predtime = time.clock()
    print 'predict end,time=%fs'%(predtime-startime)
    



def process(vector_dir,result_dir,n_fold):
    vector_file_list=os.listdir(vector_dir)
    for vector_file in vector_file_list:
        print 'process %s'%vector_file
        cross_n_validation(os.path.join(vector_dir,vector_file),os.path.join(result_dir,vector_file),n_fold)

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'Usage:'
        print sys.argv[0], ' vector_dir,result_dir, num_of_fold'
        sys.exit()
    vector_dir=sys.argv[1]
    result_dir=sys.argv[2]
    n_fold=int(sys.argv[3])
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    process(vector_dir,result_dir,n_fold)
