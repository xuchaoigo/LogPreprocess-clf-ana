import time
from pyflann import *
from numpy import *
from numpy.random import *
import numpy as np
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file
from sklearn.decomposition import TruncatedSVD

def split_md5_vector(md5_vector_file):
    suffix=md5_vector_file#[0:md5_vector_file.find('md5')-1]
    md5_file='%s.md5'%suffix
    print md5_file
    vector_file='%s.vector'%suffix
    print vector_file
    md5_vector_handle=open(md5_vector_file,'r')
    md5_handle=open(md5_file,'w')
    vector_handle=open(vector_file,'w')
    cnt = 0
    for line in md5_vector_handle:
        cnt +=1
        line=line.strip('\n')
        medium=line.find(' ')
        md5=line[0:medium]
        vector=line[medium+1:]
        md5_handle.write('%s\n'%md5)
        vector_handle.write('%s\n'%vector)
    print 'process %d vecs'%cnt
    return vector_file,md5_file

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],'train_vec_file test_vec_file new_test_vector'
        print 'train_vec_file does NOT contain md5!'
        print 'test_vec_file does contain md5!'
        exit(-1)

    test_vec_file_without_md5,md5_file = split_md5_vector(sys.argv[2])
    
    train_vector = sys.argv[1]
    start_time = time.time()
    print 'loading train data...'
    X_train, y_train = load_svmlight_file(train_vector)
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'
    X_test, y_test = load_svmlight_file(test_vec_file_without_md5,n_features=X_train.shape[1])
    print 'X_test.shape=',X_test.shape
    print 'Y_test.shape=',y_test.shape
    print 'test data loaded.'

    load_time = time.time()
    print 'load_time=%fs'%(load_time-start_time)

    print 'SVD input train_set shape:',X_train.shape
    print 'SVD input test_set shape:',X_test.shape
    svd = TruncatedSVD(n_components=500, random_state=42)
    svd.fit(X_train) 
    TruncatedSVD(algorithm='randomized', n_components=500, n_iter=5,
            random_state=42, tol=0.0)
    print 'SVD var percent=',(svd.explained_variance_ratio_.sum())
    X_train_svd = svd.transform(X_train)
    X_test_svd = svd.transform(X_test)
    print 'SVD output train shape:',X_train_svd.shape
    print 'SVD output test shape:',X_test_svd.shape
    preprocess_time = time.time()
    print 'preprocess_time=%fs'%(preprocess_time-load_time)
    
    num_neighbors = 11
    print 'num_neighbors=',num_neighbors
    flann = FLANN()
    indices,dists = flann.nn(X_train_svd,X_test_svd,num_neighbors,algorithm="kmeans",
branching=32, iterations=7, checks=16);
    print indices
    print 'indices shape=',indices.shape
    print dists
    print 'dists shape=',dists.shape

    md5_read_handle=open(md5_file,'r')
    md5_write_handle=open('%s.output_nn'md5_file,'w')
    md5_lines = md5_handle.readlines()
    for vec in xrange(X_test_svd.shape[0]):
            num_posi = 0
            num_nega = 0
            num_strange_neighbor = 0
            if vec%5000 == 0:
                print 'prcess %d vec'%vec
            for x in xrange(1,num_neighbors):
                if y_train[indices[vec][x]]==1:
                    num_posi+=1
                elif y_train[indices[vec][x]]==-1:
                    num_nega+=1
            target_label = y_test[vec]
            if target_label== -1:
                num_strange_neighbor = num_posi
            elif target_label== 1:
                num_strange_neighbor = num_nega
            else:
                print 'wtf'
            md5_write_handle.write('%s, %d'%(md5_lines[vec].strip(),num_strange_neighbor))

    end_time = time.time()
    print 'pyflann end,time=%fs'%(end_time-preprocess_time)
