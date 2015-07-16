import os
import sys
import string
import time

def conv_pattern(vector,conv_kernel):
    pattern=[]
    for i in range(len(conv_kernel)):
        if conv_kernel[i] == 1:
            pattern.append(vector[i])
    pattern_key=pattern[0]
    for i in range(1,len(pattern)):
        pattern_key='%s_%s'%(pattern_key,pattern[i])
    return pattern_key 

def pattern_get(pattern_file):
    g_pattern={}
    file_handle=open(pattern_file,'r')
    for i in range(10000):
        line=file_handle.readline()
        [pattern,contribution]=line.split(':')
        g_pattern[pattern]=i+1
    file_handle.close()
    return g_pattern

def filter_vector(vector):
    single_vector=[]
    num=0
    vector_length=len(vector)
    while num<vector_length:
        if num+4<=vector_length:
            if vector[num] != vector[num+2] or vector[num+1] != vector[num+3]:
                single_vector.append(vector[num])
                num +=1
            else:
                num += 2
        else:
            for i in range(num,vector_length):
                single_vector.append(vector[i])
            break         
    return single_vector

def filter_vector_file(vector_file):
    print 'begin filtering vector'
    vector_list=[]
    white_vector_list=[]
    black_vector_list=[]
    vector_handle=open(vector_file,'r')
    for vector in vector_handle:
        vector_item=vector.strip('\n').strip(' ').split(' ')
        vector_item=filter_vector(vector_item)
        label=vector_item[0]
        del vector_item[0]
        if label == '-1':
            black_vector_list.append(vector_item)
        else:
            white_vector_list.append(vector_item)
    vector_handle.close()
    vector_list.append(white_vector_list)
    vector_list.append(black_vector_list)
    print 'vector fiter over'
    return vector_list      
        
def get_vector_dict(vector,conv_kernel,g_pattern):
    local_pattern={}
    kernel_length=len(conv_kernel)
    vector_length=len(vector)
    for i in range(vector_length-kernel_length+1):
        vector_part=vector[i:i+kernel_length]
        pattern_key=conv_pattern(vector_part,conv_kernel)
        if pattern_key in g_pattern:
            if g_pattern[pattern_key] in local_pattern:
                local_pattern[g_pattern[pattern_key]] += 1
            else:
                local_pattern[g_pattern[pattern_key]] = 1
    return local_pattern

def generate_vector(vector_list,g_pattern,conv_kernel,pattern_vector_file):
    file_handle=open(pattern_vector_file,'w')
    for vector in vector_list[0]:
        vector_dict=get_vector_dict(vector,conv_kernel,g_pattern)  
        file_handle.write('+1')
        white_vector= sorted(vector_dict.iteritems(), key=lambda d:d[0], reverse = False)
        for vector_item in white_vector:
            file_handle.write(' %d:%d'%(vector_item[0],vector_item[1]))
        file_handle.write('\n')

    for vector in vector_list[1]:
        vector_dict=get_vector_dict(vector,conv_kernel,g_pattern)  
        file_handle.write('-1')
        black_vector= sorted(vector_dict.iteritems(), key=lambda d:d[0], reverse = False)
        for vector_item in black_vector:
            file_handle.write(' %d:%d'%(vector_item[0],vector_item[1]))
        file_handle.write('\n')
    file_handle.close()

def get_conv_kernel(pattern_file):
    conv_kernel=[]
    for char in pattern_file:
        if char == '0':
            conv_kernel.append(0)
        if char == '1':
            conv_kernel.append(1)
    return conv_kernel

def process_vector(vector_list,pattern_selection_dir,pattern_vector_dir):
    pattern_file_list=os.listdir(pattern_selection_dir)
    for pattern_file in pattern_file_list:
        vector_file=pattern_file.replace('pattern','vector')
        print 'generating %s'%vector_file
        g_pattern=pattern_get(os.path.join(pattern_selection_dir,pattern_file))
        vector_file=os.path.join(pattern_vector_dir,vector_file) 
        conv_kernel=get_conv_kernel(pattern_file)
        generate_vector(vector_list,g_pattern,conv_kernel,vector_file)
        

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'Usage:'
        print sys.argv[0] , ' pattern_selection_dir patterv_vector_dir vector_file'
        sys.exit()
    pattern_selection_dir=sys.argv[1]
    pattern_vector_dir=sys.argv[2]
    vector_file=sys.argv[3]
    if not os.path.exists(pattern_vector_dir):
        os.mkdir(pattern_vector_dir)
    vector_list=filter_vector_file(vector_file)
    process_vector(vector_list,pattern_selection_dir,pattern_vector_dir)
