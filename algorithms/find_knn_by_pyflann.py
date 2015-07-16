import time
from pyflann import *
from numpy import *
from numpy.random import *
import numpy as np
from sklearn.datasets import load_svmlight_file
from sklearn.datasets import dump_svmlight_file
from sklearn.decomposition import TruncatedSVD

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:'
        print sys.argv[0],'train_vector_file new_train_vector'
        exit(-1)
 
    start_time = time.time()
    print 'loading train data...'
    train_vector = sys.argv[1]
    X_train, y_train = load_svmlight_file(train_vector)
    print 'X_train.shape=',X_train.shape
    print 'Y_train.shape=',y_train.shape
    print 'train data loaded.'

    load_time = time.time()
    print 'load_time=%fs'%(load_time-start_time)

    print 'SVD input shape:',X_train.shape
    svd = TruncatedSVD(n_components=500, random_state=42)
    svd.fit(X_train) 
    TruncatedSVD(algorithm='randomized', n_components=500, n_iter=5,
            random_state=42, tol=0.0)
    print 'SVD var percent=',(svd.explained_variance_ratio_.sum())
    X_train_svd = svd.transform(X_train)
    print 'SVD output shape:',X_train_svd.shape
    preprocess_time = time.time()
    print 'preprocess_time=%fs'%(preprocess_time-load_time)
    
    num_neighbors = 11
    THRESHOLD = (num_neighbors-1)*0.1
    print 'num_neighbors=',num_neighbors
    print 'THRESHOLD=',THRESHOLD
    flann = FLANN()
    indices,dists = flann.nn(X_train_svd,X_train_svd,num_neighbors,algorithm="kmeans",
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
    for vec in xrange(X_train_svd.shape[0]):
            num_posi = 0
            num_nega = 0
            if vec%10000 == 0:
                print 'prcess %d vec'%vec
            for x in xrange(1,num_neighbors):
                if y_train[indices[vec][x]]==1:
                    num_posi+=1
                elif y_train[indices[vec][x]]==-1:
                    num_nega+=1
            target_label = y_train[vec]
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
    output_vec_name = '%s.n%d_t%d'%(sys.argv[2],num_neighbors,int(THRESHOLD))    
    full_list=range(X_train.shape[0])
    reserve_list=list(set(full_list)-set(error_list))
    X_train_new = X_train[reserve_list]
    y_train_new = np.delete(y_train,error_list)
    dump_svmlight_file(X_train_new,y_train_new,output_vec_name,zero_based=False)

    X_train_error = X_train[error_list]
    y_train_error = np.delete(y_train,reserve_list)
    dump_svmlight_file(X_train_error,y_train_error,'%s.err'%output_vec_name,zero_based=False)

    end_time = time.time()
    print 'pyflann end,time=%fs'%(end_time-preprocess_time)
