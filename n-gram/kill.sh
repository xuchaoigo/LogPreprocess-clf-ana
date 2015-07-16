#!/bin/sh
keys=`(ps -ef |grep $1 |grep -v "grep") | awk '{print $2}'`
for key in ${keys[*]}
do
       kill -9 $key
done
