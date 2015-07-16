import os
import time
import sys

def conv_pattern(vector, conv_kernel):
    pattern = []
    for i in range(len(conv_kernel)):
        if conv_kernel[i] == 1:
            pattern.append(vector[i])

    pattern_key = pattern[0]
    for i in range(1, len(pattern)):
        pattern_key = '%s_%s' % (pattern_key, pattern[i])

    return pattern_key


def get_pattern(vector, conv_kernel, g_pattern):
    local_pattern={}
    kernel_length = len(conv_kernel)
    vector_length = len(vector)
    for i in range(vector_length - kernel_length + 1):
        vector_part = vector[i:i + kernel_length]
        pattern_key = conv_pattern(vector_part, conv_kernel)
        local_pattern[pattern_key]=1
    for pattern_key in local_pattern:
        if pattern_key in g_pattern:
            g_pattern[pattern_key] += 1
        else:
            g_pattern[pattern_key] = 1


def filter_vector(vector):
    single_vector = []
    num = 0
    vector_length = len(vector)
    while num < vector_length:
        if num + 4 <= vector_length:
            if vector[num] != vector[num + 2] or vector[num + 1] != vector[num + 3]:
                single_vector.append(vector[num])
                num += 1
            else:
                num += 2
        else:
            for i in range(num, vector_length):
                single_vector.append(vector[i])
            break
    return single_vector


def filter_vector_file(vector_file):
    vector_list = []
    white_vector_list = []
    black_vector_list = []
    vector_handle = open(vector_file, 'r')
    for vector in vector_handle:
        vector_item = vector.strip('\n').strip(' ').split(' ')
        vector_item = filter_vector(vector_item)
        label = vector_item[0]
        del vector_item[0]
        if label == '-1':
            black_vector_list.append(vector_item)
        else:
            white_vector_list.append(vector_item)

    vector_handle.close()
    vector_list.append(white_vector_list)
    vector_list.append(black_vector_list)
    return vector_list


def pattern_single(conv_kernel, vector_list, pattern_dir):
    white_pattern = {}
    black_pattern = {}
    pattern_file = '%d' % conv_kernel[0]
    for i in range(1, len(conv_kernel)):
        pattern_file = '%s_%d' % (pattern_file, conv_kernel[i])

    # white vector collection
    for vector in vector_list[0]:
        get_pattern(vector, conv_kernel, white_pattern)
    white_list = sorted(white_pattern.iteritems(), key=lambda d: d[1], reverse=True)
    white_pattern_file = '%s_%s' % ('white', pattern_file)
    white_pattern_full_file = os.path.join(pattern_dir, white_pattern_file)
    pattern_handle = open(white_pattern_full_file, 'w')
    for pattern in white_list:
        pattern_handle.write('%s:%d\n' % (pattern[0], pattern[1]))

    # black vector collection
    pattern_handle.close()
    for vector in vector_list[1]:
        get_pattern(vector, conv_kernel, black_pattern)

    black_list = sorted(black_pattern.iteritems(), key=lambda d: d[1], reverse=True)
    black_pattern_file = '%s_%s' % ('black', pattern_file)
    black_pattern_full_file = os.path.join(pattern_dir, black_pattern_file)
    pattern_handle = open(black_pattern_full_file, 'w')
    for pattern in black_list:
        pattern_handle.write('%s:%d\n' % (pattern[0], pattern[1]))

    pattern_handle.close()


def check_kernel(kernel_list, number,kernel_size):
    kernel = [0 for i in range(kernel_size)]
    number_bin = bin(number)
    count_1 = 0
    number_bin_length = len(number_bin)
    if len(number_bin) > 2:
        for i in range(2, number_bin_length):
            count_1 += int(number_bin[i])

        if count_1 >= 3:
            k = kernel_size
            for j in range(number_bin_length - 1, 1, -1):
                kernel[k - 1] = int(number_bin[j])
                k -= 1

            for j in range(k):
                kernel[j] = 0

            kernel_list.append(kernel)


def generate_conv_kernel(kernel_size):
    kernel_list = []
    max_kernel_length = 2 ** kernel_size
    for number in range(1, max_kernel_length):
        check_kernel(kernel_list, number,kernel_size)

    return kernel_list


def pattern_collection(vector_list, pattern_dir, kernel_size):
    conv_kernel_list = generate_conv_kernel(kernel_size)
    for conv_kernel in conv_kernel_list:
        pattern_single(conv_kernel, vector_list, pattern_dir)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage:'
        print sys.argv[0], ' vector_file_name save_pattern_dir conv_kernel_size'
        sys.exit()
    start_time = time.time()
    vector_file = sys.argv[1]
    pattern_dir = sys.argv[2]
    kernel_size = int(sys.argv[3])
    if not os.path.exists(pattern_dir):
        os.mkdir(pattern_dir)
    vector_list = filter_vector_file(vector_file)
    pattern_collection(vector_list, pattern_dir, kernel_size)
    end_time = time.time()
    print 'pattern extraction over,time consumed:%d' % (end_time - start_time)
