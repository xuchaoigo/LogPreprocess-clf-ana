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


def svm_test_accuracy(x_train,y_train,x_test,y_test):
    clf = svm.LinearSVC()
    clf.fit(x_train, y_train)
    y_train_predict =clf.predict(x_train)
    y_test_predict =clf.predict(x_test)

    result_handle=open('result_accuracy.txt','a')
    result_handle.write('%d\n'%x_train.shape[0])
    result_handle.write('%f,%f\n'%(np.mean(y_train_predict==y_train),np.mean(y_test_predict==y_test)))
    result_handle.close()

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print sys.argv[0],' vec.uniq.final_file'
        exit(-1)

    vector_file = sys.argv[1]

    start_time=time.clock()
    x_total, y_total = load_svmlight_file(vector_file)
    [row,col]=x_total.shape

    total_num=row
    print 'total num:%d'%total_num
    begin=5000
    interval=5000
    test_num=200000

    total_sequence=range(total_num)
    test_sequence=random.sample(total_sequence,test_num)
    train_sequence=list( set(total_sequence)-set(test_sequence) )

    x_test=x_total[test_sequence]
    y_test=y_total[test_sequence]

    while begin < total_num:
        print begin
        part_sequence=random.sample(train_sequence,begin)
        part_x_train=x_total[part_sequence]
        part_y_train=y_total[part_sequence]
        svm_test_accuracy(part_x_train,part_y_train,x_test,y_test)
        begin += interval

    end_time=time.clock()
    print 'time consumed:%d'%(end_time-start_time)
