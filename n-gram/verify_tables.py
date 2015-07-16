import os
import sys
import time

def find_pos_of_nth_str(source_str,target_str,n):
    if source_str=='' or target_str=='' or n<=0:
        return 142857
    pos = -1
    while n!=0:
        pos = source_str.find(target_str,pos+1)
        if pos==-1:
            return 142857
        n-=1
    return pos


def get_table(top_src_dir):
        file_list=[]
        for root,dirs,files in os.walk(top_src_dir):
            for name in files:
                file_list.append(name)

        split_set = set()
        tab_out_set= set()
        for mixed_file in file_list:
            if 'split' in mixed_file:
                pos = mixed_file.rfind('.')
                if pos!=-1:
                    table_name = mixed_file[pos+1:]
                split_set.add(table_name)
            if '.tbl' in mixed_file:
                divide_tabname  = find_pos_of_nth_str(mixed_file,'_',5)
                tabname = mixed_file[3:divide_tabname]
                tab_out_set.add(tabname)

        print '%d tables in spilt files.'%len(split_set)
        print '%d tables in tab files.'%len(tab_out_set)
        cnt_all =0
        cnt_miss =0

        NGRAM = 2
        tab_in_set= set()
        for tab in split_set:
            if '_' in tab:
                cnt_all+=1
                found = 0
                
                if NGRAM ==2:
                    divide_pos = find_pos_of_nth_str(tab,'_',3)
                    if divide_pos==142857:
                        continue
                    subtable1 = tab[:divide_pos]
                    subtable2 = tab[divide_pos+1:]
                    real_tab_in = '%s$%s'%(subtable1,subtable2)
                    #ingore strange tables.
                    if real_tab_in.count('_')!=4:
                        continue
                elif NGRAM ==1:
                    real_tab_in = tab
                else:
                    exit(1)

                tab_in_set.add(real_tab_in)
        
        print 'miss set = '
        miss_set = tab_in_set.difference(tab_out_set)
        print miss_set
        cnt_miss = len(miss_set)
        
        #for miss_file in miss_set:
            #os.system('cp %s/*.%s ./leave_outs'%(top_src_dir,miss_file.replace('$','_')))
                   
        print 'cnt all=',cnt_all
        print 'cnt miss=',cnt_miss
            
        #print 'strange set = '
        #print tab_out_set.difference(tab_in_set)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage:'
        print sys.argv[0], 'top_src_dir '
        sys.exit()
  
    tabdir = sys.argv[1]
    get_table(tabdir)


