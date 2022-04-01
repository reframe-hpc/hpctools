#!/bin/bash

# smem will report mem usage: https://github.com/kwkroeger/smem.git
# smem reports physical memory usage, taking shared memory pages into account.
# Unshared memory is reported as the USS (Unique Set Size). Shared memory is
# divided evenly among the processes sharing that memory. The unshared  memory
# (USS) plus a process's proportion of shared memory is reported as the PSS
# (Proportional Set Size). The USS and PSS only include physical memory usage.
# They do not include memory that has been swapped out to disk.  
# 
# PID User     Command     Swap      USS      PSS      RSS
# ....

# Add in slurm jobscript:
# ~/smem.sh &
# srun ...
# smem_pid=`ps x |grep -m1 $HOME/smem.sh |awk '{print $1}'`
# kill -9 $smem_pid

# rm -f $SLURMD_NODENAME.rpt
out=$SLURMD_NODENAME.rpt
out=smem.rpt
ps x |awk '{print "# ",$0}' > $out
t0=`date +%s`
while [ true ] ;do
    t=`date +%s |awk -v tzero=$t0 '{print $0-tzero}'`
    ~/bin/smem/smem.git/smem -p --cmd-width=0 |& grep sedov/sedov |egrep -v "srun|grep" \
        |awk -v tt=$t '{print tt,$0}'  >> $out
    sleep 5
done
