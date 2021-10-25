#!/usr/bin/env python3
# https://github.com/mkaz/termgraph 

# TODO: print commit + title: elapsed time in seconds/weak scaling on Pilatus (cpu: AMD EPYC 7742 64-Core craype-x86-rome = znver2)
import json

infile = 'latest.json' ;f = open(infile) ;d = json.load(f) ;f.close()

# print('@ native,singularity')
# see my modified ./termgraph.py
titles = [
    '#A: cpe141.sif cpeCray cce/11.0.2 cray-mpich/8.1.6.53 container',
    '#B: cpe141.sif cpeCray cce/12.0.2 cray-mpich/8.1.8    native',
    '#C: debian11.sif clang/13.0.0 mpich/3.4.1 container',
    '#D: null',
    #
    '#E: cpe141.sif cpeGNU gcc/10.2.0 cray-mpich/8.1.6.53 container',
    '#F: cpe141.sif cpeGNU gcc/10.3.0 cray-mpich/8.1.8    native',
    '#G: debian11.sif g++/10.2.1 mpich/3.4.1',
    '#H: null',
    '# with: singularity/3.5.3-1, Pilatus/weak scaling/sedov test case: 64omp/node, 1mpi/node, 64*1e5np/node, 4steps',
    # '# hpe_cpe_1.4.1.sif / debian11_clang13_mpich341.def.sif'
]
for i in titles: print(i)
print('@ A,B,C,D,E,F,G,H')
for n_cn in [1, 2, 4, 8, 16, 32]:
    first_column = True
    for i in d['runs'][0]['testcases']:
        if i['result'] == 'success' and \
           i['name'].startswith('RunContainer') and \
           len(i['nodelist']) == n_cn:
            if first_column:
                row = f"{len(i['nodelist'])}cn,{i['perfvars'][1]['value']},{i['perfvars'][2]['value']}"
                first_column = False
            else:
                row = row + f",{i['perfvars'][1]['value']},{i['perfvars'][2]['value']}"
            print(row)

        # row1 = f"{len(i['nodelist'])}cn,{i['perfvars'][1]['value']},{i['perfvars'][2]['value']}"
        # row2 = f"#  {i['name']}"
        # print(f'{row1}\n{row2}')

# print('@ native,singularity')
# # for i in d['runs'][0]['testcases'][2::2]:
# # 2,4,6,8,10,12,14,16: np_per_c=6e4
# # 3,5,7,9,11,13,15,17: np_per_c=8e4
# for i in d['runs'][0]['testcases'][2:]:
#     # 'RunContainer_znver2_Singularity_hpe_cpe_1_4_1_sif_sedov_1_64_80000_0'
#     # >>> '_80000_' in d['runs'][0]['testcases'][3]['name']
#     # if '_80000_' in i['name']:
#     if '_100000_' in i['name']:
#         row1 = f"{len(i['nodelist'])}cn,{i['perfvars'][1]['value']},{i['perfvars'][2]['value']}"
#         row2 = f"# {i['stagedir']}"
#         print(f'{row1}\n{row2}')
#         # i['perfvars'][0] = cubeside
#         # i['perfvars'][1] = elapsed_time_container
#         # i['perfvars'][2] = elapsed_time_native
#         # i['perfvars'][3] = elapsed_steps

# source ~/myvenv_pilatus/bin/activate
# termgraph ./in --color {blue,red}
# termgraph ./eff.colors --color {red,blue,green,magenta,yellow,black} --space-between --suffix ' sec'
# cat ./in
