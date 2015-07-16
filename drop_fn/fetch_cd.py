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
from sklearn.datasets import dump_svmlight_file
from sklearn.random_projection import sparse_random_matrix
import random
import time
from sklearn.externals import joblib

def train_model(train_file):
    x_train,y_train=load_svmlight_file(train_file)
    clf=svm.LinearSVC()
    clf.fit(x_train,y_train)
    joblib.dump(clf, './model/svm_model')
    print 'model train over'

def result_output(y_oral,y_predict):
    if len(y_oral) != len(y_predict):
        print 'data preparation fp!'
        return
    data_len = len(y_oral)
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for i in range(data_len):
        if y_oral[i] == 1 and y_predict[i] == 1:
            tp += 1
        elif y_oral[i] == 1 and y_predict[i] == -1:
            fn += 1
        elif y_oral[i] == -1 and y_predict[i] == -1:
            tn += 1 
        else:
            fp += 1
    print 'fn:%d'%fn
    print 'tp:%d'%tp
    if fn+tp != 0:
        print 'false negative:%f'%(fn/(fn+tp))
    if fp+tn != 0:
        print 'false positive:%f'%(fp/(fp+tn))    
    if fn+tp != 0:
        return fn/(fn+tp)

def save_md5_file(source_md5_file,dest_md5_file,digit_list):
    read_handle=open(source_md5_file,'r')
    lines=read_handle.readlines()
    read_handle.close()
    part_lines=[]
    for number in digit_list:
       part_lines.append(lines[number]) 
    write_handle=open(dest_md5_file,'w')
    write_handle.writelines(part_lines)
    write_handle.close()
    
def test_model(test_file,md5_file):
    clf=joblib.load('./model/svm_model')
    x_test,y_test=load_svmlight_file(test_file,n_features=clf.coef_.shape[1])
    y_predict=clf.predict(x_test)
    result_output(y_test,y_predict)
    ''' 
    error_list=[]
    for i in range(x_test.shape[0]):
        if y_test[i] != y_predict[i] and y_test[i] == 1:
            error_list.append(i)
    error_x=x_test[error_list]
    error_y=y_test[error_list]
    dump_svmlight_file(error_x,error_y,'fn_set_vector',zero_based=False)
    
    error_md5_file='fn_set_md5'
    save_md5_file(md5_file,error_md5_file,error_list)
    '''
    '''
    right_list=[]
    for i in range(x_test.shape[0]):
        if y_test[i] == y_predict[i]:
            right_list.append(i)
    right_x=x_test[right_list]
    right_y=y_test[right_list]
    dump_svmlight_file(right_x,right_y,'right_set_vector',zero_based=False)

    right_md5_file='right_set_md5'
    save_md5_file(md5_file,right_md5_file,right_list)
    '''


def update_model(train_set,fn_set):
    x_train,y_train=train_set
    x_fn,y_fn=fn_set
    print 'train size:%d  fn size:%d'%(x_train.shape[0],x_fn.shape[0])

    x_new_train=sp.sparse.vstack((x_train,x_fn),format='csr')
    y_new_train=np.append(y_train,y_fn)
    
    clf=svm.LinearSVC()
    clf.fit(x_new_train,y_new_train)
    y_fn_predict=clf.predict(x_fn)
    fn_rate=result_output(y_fn,y_fn_predict)
    if fn_rate<0.2:
        print 'the false negative rate is below 0.1,stop updates,save model and exit'
        joblib.dump(clf, './model/svm_model')
        sys.exit()
    else:
        error_list=[]
        for i in range(len(y_fn)):
            if y_fn[i] != y_fn_predict[i]:
                error_list.append(i)
        fn_x=x_fn[error_list]
        fn_y=y_fn[error_list]
        return [(x_new_train,y_new_train),(fn_x,fn_y)]
        '''
        Here can add some iteration methods, for example: add right and add full sets, which depends on the real datasets'
        '''
        
   
def drop_fn(train_file,drop_file):
    x_train,y_train=load_svmlight_file(train_file)
    x_fn,y_fn=load_svmlight_file(drop_file,n_features=x_train.shape[1])
    train_set=(x_train,y_train)
    fn_set=(x_fn,y_fn)
    iterations = 0
    while 1:
        print 'iteration:%d'%iterations
        iterations += 1
        train_set,fn_set=update_model(train_set,fn_set)
    
if __name__=='__main__':
    if len(sys.argv) == 1:
        print 'Usage:'
        print '     print selections:'
        print '         train:train model'
        print '         test:test data'
        print '         drop:drop false negative'
        sys.exit()
    if sys.argv[1] == 'train':
       if len(sys.argv) != 3:
            print sys.argv[0],' train train_file' 
            sys.exit()
       train_model(sys.argv[2])
       sys.exit()
    if sys.argv[1] == 'test':
        if len(sys.argv) != 4:
            print sys.argv[0],' test test_file md5_file'
            sys.exit()
        test_model(sys.argv[2],sys.argv[3])
        sys.exit()
    if sys.argv[1] == 'drop':
        if len(sys.argv) != 4:
            print sys.argv[0],' drop train_file drop_file'
            sys.exit()
        drop_fn(sys.argv[2],sys.argv[3])
        sys.exit()
