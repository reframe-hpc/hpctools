#!/bin/bash

./smi.sh &

HIP_VISIBLE_DEVICES=0 \
mpirun -np 1 ./sedov-cuda -s 1 -n 300
sleep 1
echo done

ps x |grep "smi.sh |grep -v grep"
pid=`ps x |grep "smi.sh" |grep -v grep |awk '{print $1}'`
for i in $pid ;do
    echo pid=$pid
    kill $i
    # kill $pid
done
