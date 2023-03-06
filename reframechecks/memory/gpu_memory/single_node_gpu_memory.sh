#!/bin/bash
in=$1


echo -n "num_tasks num_tasks_per_node num_cpus_per_task system pe "
echo -n "jid cn ntasks nsteps ncubeside np np_per_mpi elapsed mpich cudart "
echo    "it_throughput_per_min"

nres=`grep perfvars $in |wc -l`
for ii in `seq 0 $((nres-1))` ;do
    if [ `jq -r .runs[].testcases[$ii].result $in` == "success" ] ;then
        num_tasks=`jq .runs[].testcases[$ii].check_vars.num_tasks $in`
        num_tasks_per_node=`jq .runs[].testcases[$ii].check_vars.num_tasks_per_node $in`
        num_cpus_per_task=`jq .runs[].testcases[$ii].check_vars.num_cpus_per_task $in`
        system=`jq .runs[].testcases[$ii].system $in`
        pe=`jq .runs[].testcases[$ii].environment $in`
        echo "$num_tasks $num_tasks_per_node $num_cpus_per_task $system $pe" \
            |awk '{printf "%4d %4d %d %s %s ",$1,$2,$3,$4,$5}'
        
        #1 s_jobid
        #2 s_cn
        #3 s_ntasks
        #4 nsteps        # "name": "nsteps",
        #5 ncubeside     # "name": "ncubeside",
        #6 np            # "name": "np",
        #7 np_per_mpi    # "name": "np_per_mpi",
        #8 elapsed       # "name": "elapsed",
        #9 mpich         # "name": "mpich",
        #0 cudart        # "name": "cudart",   
        # 42176-   2-   8-  40-       798- 510082399-63760299.000000-121-812111$
        #jq .runs[].testcases[$ii].perfvars[].value $in
        jq .runs[].testcases[$ii].perfvars[].value $in \
            |awk '{printf "%s ",$0}' |awk '{print $0}' \
            |awk '{printf "%7d %4d %4d %4d %6d %10d %10d %10.2f %s %s %6.1f\n", $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$4*60/$8}'
            # |awk '{printf "### %7d-%4d-%4d-%4d-%6d-%10d-%10d-%10.2f-%s-%s$\n", $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11}'
    fi
done

#{{{ A100: .  ./single_node_gpu_memory.sh run-report-A100.json |snk 1 # > run-report-A100_64M.tbl
# num_tasks num_tasks_per_node num_cpus_per_task system pe jid cn ntasks nsteps ncubeside np np_per_mpi elapsed mpich cudartit_throughput_per_min
#    1    1 64 "hohgant:nvgpu" "PrgEnv-gnu"   42183    1    1   40    398   63521199   63521199      97.57 812111 11889   24.6
#    2    1 32 "hohgant:nvgpu" "PrgEnv-gnu"   42179    2    2   40    502  127263527   63631763     124.25 812111 11889   19.3
#    2    2 32 "hohgant:nvgpu" "PrgEnv-gnu"   42181    1    2   40    502  127263527   63631763     129.08 812111 11889   18.6
#    4    2 16 "hohgant:nvgpu" "PrgEnv-gnu"   42178    2    4   40    633  254840104   63710026     134.29 812111 11889   17.9
#    4    4 16 "hohgant:nvgpu" "PrgEnv-gnu"   42180    1    4   40    633  254840104   63710026     143.84 812111 11889   16.7
#    6    3 16 "hohgant:nvgpu" "PrgEnv-gnu"   42177    2    6   40    725  382657176   63776196     137.30 812111 11889   17.5
#    8    4 16 "hohgant:nvgpu" "PrgEnv-gnu"   42176    2    8   40    798  510082399   63760299     121.24 812111 11889   19.8
#}}}

# num_tasks num_tasks_per_node num_cpus_per_task nsteps ncubeside np np_per_mpi elapsed mpich cudart
#   16    1 12 "dom:gpu" "PrgEnv-gnu"  40 1006 1021147343   63821708     440.37 7718 110194
#    8    1 12 "dom:gpu" "PrgEnv-gnu"  40  798  510082399   63760299     384.87 7718 110194
#    4    1 12 "dom:gpu" "PrgEnv-gnu"  40  633  254840104   63710026     421.92 7718 110194
#    2    1 12 "dom:gpu" "PrgEnv-gnu"  40  502  127263527   63631763     394.95 7718 110194
#    1    1 12 "dom:gpu" "PrgEnv-gnu"  40  398   63521199   63521199     335.76 7718 110194
