import sys

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:'
        print '%s model_file'%sys.argv[0]
        exit(-1)
        
    index = -1
    index_list=[]
    model = open(sys.argv[1],'r')
    for line in model:
        if line.strip()=='w':
            index = 0
            continue
        if index >=0:
            abs_of_w = abs(float(line.strip()))
            index_list.append((index,abs_of_w))
            index+=1
	
    print 'len of w = ',len(index_list)	
    for i in range(20):
        print '%d,%s'%(index_list[i][0],index_list[i][1])
    print '-------------------------------------------------'
    index_list.sort(key=lambda x:x[1],reverse=True)    
    for i in range(20):
        print '%d,%s'%(index_list[i][0],index_list[i][1])
    
    topk = 50000
    index_file = open('%s.top%d.index'%(sys.argv[1],topk),'w')
    for i in range(topk):
        index_file.write('%d\n'%index_list[i][0])
