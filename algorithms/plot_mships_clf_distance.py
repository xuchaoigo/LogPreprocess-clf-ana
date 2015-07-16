# -*- coding: cp936 -*-
import os
import sys
import string
import time
import MySQLdb
import matplotlib
import matplotlib.pyplot as plt 
from pylab import *
import matplotlib.pyplot as plt


def get_distance(category):
    MySqlCon=MySQLdb.connect(host='127.0.0.1',user='root',passwd='123456',port=3306)  
    MySqlCur=MySqlCon.cursor()
    MySqlCon.select_db('mships_classifier_report')

    fetchcmd="select * from report where result='%s'"%category
    count=MySqlCur.execute(fetchcmd)
    result_list=MySqlCur.fetchmany(count)
    dst=[]
    for i in result_list:
        dst.append(i[2])
    x=arange(0,count,1)
    plot(x,dst,linewidth=1.0)
    xlabel("sample")
    ylabel("%s distance"%category)
    grid(True)
    show()
    savefig('distance_%s_%s.png'%(category,count))
    print 'save figure to ./distance_%s.png'%category
    print 'count of %s = %d'%(category,count)

    MySqlCur.close()
    MySqlCon.commit()
    MySqlCon.close()

if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage:%s tp/fp/tn/fp'%sys.argv[0]
        sys.exit()

    category=sys.argv[1]
    get_distance(category)     
    print 'Main process exit.'
