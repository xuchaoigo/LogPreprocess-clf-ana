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
from sklearn.random_projection import sparse_random_matrix
import random
import time

def svm_test(train_data,test_data):
    x_train,y_train=train_data
    x_test,y_test=test_data
    clf = svm.LinearSVC()
    clf.fit(x_train, y_train)
    y_predict =clf.predict(x_test)
    print 'test accuracy:%f'%(np.mean(y_predict==y_test))

def svm_val(train_data,val_data):
    x_train,y_train=train_data
    x_val,y_val=val_data

    clf = svm.LinearSVC()
    clf.fit(x_train, y_train)
    y_predict =clf.predict(x_val)
    distance=clf.decision_function(x_val)
    print 'val accuracy:%f'%(np.mean(y_predict==y_val))
    
    full_list=range(x_val.shape[0]) 
    error_list=[]
    for i in range(x_val.shape[0]):
        if y_val[i] != y_predict[i]:
            error_list.append(i) 
    if len(error_list) !=0:
        error_x=x_val[error_list]
        error_y=y_val[error_list]
        y_train=np.append(y_train,error_y)
        x_train=sp.sparse.vstack((x_train,error_x),format='csr')
        start_time=time.clock()
        reserve_list=list(set(full_list)-set(error_list))
        x_val=x_val[reserve_list]
        end_time=time.clock()
        y_val=np.delete(y_val,error_list)

    return [(x_train,y_train),(x_val,y_val)]
    
   
def split_data(vector_file):
    print 'loading data'
    x_total, y_total = load_svmlight_file(vector_file)
    [row,col]=x_total.shape

    total_num=row
    print 'total num:%d'%total_num
    train_num=9000
    val_num=500
    test_num=total_num-train_num-val_num

    total_sequence=range(total_num)
    train_sequence=random.sample(total_sequence,train_num)
    left_sequence=list( set(total_sequence)-set(train_sequence) )
    val_sequence=random.sample(left_sequence,val_num)
    test_sequence=list( set(left_sequence)-set(val_sequence))

    x_train=x_total[train_sequence]
    y_train=y_total[train_sequence]
    x_val = x_total[val_sequence]
    y_val = y_total[val_sequence]
    x_test = x_total[test_sequence]
    y_test = y_total[test_sequence]

    return [(x_train,y_train),(x_val,y_val),(x_test,y_test)]

def update_model(train_set,val_set,test_set):
    svm_test(train_set,test_set)
    return svm_val(train_set,val_set)

def process(vector_file):
    train_set,val_set,test_set=split_data(vector_file)
    for i in range(5):
        print 'iteration:',i
        train_set,val_set=update_model(train_set,val_set,test_set)
    svm_test(train_set,test_set) 

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print sys.argv[0], ' vector_file'
        sys.exit()
    vector_file=sys.argv[1]
    process(vector_file)
