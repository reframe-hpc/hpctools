import reframe as rfm
import reframe.utility.sanity as sn
import os
# import numpy as np


# {{{ gpu memory
@rfm.simple_test
class np_max_test(rfm.RunOnlyRegressionTest):
    omp_threads = parameter([12])
    # mpi_rks = parameter([1, 2])
    np_per_c = parameter([
        # 1.0e6, # 1.8e6,
        # 2.0e6, 2.2e6, 2.4e6, 2.6e6, 2.8e6,
        # 3.0e6, 3.2e6, 3.4e6, 3.6e6, 3.8e6,
        # 4.0e6, 4.2e6, 4.4e6, 4.6e6, 4.8e6,
        # 5.0e6, 5.2e6, 5.4e6, 5.6e6, 5.8e6,
        # 6.0e6, 6.2e6, 6.4e6, 6.6e6, 6.8e6 # oom: 6.8e6,
        # 7.0e6, 8.0e6, 9.0e6, 10.0e6, 11.0e6, 12.0e6
        12.0e6, 12.2e6, 12.4e6, 12.6e6, 12.8e6,
    ])
    mpi_rks = parameter([1])
    # np_per_c = parameter([1e6])
    steps = variable(str, value='0')
    exe_path = variable(str, value='/home/jgpiccinal/git/SPH-EXA_mini-app.git')
    rpt_file = variable(str, value='vm.rpt')

    valid_systems = ['*']
    valid_prog_environs = ['*']
    # modules = ['cdt-cuda/21.05', 'cudatoolkit/11.2.0_3.39-2.1__gf93aa1c']
    # sourcesdir = None
    prerun_cmds = [
        'mpirun --version',
        './smi.sh &',
    ]
    # prerun_cmds = ['module list']
    postrun_cmds = [
        r"sleep 1",  # give jobreport a chance
        r"pid=`ps x |grep smi.sh |grep -v grep |awk '{print $1}'`",
        r"for i in $pid ;do kill $i ;done",
    ]
    # Number of cores for each system
    cores = variable(dict, value={
        'daint:gpu': 12,
        'lumi:login': 12,  # 128
    })

    @run_before('run')
    def set_cubeside(self):
        phys_core_per_node = self.cores.get(self.current_partition.fullname, 1)
        # total_np = (phys_core_per_node * self.np_per_c)
        total_np = (phys_core_per_node * self.mpi_rks * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        self.executable = f'{self.exe_path}/sedov-cuda'
        self.executable_opts += [f"-n {self.cubeside}", f"-s {self.steps}"]

    @run_before('run')
    def set_num_threads(self):
        # num_threads = self.cores.get(self.current_partition.fullname, 1)
        # self.num_cpus_per_task = num_threads
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = self.omp_threads
        self.variables = {
            'LD_LIBRARY_PATH': f'{self.exe_path}:$LD_LIBRARY_PATH',
            'HIP_VISIBLE_DEVICES': '0',
            'ROCR_VISIBLE_DEVICES': '0',
            'OMP_NUM_THREADS': str(self.omp_threads),
            # 'OMP_PLACES': 'cores'
        }

    @sanity_function
    def check_execution(self):
        regex = r'Total execution time of \d+ iterations of \S+'
        return sn.assert_found(regex, self.stdout)

    # {{{ performance
    @performance_function('')
    def nsteps(self):
        regex = r'# Total execution time of (\d+) iterations of \S+:'
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function('')
    def n_cubeside(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        n_particles = sn.extractsingle(regex, self.stdout, 1, int)
        return int(pow(sn.evaluate(n_particles), 1/3))

    @performance_function('')
    def np_per_cnode(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        n_particles = sn.extractsingle(regex, self.stdout, 1, int)
        return int(sn.evaluate(n_particles) / self.mpi_rks)

    @performance_function('')
    def nparticles(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        return sn.extractsingle(regex, self.stdout, 1, int)
        # np = sn.evaluate(sn.extractsingle(regex, self.stdout, 1, int))
        # return f'{n_particles:.1E}'
        # the value extracted for performance variable 'daint:gpu:nparticles'
        # is not a number: 1.2E+07
        # return np.format_float_scientific(n_particles,
        #                                   precision=2, exp_digits=1)

    @performance_function('s')
    def elapsed(self):
        regex = r'# Total execution time of \d+ iterations of \S+: (\S+)s'
        return sn.extractsingle(regex, self.stdout, 1, float)

    @performance_function('B')
    def max_gpu_memory_b(self):
        # GPU[0] : VRAM Total Used Memory (B): 2228006912
        regex = r'VRAM Total Used Memory \(B\): (\d+)'
        rpt = os.path.join(self.stagedir, self.rpt_file)
        return sn.max(sn.extractall(regex, rpt, 1, int))

    @performance_function('GB')
    def max_gpu_memory_gb(self):
        # GPU[0] : VRAM Total Used Memory (B): 2228006912
        regex = r'VRAM Total Used Memory \(B\): (\d+)'
        rpt = os.path.join(self.stagedir, self.rpt_file)
        return sn.round(sn.max(sn.extractall(regex, rpt, 1, int)) / 1024**3, 1)
    # }}}
# }}}


# {{{ no tool
@rfm.simple_test
class np_max_test_notool(rfm.RunOnlyRegressionTest):
    # {{{
    """
# command/option: vertical selection
# commit 8065a203fa19ae3d4e1e7c31eb60ad4afe871140 (HEAD -> develop)
# Date:   Wed Mar 1 12:18:53 2023 +0100
#{{{ dom: np_per_c<=71e6 if > then cudaErrorMemoryAllocation: out of memory
#dom module load cdt/22.09
#dom module swap PrgEnv-cray PrgEnv-gnu
#dom module use /apps/daint/UES/eurohack/modules/all # CUDAcore/11.8.0
#dom module load CUDAcore/11.8.0
#dom module swap gcc gcc/11.2.0
#dom #mll cray-hdf5-parallel/1.12.0.4
#dom export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH

#dom -DGPU_DIRECT=OFF \

#dom cmake -S SPH-EXA.git -B build \
#dom -DBUILD_ANALYTICAL=OFF \
#dom -DBUILD_TESTING=OFF \
#dom -DSPH_EXA_WITH_FFTW=OFF \
#dom -DCMAKE_BUILD_TYPE=Release \
#dom -DCMAKE_CXX_COMPILER=CC \
#dom -DCMAKE_C_COMPILER=cc \
#dom -DCMAKE_CUDA_COMPILER=nvcc \
#dom -DCMAKE_CUDA_ARCHITECTURES=60

#dom cmake --build build -t sphexa-cuda -j
#dom OMP_NUM_THREADS=12 \
#dom srun -C'gpu&perf' -A`id -gn` -t10 -N2 -n2 \
#dom ./build/main/src/sphexa/sphexa-cuda --init sedov -s 1 -n 40

# --glass ./glass.h5 -s 1 -n 400
# nbody needs hdf5

#dom ~/R -c single_node_gpu_memory.py -n np_max_test_notool \
#dom --prgenv PrgEnv-gnu -r --system dom:gpu -S exe_path=$PWD/build/...

#p100 RFM_CONFIG=/users/piccinal/cscs-reframe-tests.git/config/systems/dom.py \
#p100 ~/R -c single_node_gpu_memory.py -n np_max_test_notool \
#p100 --prgenv PrgEnv-gnu --system dom:gpu -r \
#p100 -S exe_path=$PWD/build/main/src/sphexa/

#p100 [np_max_test_notool %np_per_c=71000000.0 %mpi_rks=1 /c873a7de dom:gpu:gnu
#p100   num_tasks: 1
#p100   num_tasks_per_node: 1
#p100   num_cpus_per_task: 12
#p100   performance:
#p100     - nsteps: 2  (r: 0  l: -inf% u: +inf%)
#p100     - n_cubeside: 413  (r: 0  l: -inf% u: +inf%)
#p100     - np_per_cnode: 70957944  (r: 0  l: -inf% u: +inf%)
#p100     - nparticles: 70957944  (r: 0  l: -inf% u: +inf%)
#p100     - elapsed: 35.6323 s (r: 0 s l: -inf% u: +inf%)

#daint: normal:MaxNodes=2400 large:MaxNodes=4400
#       -> 2400*70e6 = 168'000'e6 = 168 billions
#}}}
#{{{ A100/clariden: np_per_c<=e6 if > then cudaErrorMemoryAllocation: oom
# cd /scratch/f1000/piccinal/DEL/clariden/notool/
module load cray/22.12
module swap PrgEnv-cray PrgEnv-gnu
module use /apps/daint/UES/eurohack/modules/all # CUDAcore/11.8.0
module load CUDAcore/11.8.0
module swap gcc gcc/11.2.0
# hdf5
export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
# -DGPU_DIRECT=OFF \
cmake -S SPH-EXA.git -B build \
-DBUILD_ANALYTICAL=OFF \
-DBUILD_TESTING=OFF \
-DSPH_EXA_WITH_FFTW=OFF \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_CXX_COMPILER=CC \
-DCMAKE_C_COMPILER=cc \
-DCMAKE_CUDA_COMPILER=nvcc \
-DCMAKE_CUDA_ARCHITECTURES=80

cmake --build build -t sphexa-cuda -j

OMP_NUM_THREADS=64 \
srun -pnvgpu -A`id -gn` -t2 -N2 -n2 \
./build/main/src/sphexa/sphexa-cuda --init sedov -s 1 -n 100 --ascii

# --glass ./glass.h5 -s 1 -n 400
# nbody needs hdf5

vim ~/cscs-reframe-tests.git/config/systems/hohgant.py
# 'modules': ['cray', 'PrgEnv-gnu', 'gcc/11.2.0', 'CUDAcore/11.8.0']

RFM_CONFIG=~/cscs-reframe-tests.git/config/systems/hohgant.py \
~/R -c single_node_gpu_memory.py -n np_max_test_notool \
--prgenv PrgEnv-gnu \
--system hohgant:nvgpu -r -S exe_path=$PWD/build/main/src/sphexa \
--module-path=+/apps/daint/UES/eurohack/modules/all
#TODO: -m cray/22.12 --non-default-craype <- LD_LIB_PATH
#TODO: -m cdt/20.03 --non-default-craype

#a100 [       OK ] (11/20) np_max_test_notool %np_per_c=438900000.0 %mpi_rks=1
#a100 P: nsteps: 2  (r:0, l:None, u:None)
#a100 P: n_cubeside: 758  (r:0, l:None, u:None)
#a100 P: np_per_cnode: 437245479  (r:0, l:None, u:None)
#a100 P: nparticles: 437'245'479  (r:0, l:None, u:None) / -n758
#a100 P: elapsed: 93.939 s (r:0, l:None, u:None)

./single_node_gpu_memory.sh run-report-13.json |snk 1

#daint: normal:MaxNodes=2400 large:MaxNodes=4400 / P100=-n413
#       -> 2400*70e6 = 168'000'e6 = 168 billions
#       -> 2400*71e6 = 170'400'e6 = 170 billions
#  P100=71e6np/16GB ---6x---> A100=(16GB*6=96GB)=(71e6*6=426e6np) --> 438e6np !
#}}}
{{{ squashfs:
cd /scratch/e1000/piccinal/DEL/hohgant/notool/
# /store/csstaff/piccinal/cpe/base-cpe2208-gcc11-mpich8118-cuda118.squashfs
#                             base-cpe2212-gcc11-mpich8121-cuda118.squashfs
# squashfs-run base-cpe2208-gcc11-mpich8118-cuda118.squashfs bash
squashfs-run base-cpe2212-gcc11-mpich8121-cuda118.squashfs bash

module use /user-environment/modules
module load gcc/11.3.0 cray-mpich cuda/11.8.0
mpicxx --version # g++ (Spack GCC) 11.3.0
nvcc --version # Cuda compilation tools, release 11.8, V11.8.89

# cmake -S SPH-EXA.git -B build+sqfs2208 \
cmake -S SPH-EXA.git -B build+sqfs2212 \
-DBUILD_ANALYTICAL=OFF \
-DBUILD_TESTING=OFF \
-DSPH_EXA_WITH_FFTW=OFF \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_CXX_COMPILER=mpicxx \
-DCMAKE_C_COMPILER=mpicc \
-DCMAKE_CUDA_COMPILER=nvcc \
-DCMAKE_CUDA_ARCHITECTURES=80 \
-DCMAKE_CUDA_FLAGS="-arch=sm_80 -I$(dirname `which mpicc`)/../include"

# cmake --build build+sqfs2208 -t sphexa-cuda -j
cmake --build build+sqfs2212 -t sphexa-cuda -j

exit # /user-environment/ should be empty
OMP_NUM_THREADS=64 srun -pnvgpu -A`id -gn` -t1 -N1 -n1 \
--uenv-file=./base-cpe2208-gcc11-mpich8118-cuda118.squashfs \
./build+sqfs2208/main/src/sphexa/sphexa-cuda --init sedov -s 1 -n 100 --ascii

vim ~/cscs-reframe-tests.git/config/systems/hohgant.py
RFM_CONFIG=~/cscs-reframe-tests.git/config/systems/hohgant.py \
~/R -c single_node_gpu_memory.py -n np_max_test_notool \
--prgenv builtin \
--system hohgant:nvgpu -r -S exe_path=$PWD/build+sqfs2212/main/src/sphexa

# --system hohgant:nvgpu -r -S exe_path=$PWD/build+sqfs2208/main/src/sphexa
#no -S sqfs_path=$PWD
}}}
    """
    # omp_threads = parameter([12, 24])
    # omp_threads = parameter([1, 2, 3, 4, 6, 8, 10, 12, 16, 32, 64])
    # omp_threads = parameter([64, 80, 96, 112, 128])
    # omp_threads = parameter([1, 4, 8, 16, 32, 64, 96, 128])
    # omp_threads = parameter([1, 12, 16, 32, 48, 64, 80, 96, 112, 128])
    # omp_threads = parameter([12])
    # omp_threads = parameter([64])
    # mpi_rks = parameter([1, 2])
    np_per_c = parameter([
        64.0e6,  # = SebKeller
        # 1e6,
        # 70.0e6,
        # 71.0e6  # = max on 1 P100-16GB
        # 438.0e6  # = max on 1 A100-96GB (96GB/16GB=6x)
        # ko/2cn: 384.0e6  # = 6*64e6
        # ok: 340.0e6,
        # 385.0e6, 390.0e6
        # 438.0e6 + nn*1.0e5 for nn in range(0, 20, 1)

    ])
    # dom:
    # compute_nodes = parameter([1, 2, 4, 6, 8])
    # mpi_rks = parameter([1, 2, 4, 6, 8])  # 16
    # mpi_per_cn = parameter([1])
    # steps = variable(str, value='40')
    # hohgant:
    # compute_nodes = parameter([1, 2])
    # mpi_rks = parameter([1, 2, 4, 6, 8])  # 16
    # mpi_per_cn = parameter([1, 2, 3, 4])
    # steps = variable(str, value='40')
    #
    compute_nodes = parameter([1, 2, 3, 4])
    mpi_rks = parameter([1, 2, 3, 4, 6, 8, 9, 12, 16])
    mpi_per_cn = parameter([1, 2, 3, 4])
    steps = variable(str, value='40')  # 40
    #
    exe_path = variable(str, value='/home/jgpiccinal/git/SPH-EXA_mini-app.git')
    # sqfs_path = variable(str, value='/scratch/e1000/piccinal')

    # --bind-to socket
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcesdir = None
    # prerun_cmds = [
    # 'mpirun --version',
    # ]
    # Number of cores for each system
#     cores = variable(dict, value={
#         'daint:gpu': 12,
#         'dom:gpu': 12,
#         'hohgant:nvgpu': 64,
#         'clariden:nvgpu': 64,
#         'lumi:login': 12,  # 128
#     })
# }}}

    # {{{ set_skip
    @run_before('run')
    def skip_tests(self):
        run_tuples = {
            # (ntasks, cn, ntasks/cn):
            'dom:gpu': [(ii+1, ii+1, 1) for ii in range(self.compute_nodes)],
            'hohgant:nvgpu': [
                #     1cn,       2cn,        3cn,        4cn,
                (1, 1, 1), (2, 2, 1),  (3, 3, 1),  (4, 4, 1),
                (2, 1, 2), (4, 2, 2),  (6, 3, 2),  (8, 4, 2),
                (3, 1, 3), (6, 2, 3),  (9, 3, 3), (12, 4, 3),
                (4, 1, 4), (8, 2, 4), (12, 3, 4), (16, 4, 4),
            ],
        }
        current_tuple = (self.mpi_rks, self.compute_nodes, self.mpi_per_cn)
        cp = self.current_partition.fullname
        # print(cp, run_tuples[cp], self.compute_nodes)
        self.skip_if(current_tuple not in run_tuples[cp],
                     msg=f'will not run {current_tuple}/{cp}')
    # }}}

    # {{{ set_slurm_runtime
    @run_before('run')
    def set_slurm_runtime(self):
        self.num_tasks = self.mpi_rks
        self.num_tasks_per_node = self.mpi_per_cn
        # ~/jg_runonly.py # print(cpu.info['num_cpus_per_socket'])
        topo = {
                'dom:gpu': {'tasks-per-cn': 1, 'omp': 12, 'visi': ''},
                'daint:gpu': {'tasks-per-cn': 1, 'omp': 12, 'visi': ''},
                'hohgant:nvgpu': {
                    'tasks-per-cn':
                        self.num_tasks if self.num_tasks < 4 else 4,
                    'omp':
                        int(64/self.num_tasks) if self.num_tasks < 3 else 16,
                    'visi': '~/cuda_visible_devices.sh',
                },
                'hohgant:gpu-squashfs': {
                    'tasks-per-cn':
                        self.num_tasks if self.num_tasks < 4 else 4,
                    'omp':
                        int(64/self.num_tasks) if self.num_tasks < 3 else 16,
                    'visi': '~/cuda_visible_devices.sh',
                }
        }
        cp = self.current_partition.fullname
        # self.num_tasks_per_node = topo[cp]['tasks-per-cn']
        self.num_cpus_per_task = topo[cp]['omp']
        # core_per_node = self.cores.get(self.current_partition.fullname, 1)
        # visible = '~/cuda_visible_devices.sh' if core_per_node>12 else ''
        self.visible = topo[cp]['visi']
        self.env_vars = {
            # 'LD_LIBRARY_PATH': f'{self.exe_path}:$LD_LIBRARY_PATH',
            # 'HIP_VISIBLE_DEVICES': '0',
            # 'ROCR_VISIBLE_DEVICES': '0',
            # 'OMP_NUM_THREADS': str(self.omp_threads),
            'MPICH_VERSION_DISPLAY': '1',
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
            # 'OMP_PLACES': 'cores'
        }
        self.prerun_cmds += [
            'ulimit -c 0',
            # 'ulimit -a',
            # f'# {self.current_partition.fullname}',
            'echo "# _SLURM_MPI_TYPE=$SLURM_MPI_TYPE"',
            'echo "# _SLURM_JOB_PARTITION=$SLURM_JOB_PARTITION"',
            'echo "# _SLURM_JOBID=$SLURM_JOBID"',
            'echo "# _SLURM_JOB_NUM_NODES=$SLURM_JOB_NUM_NODES"',
            'echo "# _SLURM_NTASKS=$SLURM_NTASKS"',
            'echo "# _SLURM_TASKS_PER_NODE=$SLURM_TASKS_PER_NODE"',
            'echo "# _SLURM_JOB_CPUS_PER_NODE=$SLURM_JOB_CPUS_PER_NODE"',
            # _SLURM_TASKS_PER_NODE=1(x2)
            # _SLURM_JOB_CPUS_PER_NODE=24(x2)
            # echo "# SLURM_NTASKS = \$SLURM_NTASKS / -n --ntasks"
            # echo "# SLURM_NTASKS_PER_NODE = \$SLURM_NTASKS_PER_NODE / -N
            # echo "# SLURM_CPUS_PER_TASK = \$SLURM_CPUS_PER_TASK / -c
        ]
    # }}}

    # {{{ set_sph_runtime
    @run_before('run')
    def set_sph_runtime(self):
        total_np = (self.mpi_rks * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        self.executable = f' '
        # self.job.launcher.options = []
        self.executable_opts += [
            '--cpu-bind=verbose,none',
            # --report-bindings
            # '--bind-to', 'none',
            # 'numactl', '--interleave=all',
            # better to edit config file -> #SBATCH
            # no: f'--uenv-file={self.sqfs_path}/0.sqfs,
            self.visible,
            # '--bind-to socket',
            f'{self.exe_path}/sphexa-cuda', '--init', 'sedov',
            f"-n {self.cubeside}", f"-s {self.steps}", '--ascii'
        ]
    # }}}

    # {{{ extract_linked_version
    @run_before('run')
    def extract_linked_version(self):
        cmd1 = f'ldd {self.exe_path}/sphexa-cuda | grep libcudart '
        cmd2 = "awk '{print \"ls -l \",$3}'"
        cmd3 = 'sh'
        cmd4 = "awk '{print $11}'"
        self.rpt = os.path.join(self.stagedir, 'rpt')
        cmd = f'{cmd1} | {cmd2} | {cmd3} | {cmd4} > {self.rpt}'
        self.prerun_cmds += [
            cmd,
            # if MPICH_VERSION_DISPLAY is unavailable:
            # f'ldd {self.exe_path}/sphexa-cuda | grep mpich >> rpt',
        ]
    # }}}

    # {{{ sanity
    @sanity_function
    def check_execution(self):
        regex = r'# Total execution time of \d+ iterations of \S+'
        return sn.assert_found(regex, self.stdout)
    # }}}

    # {{{ performance
    # {{{  # you cannot mix 'perf_patterns' and 'perf_variables' syntax
#     @performance_function('')
#     def np_per_cnode(self):
#         regex = r'Data generated for (\d+) global particles'
#         n_particles = sn.extractsingle(regex, self.stdout, 1, int)
#         return int(sn.evaluate(n_particles) / self.mpi_rks)
#
    # }}}
    @run_before('performance')
    def report_job(self):
        regex_mpich = r'MPI VERSION\s+: CRAY MPICH version (\S+) '
        regex_cudart = r'libcudart.so.(\S+)$'
        regex_nsteps = r'# Total execution time of (\d+) iterations of \S+'
        regex_global_np = r'Data generated for (\d+) global particles'
        regex_elapsed = (
            r'# Total execution time of \d+ iterations of \S+ up to t ='
            r' \S+: (\S+)s'
        )
        regex_s = {
            'mpi': r'_SLURM_MPI_TYPE=(\S+)',
            'part': r'_SLURM_JOB_PARTITION=(\S+)',
            'jid': r'_SLURM_JOBID=(\d+)',
            'cn': r'_SLURM_JOB_NUM_NODES=(\d+)',
            'nt': r'_SLURM_NTASKS=(\d+)',
            'nt-cn': r'_SLURM_TASKS_PER_NODE=(\d+)',
            'c-cn': r'_SLURM_JOB_CPUS_PER_NODE=(\d+)',
        }
        self.perf_patterns = {
            's_jobid': sn.extractsingle(regex_s['jid'], self.stdout, 1, int),
            's_cn': sn.extractsingle(regex_s['cn'], self.stdout, 1, int),
            's_ntasks': sn.extractsingle(regex_s['nt'], self.stdout, 1, int),
            # 's_nt-cn': sn.extractsingle(regex_s['nt-'], self.stdout, 1, int),
            # 's_cpu-cn': sn.extractsingle(regex_s['c-'], self.stdout, 1, int),
            #
            'nsteps': sn.extractsingle(regex_nsteps, self.stdout, 1, int),
            'ncubeside': sn.extractsingle(
                regex_global_np, self.stdout, 1,
                conv=lambda x: int(pow(int(x), 1/3))),
            'np': sn.extractsingle(regex_global_np, self.stdout, 1, int),
            'np_per_mpi': sn.extractsingle(
                regex_global_np, self.stdout, 1,
                conv=lambda x: int(int(x) / self.mpi_rks)),
            'elapsed': sn.extractsingle(regex_elapsed, self.stdout, 1, float),
            #
            'mpich': sn.extractsingle(regex_mpich, self.stderr, 1,
                                      conv=lambda x: int(x.replace('.', ''))),
            'cudart': sn.extractsingle(regex_cudart, self.rpt, 1,
                                       conv=lambda x: int(x.replace('.', ''))),
        }
    # }}}
# }}}
