import sys


#0eddc80c2992bc286dabc63f58a7b398 8/10 -1 73:1 187:1 211:1 305:1 407:1 513:1 972:1 1341:1
def get_md5_list_from_file(vec_file):
    ret_list=[]
    handle = open(vec_file,'r')
    for line in handle:
        line = line.strip()
        arg_list = line.split(' ')
        ret_list.append(arg_list[1])
    return ret_list

def process(vec_file):
    fet_ratio_list = get_md5_list_from_file(vec_file)
    print 'read %d md5.'%len(fet_ratio_list)
    match_num = 0
    all_num = 0
    for ratio in fet_ratio_list:
        num_list = ratio.split('/')
        match_num += int(num_list[0])
        all_num += int(num_list[1])
    print 'match_num=',match_num
    print 'all_num=',all_num
    print 'match ratio=',match_num/float(all_num)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],' vector_file(with md5 and fet_quality)'
        sys.exit()
    process(sys.argv[1])
