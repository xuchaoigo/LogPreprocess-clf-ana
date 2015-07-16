from __future__ import division
import random
import os
import sys
import time
import string
import numpy as np
import scipy as sp
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn.random_projection import sparse_random_matrix

from scipy import interp
from sklearn.metrics import roc_curve, auc


def svm_test_accuracy(train_file,test_file,result_file):
    start_time=time.clock()
    x_train,y_train = load_svmlight_file(train_file)
    x_test,y_test = load_svmlight_file(test_file) 
    clf = svm.LinearSVC()
    clf.fit(x_train, y_train)
    result_handle=open(result_file,'w')
    try:
        y_test_predict =clf.predict(x_test)
        result_handle.write('%f\n'%(np.mean(y_test_predict==y_test)))
        end_time=time.clock()
        result_handle.write('time consumed:%d\n'%(end_time-start_time))
    except:
        result_handle.write('the size of train not equal to test,failed to predict\n')
    result_handle.close()

def train_and_test(train_dir,test_dir,result_dir):
    train_file_list=os.listdir(train_dir)
    test_file_list=os.listdir(test_dir)
    result_file_list=os.listdir(result_dir)
    for i in range(len(train_file_list)):
        if train_file_list[i] not in result_file_list:
            print 'processing %s'%train_file_list[i]
            svm_test_accuracy(os.path.join(train_dir,train_file_list[i]),os.path.join(test_dir,test_file_list[i]),os.path.join(result_dir,train_file_list[i]))

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'Usage:'
        print sys.argv[0],' train_dir test_dir result_dir'
        sys.exit()

    train_dir = sys.argv[1]
    test_dir = sys.argv[2]
    result_dir = sys.argv[3]
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    train_and_test(train_dir,test_dir,result_dir)
