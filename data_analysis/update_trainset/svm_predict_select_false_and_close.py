# -*- coding: cp936 -*-
import os
import sys
import time
import numpy as np
from sklearn import svm
from sklearn.svm import LinearSVC
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file

def split_md5_vector(md5_vector_file):
    suffix=md5_vector_file#[0:md5_vector_file.find('md5')-1]
    vector_file='%s.vector'%suffix
    print vector_file
    md5_list=[]
    quality_list=[]
    md5_vector_handle=open(md5_vector_file,'r')
    vector_handle=open(vector_file,'w')
    cnt = 0
    for line in md5_vector_handle:
        cnt +=1
        line=line.strip('\n')
        medium=line.find(' ')
        medium2=line.find(' ',medium+1)
        md5=line[0:medium]
        quality=line[medium+1:medium2]
        vector=line[medium2+1:]
        vector_handle.write('%s\n'%vector)
        md5_list.append(md5)
        quality_list.append(quality)
    print 'process %d vecs'%cnt
    return vector_file,md5_list,quality_list      

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'train_vector_file test_vector_file'
        print 'train_vec_file does NOT contain md5!'
        print 'test_vec_file does contain md5!'
        exit(-1)
    [test_vec_file_without_md5,md5_list,fet_quality] = split_md5_vector(sys.argv[2])

    start_time = time.time()
    print 'loading train data...'
    X_train, y_train = load_svmlight_file(sys.argv[1] )
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    print 'loading test data...'
    X_test, y_test = load_svmlight_file(test_vec_file_without_md5,n_features=X_train.shape[1])
    print 'X_test.shape=',X_test.shape
    print 'y_test.shape=',y_test.shape
    print 'test data loaded.'
    
    clf = svm.LinearSVC()
    y_pred = clf.fit(X_train, y_train).predict(X_test)
    print 'y_pred.shape=',y_pred.shape   
    print y_pred
    distance = clf.decision_function(X_test)
    print 'distance.shape=',distance.shape   
    
    result_file_handle=open('%s.result'%sys.argv[2],'w')
    #output md5 and it's level
    for i in xrange(y_test.shape[0]):    
        if int(y_pred[i])==1:
            result_file_handle.write('%s,%d,%f\n'%(md5_list[i],100,float(distance[i])))        
        elif int(y_pred[i])==-1:        
            result_file_handle.write('%s,%d,%f\n'%(md5_list[i],200,float(distance[i])))
    
    num_tp=0.0
    num_tn=0.0
    num_fp=0.0
    num_fn=0.0
    cnt = 0
    THRESHOLD =1
    error_list=[]    
    vec_size = y_pred.size    
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
            if abs(distance[i]) < THRESHOLD:
                error_list.append(i)

    print 'len of error_list=',len(error_list)
    full_list=range(X_train.shape[0])
    reserve_list=list(set(full_list)-set(error_list))
    X_train_new = X_train[error_list]
    y_train_new = np.delete(y_train,reserve_list)

    print 'X_train_new.shape=',X_train_new.shape
    print 'len of error_list=',len(error_list)
    dump_svmlight_file(X_train_new,y_train_new, '%s.false_close'%sys.argv[2],zero_based=False)
    print '----> vector predict end!'
    print 'tn=',num_tn
    print 'fp=',num_fp
    print 'tp=',num_tp
    print 'fn=',num_fn
    print 'fp per=%f'%(num_fp/(num_fp+num_tn))
    print 'fn per=%f'%(num_fn/(num_fn+num_tp))

    pred_time = time.time()
    print 'predict end,time=%fs'%(pred_time-start_time)
