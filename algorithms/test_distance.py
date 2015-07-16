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
import matplotlib
import matplotlib.pyplot as plt
from pylab import *
import matplotlib.pyplot as plt


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'svm_train_vec svm_test_vec'
        exit(-1)
    print 'loading data'
    X_train, y_train = load_svmlight_file(sys.argv[1])    
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'
    X_test, y_test = load_svmlight_file(sys.argv[2],n_features=X_train.shape[1])
    print 'X_test.shape=',X_test.shape
    print 'Y_test.shape=',y_test.shape
    print 'test data loaded.'
    startime= time.clock()
    print 'fs start'
    fstime = time.clock()
    print 'fs end,time=%fs'%(fstime-startime)
  
    print 'SVM trainning start'
    clf = svm.LinearSVC()
    clf.fit(X_train, y_train)
    print 'SVM predicting start'

    num_tp=0.0
    num_tn=0.0
    num_fp=0.0
    num_fn=0.0
    cnt = 0
    y_pred = clf.predict(X_test)
    distance = clf.decision_function(X_test)
    print 'y_pred.shape=',y_pred.shape
    print 'distance.shape=',distance.shape
    dist_dict={}
    for d in distance:
        if int(d) in dist_dict:
            dist_dict[int(d)]+=1
        else:
            dist_dict[int(d)]=1

    dist_dict = sorted(dist_dict.items(), key=lambda d: d[0]) 
    file_handle=open('distance_of_%s'%sys.argv[2],'w')
    for v in dist_dict:
        file_handle.write('%d: num = %d\n'%(v[0],v[1]))
    file_handle.close()    

    vec_size = y_pred.size    
    print 'size=',vec_size
    for i in xrange (0,vec_size): 
        cnt +=1
        if cnt %10000==0:
            print 'cnt = ',cnt   
        resultr = '%dto%d'%(y_test[i], y_pred[i]) 
        if resultr == '1to1':
            num_tn+=1            
        elif resultr == '1to-1':
            num_fp+=1
        elif resultr == '-1to-1':
            num_tp+=1            
        elif resultr == '-1to1':
            num_fn+=1            
    
    print '---->%s predict end!'%(sys.argv[1])
    print 'tn=',num_tn
    print 'fp=',num_fp
    print 'tp=',num_tp
    print 'fn=',num_fn

    print 'SVM predict end'
    print 'fp per=%f'%(num_fp/(num_fp+num_tn))
    print 'fn per=%f'%(num_fn/(num_fn+num_tp))
    #print "Accuracy", np.mean(y_pred == y_test)
    """
    total_num = distance.shape[0]
    plot_num = 3000
    total_sequence=range(total_num)
    plot_sequence=random.sample(total_sequence,plot_num)
    distance_plot = distance[plot_sequence]
    x=arange(0,plot_num,1)
    plot(x,distance_plot,linewidth=1.0)
    xlabel("sample")
    ylabel("distance")
    grid(True)
    show()
    savefig('distance_%s_random.png'%(sys.argv[1]))
    print 'save figure to ./distance_%s.png'%sys.argv[1]
    print 'plot_num = %d'%(plot_num)
    """
    predtime = time.clock()
    print 'predict end,time=%fs'%(predtime-startime)
    
