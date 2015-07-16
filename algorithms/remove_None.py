import sys
if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'Usage:'
        print '%s input_file output_file'%sys.argv[0]
        exit(-1)

    input_handle = open(sys.argv[1],'r')
    output_handle = open(sys.argv[2],'w')
    count = 0
    for line in input_handle:
        count += 1
        if count%10000 == 0:
            print 'processing count: %d'%count
        new_line = ''
        str_list = line.split()
        for str in str_list:
            if str[:4] != 'None':
                new_line += '%s '%str
        if len(new_line)>3:
            output_handle.write('%s\n'%new_line)

    input_handle.close()
    output_handle.close()
