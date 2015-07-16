# -*- coding: cp936 -*-
import os
import sys
import string
from sklearn import svm
from sklearn.datasets import load_svmlight_file

def check_sparse_vector(svm_dir):
    file_list = []
    for root,dirs,files in os.walk(svm_dir):
        for name in files:
            svm_file = os.path.join(root,name)
            try:
                print 'checking file:',svm_file
                X_train, y_train = load_svmlight_file(svm_file)
                print 'file checked'
            except Exception,e:
                print e
                print traceback.format_exc()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' sparse_data_dir'
        print 'Used to check format of individual vec files uploaded by cluster clients.'
        sys.exit()
    
    print 'Main process start.'
    sparse_dir = sys.argv[1]
    check_sparse_vector(sparse_dir);     
    print 'Main process exit.'
