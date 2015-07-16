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
    return vector_file

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0],'train_vec_file test_vec_file new_test_vector'
        print 'train_vec_file does NOT contain md5!'
        print 'test_vec_file does contain md5!'
        exit(-1)

    test_vec_file_without_md5 = split_md5_vector(sys.argv[2])
    
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
    THRESHOLD = (num_neighbors-1)*0.1
    print 'num_neighbors=',num_neighbors
    print 'THRESHOLD=',THRESHOLD
    flann = FLANN()
    indices,dists = flann.nn(X_train_svd,X_test_svd,num_neighbors,algorithm="kmeans",
branching=32, iterations=7, checks=16);
    print indices
    print 'indices shape=',indices.shape
    #print dists
    #print 'dists shape=',dists.shape
     
    file_handle=open('all_dists_%s'%sys.argv[2],'w')
    np.savetxt(file_handle, dists)
    file_handle.close()    
    file_handle=open('all_indices_%s'%sys.argv[2],'w')
    np.savetxt(file_handle, indices)
    file_handle.close()    

    error_list=[]   
    for vec in xrange(X_test_svd.shape[0]):
            num_posi = 0
            num_nega = 0
            if vec%5000 == 0:
                print 'prcess %d vec'%vec
            for x in xrange(1,num_neighbors):
                if y_train[indices[vec][x]]==1:
                    num_posi+=1
                elif y_train[indices[vec][x]]==-1:
                    num_nega+=1
            target_label = y_test[vec]
            if target_label== -1 and num_nega <= THRESHOLD:
                #print 'self label=%d'%target_label
                #print 'self index=%d'%(vec)
                error_list.append(vec)
                #for x in xrange(1,num_neighbors):
                #    print '%d,%d'%(y_train[indices[vec][x]],indices[vec][x])
            
            if target_label== 1 and num_posi <= THRESHOLD:
                #print 'self label=%d'%target_label
                #print 'self index=%d'%(vec)
                error_list.append(vec)
                #for x in xrange(1,num_neighbors):
                #    print '%d,%d'%(y_train[indices[vec][x]],indices[vec][x])
    print error_list
    print 'len of error_list=',len(error_list)
    if len(error_list)==0:
        end_time = time.time()
        print 'do nothing,pyflann end,time=%fs'%(end_time-preprocess_time)
    output_vec_name = '%s.n%d_t%d'%(sys.argv[2],num_neighbors,int(THRESHOLD))    
    full_list=range(X_test.shape[0])
    reserve_list=list(set(full_list)-set(error_list))
    X_test_new = X_test[reserve_list]
    y_test_new = np.delete(y_test,error_list)
    dump_svmlight_file(X_test_new,y_test_new,output_vec_name,zero_based=False)

    X_test_error = X_test[error_list]
    y_test_error = np.delete(y_test,reserve_list)
    dump_svmlight_file(X_test_error,y_test_error,'%s.err'%output_vec_name,zero_based=False)

    end_time = time.time()
    print 'pyflann end,time=%fs'%(end_time-preprocess_time)
