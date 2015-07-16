import os
import sys
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0],'distance_file'
        exit(-1)
    
    distance_range = xrange(1,16)
    cmd="grep '\+00' %s|wc -l"%(sys.argv[1])
    print cmd
    os.system(cmd)
    for num in distance_range:
        cmd="grep '\+%02d' %s|wc -l"%(num,sys.argv[1])
        print cmd
        os.system(cmd)
    
    for num in distance_range:
        cmd="grep '\-%02d' %s|wc -l"%(num,sys.argv[1])
        print cmd
        os.system(cmd)
