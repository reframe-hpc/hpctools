# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

# import contextlib
import reframe as rfm
import reframe.utility.sanity as sn
# from reframe.core.launchers import LauncherWrapper


hdf5_mod = {
    'A64FX': {
        'PrgEnv-arm-A64FX': 'hdf5/1.13.0-A64FX+ARM',
        'PrgEnv-gnu-A64FX': 'hdf5/1.13.0-A64FX+GNU',
        'PrgEnv-nvidia-A64FX': 'hdf5/1.13.0-A64FX+NVHPC',
    },
    'neoverse-n1': {
        'PrgEnv-arm-N1': 'hdf5/1.13.0-N1+ARM',
        'PrgEnv-gnu': 'hdf5/1.13.0-N1+GNU',
        'PrgEnv-nvidia': 'hdf5/1.13.0-N1+NVHPC',
    },
    'TX2': {
        'PrgEnv-arm-TX2': 'hdf5/1.13.0-TX2+ARM',
        'PrgEnv-gnu': 'hdf5/1.13.0-TX2+GNU',
        'PrgEnv-nvidia': 'hdf5/1.13.0-TX2+NVHPC',
    },
    'gpu': {
        'PrgEnv-gnu': '' # 'hdf5/1.13.0',
    },
    'mc': {
        'PrgEnv-gnu': '' # 'hdf5/1.13.0',
    },
    'a100': {
        'PrgEnv-gnu': '' # 'hdf5/1.13.0',
    },
}
max_mpixomp = {
    'dom': {'gpu': 12, 'mc': 36},
    'daint': {'gpu': 12, 'mc': 36},
    'wombat': {'neoverse-n1': 40, 'TX2': 64, 'A64FX': 48},
    'lumi': {'gpu': 64},
    'dmi': {'a100': 112},
}
topology_mpixomp = {
    'dom': {'gpu': {'cps': 12, 's': 1}, 'mc': {'cps': 18, 's': 2}},
    'lumi': {'gpu': {'cps': 64, 's': 1}},
    'wombat': {
        'neoverse-n1': {'cps': 40, 's': 1},
        'TX2': {'cps': 32, 's': 2},
        'A64FX': {'cps': 12, 's': 4},
        },
    'dmi': {'a100': {'cps': 28, 's': 2}},
    }
# cmake -S SPH-EXA.git -B build -DBUILD_TESTING=OFF -DBUILD_ANALYTICAL=OFF \
# -DSPH_EXA_WITH_HIP=OFF -DBUILD_RYOANJI=OFF -DCMAKE_BUILD_TYPE=Release \
# -DCMAKE_CXX_COMPILER=mpicxx -DCMAKE_CUDA_COMPILER=nvcc

# x=~/DEL/reframe/stage/wombat/gpu/PrgEnv-arm/build_sedov_notool/build/src/sedov
# ~/Ampere -c sedov_cuda.py -p PrgEnv-arm$ -n run_sedov_cuda -S mypath=$x -r
# x=
# ~/TX2 -c sedov_cuda.py -p PrgEnv-arm -n run_sedov_cuda -S mypath=$x -r
# x=~/DEL/reframe/stage/wombat/A64FX/PrgEnv-arm-A64FX/build_sedov_notool/build/src/sedov
# ~/A64FX -c sedov_cuda.py -p PrgEnv-arm-A64FX -n run_sedov -S mypath=$x -r
# x=/scratch/snx3000tds/piccinal/reframe/stage/dom/gpu/PrgEnv-gnu/build_sedov_notool/build/src/sedov
# ~/R -c sedov_cuda.py -n run -S mypath=$x -p PrgEnv-gnu -r -m cudatoolkit/21.5_11.3 -m gcc/9.3.0
#
# egrep "highmem_rss|num_tasks|cubeside" reframe.out |tr -d "\n" |sed -e "s@* num_tasks@\nnum_tasks@g" |awk '{print $2","$5","$9}'
#{{{ run sedov
@rfm.simple_test
class run_sedov_cuda(rfm.RunOnlyRegressionTest):
    # use_tool = variable(bool, value=False)
    # use_tool = parameter([False, True])
    # use_tool = parameter(['Score-P/7.1-CrayNvidia-21.09'])
    # use_tool = parameter(['Score-P'])
    sourcesdir = None
    use_tool = parameter(['notool'])
    mypath = variable(str, value='.')
    # compute_nodes = parameter([1, 2, 4, 6, 8, 12, 16, 24, 48])
    compute_nodes = parameter([1, 2, 4, 6, 8, 12, 16, 24, 48])
    steps = parameter([0]) # 10
    cube = parameter([100]) # variable(int, value=100)
    valid_systems = ['wombat:gpu', 'dom:gpu', 'dom:mc']
    valid_prog_environs = ['builtin', 'PrgEnv-gnu', 'PrgEnv-arm-N1', 'PrgEnv-arm-TX2', 'PrgEnv-gnu-A64FX', 'PrgEnv-arm-A64FX', 'PrgEnv-nvidia']
    #{{{ compute_nodes = parameter([0, 1, 2, 4])
    # steps = parameter([13]) # 10
    # compute_nodes = parameter([1, 2, 4, 8, 16])
    # np_per_c = parameter([5.34e6]) #ko 6.4e6
    # sk wants 5.34e6 ok 6.0e6, 6.2e6 does not scale
    # ---- wombat
    # compute_nodes = parameter([1, 2, 4])
    # np_per_c = parameter([45e5]) # OK <------------- -n572 = 187'149'248/2gpu
    #donotscale np_per_c = parameter([47e5]) # OK <------------- -n572 = 187'149'248/2gpu
    # 47e5 ok  / 48e5 ko
    # ----
    # np_per_c = variable(int)
    # compute_nodes = parameter([1, 2, 4, 8])
    # np_per_c = parameter([4.0e6, 6.0e6])
    # juwels: ok: 16e6 191'102'976 -n576 / Approx: 50.4512GB / each gpu with 40GB
    # juwels: ko: 18e6
    # dom:
    # catalyst ok: 5.2e6 = -n396 = 62'099'136/cn
    # catalyst oom: 5.4e6
    # noinsitu ok: 6.2e6 = 74'088'000 /1cn = -n420 64GB/cpu + 16GB/P100
    # noinsitu oom: 6.4e6    
    # 2 24-core AMD EPYC Rome 7402 CPUs (each with 512GB DDR memory) and
    # 4 NVIDIA Ampere A100 GPUs (each with 40GB HBM2e), with
    # insitu = parameter(['none', 'Catalyst'])
    # modules = ['gcc/10.3.0', 'Score-P/7.1-CrayNvidia-21.09'] # , 'gcc/9.3.0']
    # modules = ['Nsight-Systems/2022.1.1', 'Nsight-Compute/2022.1.0']
    # sedov-cuda': corrupted double-linked list: 0x000000000084f570 ***
    # --> load PrgEnv-cray + gcc
    # valid_prog_environs = ['PrgEnv-gnu']
    # modules = ['daint-gpu', 'ParaView']
    # modules = ['CMake',] # 'PrgEnv-cray', 'gcc/9.3.0']
    #}}}
    time_limit = '30m'
    use_multithreading = False
    strict_check = False
    # executable = variable(str, value='$HOME/sedov-cuda')

    #{{{ run
    @run_before('run')
    def set_run(self):
        # self.executable = '$HOME/sedov-cuda'
        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            self.executable = f'{self.mypath}/sedov'
        else:
            self.executable = f'{self.mypath}/sedov-cuda'

        # self.num_tasks = 9
        # self.job.launcher =
        # LauncherWrapper(self.job.launcher, 'time', ['-p'])
        # @run_before('performance')
        self.skip_if_no_procinfo()
        procinfo = self.current_partition.processor.info
        if self.current_system.name in ['dom']:
            self.num_tasks_per_node = 1
            self.num_tasks = self.compute_nodes * self.num_tasks_per_node
            self.num_cpus_per_task = 12
            self.np_per_c = 5.34e6 # 64e6 per cn
        elif self.current_system.name in ['wombat']:
            if self.compute_nodes > 0:
                self.num_tasks_per_node = 2
                self.num_tasks = self.compute_nodes * self.num_tasks_per_node
                self.num_cpus_per_task = 20
                self.np_per_c = 32.1e5 # 64e6 per gpu
            else:
                self.num_tasks_per_node = 1
                self.num_tasks = 1
                self.num_cpus_per_task = 20
                self.np_per_c = 32.1e5 # 64e6 per gpu
                # could use VISIBLE_CUDA_DEVICES

        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            self.num_tasks = self.compute_nodes
            self.num_tasks_per_node = self.num_tasks
            # self.num_tasks = self.compute_nodes * self.num_tasks_per_node
            self.num_cpus_per_task = int(48 / self.num_tasks_per_node)
            self.np_per_c = int(64e6 / self.num_tasks)
            # self.np_per_c = 10e6
        # self.num_tasks = self.compute_nodes * self.num_tasks_per_node
        #no! self.num_tasks_per_core = 1
        # --cpus-per-task=<ncpus> = -c = openmp threads
        # self.num_cpus_per_task = \
        #     int(procinfo['num_cpus'] / procinfo['num_cpus_per_core'])
        # total_np = (self.compute_nodes * self.num_tasks_per_node *
        #             self.num_cpus_per_task * self.np_per_c)
        # self.cubeside = int(pow(total_np, 1 / 3))
        if self.compute_nodes > 0:
            total_np = (self.compute_nodes * self.num_tasks_per_node *
                        self.num_cpus_per_task * self.np_per_c)
        else:
            total_np = (self.num_tasks * self.num_tasks_per_node *
                        self.num_cpus_per_task * self.np_per_c)

        self.cubeside = int(pow(total_np, 1 / 3))
        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            self.cubeside = self.cube #  400  # 64e6 per node

        if self.steps == 200:
            self.cubeside = 50

        self.executable_opts = [
            '-n', str(self.cubeside),
            '-s', str(self.steps),
            # '-w', '-1',
        ]
        self.variables = {
            # 'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
            'OMP_PLACES': 'sockets',
            'OMP_PROC_BIND': 'close',
            # numactl --interleave=all
            # 'LD_LIBRARY_PATH': '$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH',
            # 'SCOREP_FILTERING_FILE': 'sedov.filt',
            # 'SCOREP_CUDA_ENABLE': 'default',
            # 'SCOREP_CUDA_BUFFER': '50M',
            # 'SCOREP_PROFILING_ENABLE_CORE_FILES': '1',
            # export LD_LIBRARY_PATH=/users/piccinal/easybuild/dom/haswell/software/CubeW/4.6-CrayNvidia-21.09/lib64:$LD_LIBRARY_PATH
        }
        self.job.launcher.options = ['--mpi=pmix', 'numactl', '--interleave=all']
        if self.current_system.name in {'daint', 'dom'}:
            self.job.launcher.options = ['numactl', '--interleave=all']

#{{{
        # if self.use_tool = 'Score-P':

#         profiler = 'nsys'
#         self.rpt = 'rk0.rpt'
#         # NOTE: Warning: LBR backtrace method is not supported on this platform. DWARF backtrace method will be used.
#         if self.use_tool:
#             self.job.launcher.options = [
#                 profiler, 'profile', '--force-overwrite=true',
#                 '-o', '%h.%q{SLURM_NODEID}.%q{SLURM_PROCID}',
#                 '--trace=cuda,mpi,nvtx', '--mpi-impl=mpich',
#                 '--stats=true',
#                 '--cuda-memory-usage=true',
#                 '--backtrace=dwarf',
#                 '--gpu-metrics-set=ga100',
#                 '--gpu-metrics-device=all',
#                 # '--gpu-metrics-device=0,1',
#                 '--gpu-metrics-frequency=15000',
#                 #--sampling-period=3000000 
#                 # '--nic-metrics=true'
#             ]
# #             self.postrun_cmds += [
# #                 f'{profiler} stats *.0.nsys-rep &> {self.rpt}',
# #                 # f'{profiler} stats *$SLURMD_NODENAME.*.qdrep &> {self.rpt}',
# #             ]
#}}}
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += [
            'echo stoptime=`date +%s`',
            'echo "job done"',
            'rm -f core*',
            'echo "SLURMD_NODENAME=$SLURMD_NODENAME"',
            'echo "SLURM_JOBID=$SLURM_JOBID"',
        ]
        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            self.prerun_cmds += ['$HOME/smem.sh &']
            self.postrun_cmds += [
                "smem_pid=`ps x |grep -m1 $HOME/smem.sh |awk '{print $1}'`",
                "kill -9 $smem_pid"
            ]
    #}}}

    @sanity_function
    def assert_sanity(self):
        #steps = self.exec_opts[self.suite][self.size]['s']
        regex1 = r'Total execution time of \d+ iterations of \S+: \S+s$'
        #regex3 = f'^stoptime{self.repeat}='
        return sn.all([
            sn.assert_found(regex1, self.stdout),
        ])

    #{{{ analytical
    @run_before('run')
    def set_compare(self):
        # print(self.steps, type(self.steps))
        if self.steps == 200:
            self.executable_opts += ['-w', str(self.steps)]
            self.postrun_cmds += [
                '# analytical_solution:',
                'source ~/myvenv_matplotlib/bin/activate',
                f'ln -s {self.mypath}/../analytical_solutions/sedov_solution/sedov_solution',
                f'ln -s {self.mypath}/../../../src/analytical_solutions/compare_solutions.py',
                'python3 ./compare_solutions.py sedov -bf ./sedov_solution '
                '-n 125000 -sf ./dump_sedov200.txt -cf ./constants.txt -i 200 -np '
                '--error_rho --error_p --error_vel '
                # FIXME: add after we move to glass initial model
                # '--error_u --error_cs '
            ]
        else:
            self.executable_opts += ['-w', '-1']

    # Checking Errors L1 ...
    # Error L1_rho = 0.15792224703716007
    # Error L1_u   = 2687361599999999.5
    # Error L1_p   = 0.19511670163905478
    # Error L1_vel = 0.12847877073319336
    # Error L1_cs  = 154556.49990558348
    # Checked Error L1_rho successfully: 0.15792224703716007 <= 1.0
    # Checked Error L1_u         failed: 2687361599999999.5 > 1.0
    # Checked Error L1_p   successfully: 0.19511670163905478 <= 1.0
    # Checked Error L1_vel successfully: 0.12847877073319336 <= 1.0
    # Checked Error L1_cs        failed: 154556.49990558348 > 1.0
    # Writing Errors L1    file [./sedov_errors_L1_0.0673556.dat ]
    @performance_function('le1', perf_key='L1_rho')
    def report_rho(self):
        regex = r'Checked Error L1_rho\s+\S+:\s+(?P<err>\S+)\s+'
        if self.steps == 200:
            return sn.round(sn.extractsingle(regex, self.stdout, 'err', float), 6)
        else:
            return 0

    @performance_function('le1', perf_key='L1_p')
    def report_p(self):
        regex = r'Checked Error L1_p\s+\S+:\s+(?P<err>\S+)\s+'
        if self.steps == 200:
            return sn.round(sn.extractsingle(regex, self.stdout, 'err', float), 6)
        else:
            return 0

    @performance_function('le1', perf_key='L1_vel')
    def report_vel(self):
        regex = r'Checked Error L1_vel\s+\S+:\s+(?P<err>\S+)\s+'
        if self.steps == 200:
            return sn.round(sn.extractsingle(regex, self.stdout, 'err', float), 6)
        else:
            return 0
    #}}}

    #{{{ memory
    @performance_function('%', perf_key='highmem_rss')
    def report_highmem_rss(self):
        #regex = r'^.*%\s+(?P<pct>\S+)%\s+\S+%\s+$'
        regex = r'^.*\s+(?P<pct>\S+)% $'
        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            return sn.max(sn.extractall(regex, 'smem.rpt', 'pct', float))
        else:
            return 0
    #}}}

    #{{{ timers
    @performance_function('s', perf_key='elapsed_date')
    def report_elapsed_date(self):
        regex_start_sec = r'^starttime=(?P<sec>\d+.\d+)'
        regex_stop_sec = r'^stoptime=(?P<sec>\d+.\d+)'
        start_sec = sn.extractall(regex_start_sec, self.stdout, 'sec', int)
        stop_sec = sn.extractall(regex_stop_sec, self.stdout, 'sec', int)
        return sn.round((stop_sec[0] - start_sec[0]), 1)

    @performance_function('s', perf_key='elapsed_internal')
    def report_elapsed_internal(self):
        # Total execution time of 0 iterations of Sedov: 0.373891s
        regex = r'Total execution time of \d+ iterations of \S+: (?P<s>\S+)s$'
        sec = sn.extractsingle(regex, self.stdout, 's', float)
        return sn.round(sec, 1)

    @performance_function('cn', perf_key='compute_nodes')
    def report_cn(self):
        return self.compute_nodes

    @performance_function('-n', perf_key='cubeside')
    def report_cubeside(self):
        return self.cubeside

    @performance_function('np', perf_key='np_per_c')
    def report_np_per_c(self):
        return self.np_per_c

    @performance_function('-s', perf_key='steps')
    def report_steps(self):
        return self.steps

    #}}}

# 00_init
# 00_box
# -g runs ok
# cube_stat
# cube_calltree -m time -i  profile.cubex -a -c / ok on juwels
#}}}


# x='--module-path +/sw/wombat/ARM_Compiler/21.1/modulefiles --module-path +$HOME/modulefiles'
# ./R -c sedov_cuda.py -n run_tests -r -S repeat=3 $x -S mypath='../build_with_armpl_notool/build/JG/sbin/performance'
# dom:
# ~/R -c sedov_cuda.py -n run_tests -r -m nvhpc-nompi/21.9 -m gcc/9.3.0 -S repeat=1 -S mypath='../build_without_armpl_notool/build/JG/sbin/performance' -p PrgEnv-gnu
# dmi: salloc -pgpu -t 6:0:0 ; ssh cl-node027
#{{{ run_tests
@rfm.simple_test
class run_tests(rfm.RunOnlyRegressionTest):
    sourcesdir = None
    # use_tool = parameter(['notool'])
    analytical = parameter(['analytical'])
    cubeside = parameter([200]) # 200
    steps = parameter([800]) # 800
    #mypath = variable(str, value='../build_notool/build/JG/sbin/performance')
    mypath = variable(str, value='../build_analytical_False_without_armpl_notool/build/JG/bin')
    repeat = variable(int, value=1)
    compute_nodes = parameter([0])
    # compute_nodes = parameter([1])
    mpi_ranks = parameter([1])
    openmp_threads = parameter([56])
#    mpi_ranks = parameter([1, 2, 4, 7, 8, 14, 28, 56])
#    openmp_threads = parameter([1, 2, 4, 7, 8, 14, 28, 56])
#    mpi_ranks = parameter([1, 2, 4, 8, 12, 16, 32, 40, 48, 64])
#    openmp_threads = parameter([1, 2, 4, 8, 12, 16, 32, 40, 48, 64])
    # openmp_threads = parameter([1, 2, 4])
    valid_systems = ['wombat:gpu', 'dom:gpu', 'dom:mc']
    valid_prog_environs = [
        # 'builtin',
        'PrgEnv-arm-N1', 'PrgEnv-arm-TX2', 'PrgEnv-arm-A64FX',
        'PrgEnv-nvidia', 'PrgEnv-nvidia-A64FX',
        'PrgEnv-gnu', 'PrgEnv-gnu-A64FX',
        'PrgEnv-cray'
    ]
    time_limit = '120m'
    use_multithreading = False
    strict_check = False

    #{{{ skip
#     @run_before('run')
#     def set_skip(self):
#         max_ranks = {
#             'dom': {'gpu': 1},
#             #'daint': {'gpu': 12, 'mc': 36},
#             'wombat': {'neoverse-n1': 1, 'TX2': 2, 'A64FX': 4},
#             'lumi': {'gpu': 64},
#         }
#         max_threads = {
#             'dom': {'gpu': 12, 'mc': 36},
#             'daint': {'gpu': 12, 'mc': 36},
#             'wombat': {'neoverse-n1': 40, 'TX2': 64, 'A64FX': 48},
#             'lumi': {'gpu': 64},
#         }
#         self.skip_if(
#             self.mpi_ranks > max_ranks[self.current_system.name][self.current_partition.name],
#             f'{self.mpi_ranks} > max mpi ranks'
#         )
#         self.skip_if(
#             self.openmp_threads > max_threads[self.current_system.name][self.current_partition.name],
#             f'{self.openmp_threads} > max openmp threads'
#         )
    #}}}
    #{{{ run
    @run_before('run')
    def set_hdf5(self):
        # print(self.current_partition.name)
        # print(self.current_environ.name)
        # print(hdf5_mod[self.current_partition.name][self.current_environ.name])
        if hdf5_mod[self.current_partition.name][self.current_environ.name]:
            self.modules = [hdf5_mod[self.current_partition.name][self.current_environ.name]]
#         else:
#             self.prerun_cmds = [
#                 # 'export CMAKE_PREFIX_PATH=/users/piccinal/bin/hdf5/1.13.0:$CMAKE_PREFIX_PATH',
#                 # 'module load cray-hdf5-parallel',
#                 'module load hdf5/1.13.0',
#             ]

    @run_before('run')
    def set_run(self):
        self.executable = '$HOME/affinity'
#        self.mypath = '../build_notool/build/JG/sbin/performance'
#         tests = {
#             'octree': {'name': f'{self.mypath}/octree_perf', 'ranks': '1'},
#             'peers': {'name': f'{self.mypath}/peers_perf', 'ranks': '1'},
#             'scan': {'name': f'{self.mypath}/scan_perf', 'ranks': '1'},
#             'hilbert': {'name': f'{self.mypath}/hilbert_perf', 'ranks': '1'},
#         }
        self.prerun_cmds += [
            'module list',
            'mpicxx --version || true',
            'nvcc --version || true',
            'module rm gnu10/10.2.0 binutils/10.2.0'
        ]
#        self.num_tasks = 1 # topology_mpixomp[self.current_system.name][self.current_partition.name]['s']
#        self.num_tasks_per_node = self.num_tasks
#        self.num_cpus_per_task = max_mpixomp[self.current_system.name][self.current_partition.name]

        self.num_tasks = self.mpi_ranks
        self.num_tasks_per_node = self.mpi_ranks
        self.num_cpus_per_task = self.openmp_threads
        # print(self.num_tasks, self.num_tasks_per_node, self.num_cpus_per_task)

        # self.num_cpus_per_task = topology_mpixomp[self.current_system.name][self.current_partition.name]['cps']
        # self.num_tasks = self.mpi_ranks # 1
        # self.num_tasks_per_node = self.mpi_ranks
        # self.num_cpus_per_task = self.openmp_threads
        #
        # self.num_tasks_per_node = self.mpi_ranks if \
        #     self.mpi_ranks < max_mpixomp[self.current_system.name][self.current_partition.name] \
        #     else max_mpixomp[self.current_system.name][self.current_partition.name]
        #self.num_cpus_per_task = self.openmp_threads // self.mpi_ranks
        #if self.num_cpus_per_task < 1:
        #    self.num_cpus_per_task = 1
        # print(self.openmp_threads, self.mpi_ranks, self.num_cpus_per_task)
        # self.job.launcher =
        # LauncherWrapper(self.job.launcher, 'time', ['-p'])
        # self.skip_if_no_procinfo()
        # procinfo = self.current_partition.processor.info
        mpixomp = self.num_tasks_per_node * self.num_cpus_per_task
        current_max_mpixomp = max_mpixomp[self.current_system.name][self.current_partition.name]
        # skip if too many/too few processes:
        self.skip_if(
            #mpixomp != current_max_mpixomp / 2,
            mpixomp > current_max_mpixomp,
            f'{self.num_tasks_per_node}*{self.num_cpus_per_task}={mpixomp} != {current_max_mpixomp} max mpi*openmp'
        )
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            # 'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
            'OMP_PLACES': 'sockets',
            'OMP_PROC_BIND': 'close',
            'CUDA_VISIBLE_DEVICES': '0',
        }
        mpi_type = ''
        if self.current_system.name in ['wombat']:
            mpi_type = '--mpi=pmix'
            self.job.launcher.options = [mpi_type, 'numactl', '--interleave=all']
            mysrun = f'for ii in `seq {self.repeat}` ;do srun {" ".join(self.job.launcher.options)}'
        elif self.current_system.name in ['dom']:
            mpi_type = ''
            self.job.launcher.options = [mpi_type, 'numactl', '--interleave=all']
            mysrun = f'for ii in `seq {self.repeat}` ;do srun {" ".join(self.job.launcher.options)}'
        elif self.current_system.name in ['dmi']:
            # MUST: salloc THEN ssh THEN rfm -r
            # '--use-hwthread-cpus'
            self.job.launcher.options = [f'-np {self.mpi_ranks}', '--hostfile $OMPI_HOSTFILE', f'--map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS', 'numactl', '--interleave=all']
            mysrun = f'for ii in `seq {self.repeat}` ;do mpirun {" ".join(self.job.launcher.options)}'
            # self.postrun_cmds += [f'mpirun {" ".join(self.job.launcher.options)} {self.executable}']
        else:
            self.job.launcher.options = ['numactl', '--interleave=all']
            mysrun = f'for ii in `seq {self.repeat}` ;do mpirun -np {self.mpi_ranks} --map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS {" ".join(self.job.launcher.options)}'
            self.postrun_cmds += [f'mpirun -np {self.mpi_ranks} --map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS {self.executable}']

        #if self.current_system.name in {'daint', 'dom'}:
        #    self.job.launcher.options = ['numactl', '--interleave=all']
        #self.prerun_cmds += ['echo starttime=`date +%s`']
        if self.analytical in ['analytical']:
            # NOTE: -n 400 means:
            # === Total time for iteration(0) 282.116s = 5min
            # Total execution time of 0 iterations of Sedov: 344.003s (i/o=62) = 6min
            # 6.7G dump_sedov.h5part (1 step, 7168008752/1024^3)
            # 14 variables: c,grad_P_x,grad_P_y,grad_P_z,h,p,rho,u,vx,vy,vz,x,y,z
            # 14 variables * 64e6 particles * 8 b
            # 14*64*1000000*8 = 7'168'000'000
            # cubeside = 100 # 50
            # steps = 30 # 200
            output_frequency = -1 # steps
            #                  r'-o %h.%q{SLURM_NODEID}.%q{SLURM_PROCID}.qdstrm '
            #                  r'--trace=cuda,mpi,nvtx --mpi-impl=mpich '
            #                  r'--delay=2')
            self.tool_opts = (r'nsys profile --force-overwrite=true '
                              r'-o %h.qdstrm '
                              r'--trace=cuda,mpi,nvtx '
                              r'--stats=true ')
            self.postrun_cmds += [
                # sedov
                f'echo sedov: -s={self.steps} -n={self.cubeside}',
                't0=`date +%s` ;'
                f'{mysrun} {self.tool_opts} {self.mypath}/sedov-cuda -n {self.cubeside} -s {self.steps} -w {output_frequency};'
                'done; t1=`date +%s`',
                "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
                'echo "sedov_t=$tt"',
                'echo -e "\\n\\n"',
                #'source ~/myvenv_gcc11_py399/bin/activate',
                #f'ln -s {self.mypath}/sedov_solution',
                #f'python3 {self.mypath}/compare_solutions.py -s {steps} dump_sedov.h5part',
            ]
        else:
            self.postrun_cmds += [
                # octree_perf
                'echo octree_perf:',
                't0=`date +%s` ;'
                f'{mysrun} {self.mypath}/octree_perf ;'
                'done; t1=`date +%s`',
                "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
                'echo "octree_perf_t=$tt"',
                #'echo peers:',
                #f'{mysrun} {self.mypath}/peers_perf',
                # hilbert_perf
                'echo hilbert_perf:',
                't0=`date +%s` ;'
                f'{mysrun} {self.mypath}/hilbert_perf ;'
                'done; t1=`date +%s`',
                "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
                'echo "hilbert_perf_t=$tt"',
            ]
#{{{
#         if self.current_environ.name not in ['PrgEnv-nvidia', 'PrgEnv-nvidia-A64FX']:
#             self.postrun_cmds += [
#                 # scan_perf
#                 'echo scan_perf:',
#                 't0=`date +%s` ;'
#                 f'{mysrun} {self.mypath}/scan_perf ;'
#                 'done; t1=`date +%s`',
#                 "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
#                 'echo "scan_perf_t=$tt"',
#             ]
#         else:
#             self.postrun_cmds += [
#                 'echo "FIXME:"',
#                 'echo "serial scan test: PASS"',
#                 'echo "parallel scan test: PASS"',
#                 'echo "parallel inplace scan test: PASS"',
#                 'echo "scan_perf_t=0"',
#             ]
# 
#}}}
        self.postrun_cmds += [
            #
            'echo "done"',
            #'rm -f core*',
            'echo "SLURMD_NODENAME=$SLURMD_NODENAME"',
            'echo "SLURM_JOBID=$SLURM_JOBID"',
        ]
    #}}}
    #{{{ nsys
    @run_before('run')
    def get_nsys_rpt(self):
        self.postrun_cmds += [
            f'nsys stats --report nvtxsum -f csv --timeunit sec *.nsys-rep > nvtxsum.rpt',
            f'nsys stats --report gpumemsizesum -f csv *.nsys-rep > gpumemsizesum.rpt',
        ]
    #}}}

#     @run_before('run')
#     def set_mpirun(self):
#         if self.current_system.name in ['dmi']:
#             self.job.launcher.options = ['--mca btl_openib_warn_default_gid_prefix 0', '--hostfile ~/jgphpc.git/hpc/reframe/sites/minihpc/hostfile.A100']

    #{{{ sanity
    @sanity_function
    def assert_sanity(self):
        if self.analytical in ['analytical']:
            return sn.all([
                sn.assert_found('Total execution time of \d+ iterations', self.stdout),
            ])
        else:
            regex01 = r'octree_perf_t=\d+'
            regex02 = r'hilbert_perf_t=\d+'
            # regex03 = r'scan_perf_t=\d+'
            regex1 = r'compute time for \d+ hilbert keys: \S+ s on CPU'
            regex2 = r'compute time for \d+ morton keys: \S+ s on CPU'
            # regex3 = r'(serial scan|parallel scan|parallel inplace scan) test: PASS'
            return sn.all([
                sn.assert_found(regex01, self.stdout),
                sn.assert_found(regex1, self.stdout),
                sn.assert_found(regex02, self.stdout),
                sn.assert_found(regex2, self.stdout),
                # sn.assert_found(regex03, self.stdout),
                # sn.assert_found(regex3, self.stdout),
            ])
    #}}}

    #{{{ timers
    @performance_function('cn', perf_key='compute_nodes')
    def report_cn(self):
        return self.compute_nodes

    @performance_function('mpi', perf_key='mpi_ranks')
    def report_mpi(self):
        regex = r'# (\d+) MPI-\S+ process\(es\) with \d+ OpenMP-\S+ thread\(s\)/process'
        return sn.extractsingle(regex, self.stdout, 1, int)
        # return self.num_tasks

    @performance_function('openmp', perf_key='openmp_threads')
    def report_omp(self):
        regex = r'# \d+ MPI-\S+ process\(es\) with (\d+) OpenMP-\S+ thread\(s\)/process'
        return sn.extractsingle(regex, self.stdout, 1, int)
        # return self.num_cpus_per_task

    # 1 MPI-3.1 process(es) with 112 OpenMP-201511 thread(s)/process

    @performance_function('', perf_key='repeat')
    def report_repeat(self):
        return self.repeat

    @performance_function('', perf_key='-n')
    def report_L1_n(self):
        regex = r'sedov: -s=\d+ -n=(\d+)'
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function('steps', perf_key='-s')
    def report_L1_s(self):
        regex = r'sedov: -s=(\d+) -n='
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function('s', perf_key='elapsed_internal')
    def report_elapsed_internal(self):
        # Total execution time of 0 iterations of Sedov: 0.373891s
        regex = r'Total execution time of \d+ iterations of \S+: (?P<s>\S+)s$'
        sec = sn.extractsingle(regex, self.stdout, 's', float)
        return sn.round(sec, 1)

    #{{{ report_regions
    def report_region(self, index):
        # domain::sync: 0.109453s
        # FindNeighbors: 0.781538s
        # Density: 0.13732s
        # EquationOfState: 0.000330948s
        # mpi::synchronizeHalos: 0.00315571s
        # IAD: 0.230027s
        # mpi::synchronizeHalos: 0.0174127s
        # MomentumEnergyIAD: 0.560612s
        # Timestep: 0.0533516s
        # UpdateQuantities: 0.0130277s
        # EnergyConservation: 0.00435739s
        # UpdateSmoothingLength: 0.00656605s
        regex = {
            1: r'^# domain::sync:\s+(?P<sec>.*)s',
            2: r'^# updateTasks:\s+(?P<sec>.*)s',
            3: r'^# FindNeighbors:\s+(?P<sec>.*)s',
            4: r'^# Density:\s+(?P<sec>.*)s',
            5: r'^# EquationOfState:\s+(?P<sec>.*)s',
            6: r'^# mpi::synchronizeHalos:\s+(?P<sec>.*)s',
            7: r'^# IAD:\s+(?P<sec>.*)s',
            8: r'^# MomentumEnergyIAD:\s+(?P<sec>.*)s',
            9: r'^# Timestep:\s+(?P<sec>.*)s',
            10: r'^# UpdateQuantities:\s+(?P<sec>.*)s',
            11: r'^# EnergyConservation:\s+(?P<sec>.*)s',
            12: r'^# UpdateSmoothingLength:\s+(?P<sec>.*)s',
        }
        return sn.round(sn.sum(sn.extractall(regex[index], self.stdout, 'sec', float)), 4)

    @performance_function('s')
    def t_domain_sync(self):
        return self.report_region(1)

    @performance_function('s')
    def t_updateTasks(self):
        return self.report_region(2)

    @performance_function('s')
    def t_FindNeighbors(self):
        return self.report_region(3)

    @performance_function('s')
    def t_Density(self):
        return self.report_region(4)

    @performance_function('s')
    def t_EquationOfState(self):
        return self.report_region(5)

    @performance_function('s')
    def t_mpi_synchronizeHalos(self):
        return self.report_region(6)

    @performance_function('s')
    def t_IAD(self):
        return self.report_region(7)

    @performance_function('s')
    def t_MomentumEnergyIAD(self):
        return self.report_region(8)

    @performance_function('s')
    def t_Timestep(self):
        return self.report_region(9)

    @performance_function('s')
    def t_UpdateQuantities(self):
        return self.report_region(10)

    @performance_function('s')
    def t_EnergyConservation(self):
        return self.report_region(11)

    @performance_function('s')
    def t_UpdateSmoothingLength(self):
        return self.report_region(12)

#}}}

# 
#     #{{{ unittests
#     @performance_function('s', perf_key='octree_perf_t')
#     def report_cput_octree_perf(self):
#         regex = r'octree_perf_t=(\d+)'
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, int) / self.repeat, 2)
# 
#     @performance_function('s', perf_key='hilbert_perf_t')
#     def report_cput_hilbert_perf(self):
#         regex = r'hilbert_perf_t=(\d+)'
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, int) / self.repeat, 2)
# 
# #     @performance_function('s', perf_key='scan_perf_t')
# #     def report_cput_scan_perf(self):
# #         regex = r'scan_perf_t=(\d+)'
# #         return sn.round(sn.extractsingle(regex, self.stdout, 1, int) / self.repeat, 2)
#     #}}}
#     #{{{ hilbert_perf (hilbert, morton)
#     # compute time for 32000000 hilbert keys: 13.2216 s on CPU
#     # compute time for 32000000 morton keys: 0.11014 s on CPU
#     @performance_function('', perf_key='hilbert_perf_keys')
#     def report_keys(self):
#         regex = r'compute time for (\d+) hilbert keys: \S+ s on CPU'
#         return sn.extractsingle(regex, self.stdout, 1, int)
# 
#     @performance_function('s', perf_key='hilbert_perf_hilbert')
#     def report_cput_hilbert(self):
#         regex = r'compute time for \d+ hilbert keys: (\S+) s on CPU'
#         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 5)
# 
#     @performance_function('s', perf_key='hilbert_perf_morton')
#     def report_cput_morton(self):
#         regex = r'compute time for \d+ morton keys: (\S+) s on CPU'
#         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 5)
#     #}}}
#     #{{{ octree_perf
# #{{{There are actually three interesting metrics to extract from this test:
# #   - build time from scratch 0.0577186 nNodes(tree): 441365 count: 2000000 cornerstone construction time
# #   - first td-update: 0.0285318 construction of the internal octree
# #   - td-octree halo discovery: 0.0378064 collidingNodes: 8042 octree-based halo-discovery, a tree traversal benchmark
# #   the other metrics are not adding much in addition, for example the 2nd time you
# #   see build time from scratch it s for a slightly different particle distribution
# #   (plummer instead of gaussian)
# # octree_perf:
# #*build time from scratch 0.174687 nNodes(tree): 441365 count: 2000000
# # build time with guess 0.00604045 nNodes(tree): 441365 count: 2000000 empty nodes: 16309
# # binary tree halo discovery: 0.105535 collidingNodes: 8042
# #*first td-update: 0.0232271
# # second td-update: 0.0231308
# #*td-octree halo discovery: 0.0720088 collidingNodes: 8042
# # plummer box: -55.4645 56.2188 -54.7943 53.6066 -56.9695 57.3319
# # build time from scratch 0.161216 nNodes(tree): 434211 count: 2000000
# # build time with guess 0.00580249 nNodes(tree): 434211 count: 2000000 empty nodes: 15510
# #}}}
#     @performance_function('s', perf_key='octree_perf_cstone_construction')
#     def report_octree_perf_0(self):
#         regex = r'build time from scratch (\S+) nNodes'
#         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 6)
# 
#     @performance_function('s', perf_key='octree_perf_internal_octree')
#     def report_octree_perf_1(self):
#         regex = r'first td-update: (\S+)'
#         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 6)
# 
#     @performance_function('s', perf_key='octree_perf_tree_traversal')
#     def report_octree_perf_2(self):
#         regex = r'td-octree halo discovery: (\S+) collidingNodes'
#         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 6)
# 
#     #{{{
# #     @performance_function('s', perf_key='octree_perf_scratch_max')
# #     def report_octree_perf_0(self):
# #         regex = r'build time from scratch (\S+) nNodes'
# #         return sn.round(sn.max(sn.extractall(regex, self.stdout, 1, float)), 6)
# # 
# #     @performance_function('s', perf_key='octree_perf_scratch_min')
# #     def report_octree_perf_1(self):
# #         regex = r'build time from scratch (\S+) nNodes'
# #         return sn.round(sn.min(sn.extractall(regex, self.stdout, 1, float)), 6)
# # 
# #     @performance_function('s', perf_key='octree_perf_guess_max')
# #     def report_octree_perf_2(self):
# #         regex = r'build time with guess (\S+) nNodes'
# #         return sn.round(sn.max(sn.extractall(regex, self.stdout, 1, float)), 6)
# # 
# #     @performance_function('s', perf_key='octree_perf_guess_min')
# #     def report_octree_perf_3(self):
# #         regex = r'build time with guess (\S+) nNodes'
# #         return sn.round(sn.min(sn.extractall(regex, self.stdout, 1, float)), 6)
#     #}}}
#     #}}}
#     #{{{ scan_perf
# #     # serial benchmark bandwidth: 2035.05 MB/s
# #     # parallel benchmark bandwidth: 8181.65 MB/s
# #     # parallel inplace benchmark bandwidth: 31884.3 MB/s
# #     @performance_function('', perf_key='scan_perf_elements')
# #     def report_scan_perf_0(self):
# #         regex = r'scanning (\d+) elements'
# #         return sn.extractsingle(regex, self.stdout, 1, int)
# # 
# #     @performance_function('MB/s', perf_key='scan_perf_serial')
# #     def report_scan_perf_1(self):
# #         regex = r'serial benchmark bandwidth: (\S+) MB/s'
# #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 2)
# # 
# #     @performance_function('MB/s', perf_key='scan_perf_parallel')
# #     def report_scan_perf_2(self):
# #         regex = r'parallel benchmark bandwidth: (\S+) MB/s'
# #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 2)
# # 
# #     @performance_function('MB/s', perf_key='scan_perf_parallel_inplace')
# #     def report_scan_perf_3(self):
# #         regex = r'parallel inplace benchmark bandwidth: (\S+) MB/s'
# #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1, float)), 2)
#     #}}}
# 
    #}}}
    #{{{ nsys
    #{{{ nvtxsum
    def report_nvtxsum(self, region='___01_domain.sync'):
        regex = r'(?P<pct>\S+),(\S+,){7}PushPop,' + region
        return sn.round(sn.sum(sn.extractall(regex, 'nvtxsum.rpt', 'pct', float)), 2)
        # return sn.extractsingle(regex, 'nvtxsum.rpt', 'pct', float)

    @performance_function('%', perf_key='nsys_domain.sync')
    def nsys_p01(self):
        return self.report_nvtxsum('___01_domain.sync')

    @performance_function('%', perf_key='nsys_FindNeighbors')
    def nsys_p02(self):
        return self.report_nvtxsum('___02_FindNeighbors')

    @performance_function('%', perf_key='nsys_computeDensity')
    def nsys_p03(self):
        return self.report_nvtxsum('___03_computeDensity')

    @performance_function('%', perf_key='nsys_EquationOfState')
    def nsys_p04(self):
        return self.report_nvtxsum('___04_EquationOfState')

    @performance_function('%', perf_key='nsys_synchronizeHalos1')
    def nsys_p05(self):
        return self.report_nvtxsum('___05_synchronizeHalos1')

    @performance_function('%', perf_key='nsys_IAD')
    def nsys_p06(self):
        return self.report_nvtxsum('___06_IAD')

    @performance_function('%', perf_key='nsys_synchronizeHalos2')
    def nsys_p07(self):
        return self.report_nvtxsum('___07_synchronizeHalos2')

    @performance_function('%', perf_key='nsys_MomentumEnergyIAD')
    def nsys_p08(self):
        return self.report_nvtxsum('___08_MomentumEnergyIAD')

    @performance_function('%', perf_key='nsys_Timestep')
    def nsys_p09(self):
        return self.report_nvtxsum('___09_Timestep')

    @performance_function('%', perf_key='nsys_UpdateQuantities')
    def nsys_p10(self):
        return self.report_nvtxsum('___10_UpdateQuantities')

    @performance_function('%', perf_key='nsys_EnergyConservation')
    def nsys_p11(self):
        return self.report_nvtxsum('___11_EnergyConservation')

    @performance_function('%', perf_key='nsys_UpdateSmoothingLength')
    def nsys_p12(self):
        return self.report_nvtxsum('___12_UpdateSmoothingLength')

    @performance_function('%', perf_key='nsys_printIterationTimings')
    def nsys_p13(self):
        return self.report_nvtxsum('___13_printIterationTimings')

    @performance_function('%', perf_key='nsys_MPI')
    def nsys_p14(self):
        return self.report_nvtxsum('MPI:')
    #}}}
    #{{{ gpumemsizesum
    @performance_function('MB')
    def nsys_H2D(self):
        regex = r'(?P<mb>\S+),(\S+,){6}\[CUDA memcpy HtoD\]'
        return sn.extractsingle(regex, 'gpumemsizesum.rpt', 'mb', float)

    @performance_function('MB')
    def nsys_D2H(self):
        regex = r'(?P<mb>\S+),(\S+,){6}\[CUDA memcpy DtoH\]'
        return sn.extractsingle(regex, 'gpumemsizesum.rpt', 'mb', float)
    #}}}

# 
#     #{{{ L1 errors
#     @performance_function('np', perf_key='L1_particles')
#     def report_L1_np(self):
#         regex = r'Loaded (\S+) particles'
#         return sn.extractsingle(regex, self.stdout, 1, int)
# 
#     @performance_function('', perf_key='L1_error_density')
#     def report_L1_density(self):
#         regex = r'Density L1 error (\S+)'
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, float), 6)
# 
#     @performance_function('', perf_key='L1_error_pressure')
#     def report_L1_pressure(self):
#         regex = r'Pressure L1 error (\S+)'
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, float), 6)
# 
#     @performance_function('', perf_key='L1_error_velocity')
#     def report_L1_velocity(self):
#         regex = r'Velocity L1 error (\S+)'
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, float), 6)
#     #}}}
#
#}}}


# x='--module-path +/sw/wombat/ARM_Compiler/21.1/modulefiles --module-path +$HOME/modulefiles'
# ./R -c sedov_cuda.py -n build -r $x # -p PrgEnv-arm-N1 -p PrgEnv-nvidia -p PrgEnv-gnu
# dom: ~/R -c sedov_cuda.py -n build -r -m cudatoolkit/21.5_11.3 -m gcc/9.3.0
# mo use /apps/daint/UES/eurohack/software/nvhpc/2021_219-cuda-11.4/modulefiles
# dom: ~/R -c sedov_cuda.py -n build -r -m nvhpc-nompi/21.5 -p PrgEnv-cray
# dom: ~/R -c sedov_cuda.py -n build -r -m nvhpc-nompi/21.9 -m gcc/9.3.0 -p PrgEnv-gnu
#{{{ build
@rfm.simple_test
class build(rfm.CompileOnlyRegressionTest):
    analytical = parameter(['analytical'])
    use_info = parameter([False])
    use_armpl = parameter(['without_armpl'])
    # use_armpl = parameter(['with_armpl', 'without_armpl'])
    # use_tool = parameter([False, True])
    # use_tool = parameter(['Score-P/7.1-CrayNvidia-21.09'])
    # use_tool = parameter(['Score-P'])
    #sourcepath = '$HOME'
    sourcesdir = 'SPH-EXA.git'
    use_tool = parameter(['notool'])
    # mypath = variable(str, value='.')
    # compute_nodes = parameter([1])
    # compute_nodes = parameter([1, 2, 4, 8, 16])
    # np_per_c = parameter([5.34e6]) #ko 6.4e6
    # sk wants 5.34e6 ok 6.0e6, 6.2e6 does not scale
    # ---- wombat
    # compute_nodes = parameter([1, 2, 4])
    # np_per_c = parameter([45e5]) # OK <------------- -n572 = 187'149'248/2gpu
    #donotscale np_per_c = parameter([47e5]) # OK <------------- -n572 = 187'149'248/2gpu
    # 47e5 ok  / 48e5 ko
    # ----
    valid_systems = ['wombat:gpu', 'dom:gpu', 'dom:mc', 'lumi:gpu']
    valid_prog_environs = [
        # 'builtin',
        'PrgEnv-arm-N1', 'PrgEnv-arm-TX2', 'PrgEnv-arm-A64FX',
        'PrgEnv-nvidia', 'PrgEnv-nvidia-A64FX',
        'PrgEnv-gnu', 'PrgEnv-gnu-A64FX',
        'PrgEnv-cray'
    ]
    # modules = ['gcc/10.3.0', 'Score-P/7.1-CrayNvidia-21.09'] # , 'gcc/9.3.0']
    # modules = ['Nsight-Systems/2022.1.1', 'Nsight-Compute/2022.1.0']
    # sedov-cuda': corrupted double-linked list: 0x000000000084f570 ***
    # --> load PrgEnv-cray + gcc
    # valid_prog_environs = ['PrgEnv-gnu']
    # modules = ['daint-gpu', 'ParaView']
    # modules = ['CMake',] # 'PrgEnv-cray', 'gcc/9.3.0']

    #{{{ compile
    @run_before('compile')
    def set_compile(self):
        self.build_system = 'CMake'
        if hdf5_mod[self.current_partition.name][self.current_environ.name]:
            self.modules = [hdf5_mod[self.current_partition.name][self.current_environ.name]]

        compiler_flags = {
            'mc':
                {'PrgEnv-cray': '',
                 'PrgEnv-gnu': '',
                 'PrgEnv-intel': '',
                 'PrgEnv-nvidia': '',
                },
            'gpu':
                {'PrgEnv-cray': '',
                 'PrgEnv-gnu': '',
                 'PrgEnv-intel': '',
                 'PrgEnv-nvidia': '',
                },
            'a100':
                {'PrgEnv-cray': '',
                 'PrgEnv-gnu': '-mcpu=cascadelake',
                 'PrgEnv-intel': '',
                 'PrgEnv-nvidia': '',
                },
            # [current_partition.name][current_environ.name]
            'neoverse-n1':
                {'PrgEnv-arm-N1': '-g -mcpu=neoverse-n1',
                 'PrgEnv-gnu': '-g -mcpu=neoverse-n1',
                 'PrgEnv-nvidia': '-tp=neoverse-n1',
# -tp=host|native|neoverse-n1
#     host            Link native version of HPC SDK cpu math library
#     native          Alias for -tp host
#     neoverse-n1     Arm Neoverse N1 architecture
# Jeff Hammond (NVIDIA): NVC++ currently doesn’t specialize for ARM microarchitectures
                },
            'TX2':
                {'PrgEnv-arm-TX2': '-g -mcpu=thunderx2t99',
                 'PrgEnv-gnu': '-g -mcpu=thunderx2t99',
                 'PrgEnv-nvidia': '-tp=host',
                },
            'A64FX':
                {'PrgEnv-arm-A64FX': '-g -mcpu=a64fx',
                 'PrgEnv-gnu-A64FX': '-g -mcpu=a64fx',
                # i.e -march=armv8.2-a+sve -mtune=a64fx (Wael Elwasif)
                 'PrgEnv-nvidia-A64FX': '',
                },
        }
# module load /ccsopen/home/piccinal/bin/nvidia/hpc_sdk/modulefiles/nvhpc/22.2
# module load nvhpc/22.2
# NVIDIA: remove -fno-math-errno / neoverse-n1/PrgEnv-nvidia/build_with_armpl_notool
# NVIDIA: gnu10/10.2.0 + armpl-AArch64/21.1.0 + nvhpc-nompi/22.1 =
# /autofs/nccs-svm1_wombat_sw/CentOS8/spack/opt/spack/linux-centos8-thunderx2/gcc-10.2.0/gcc-11.1.0-uw6b7xkoq2wqxsaq4q6bl3wpaulxnehx/lib/gcc/aarch64-unknown-linux-gnu/11.1.0/../../../../include/c++/11.1.0/bits/stl_vector.h:346:
# undefined reference to `std::__throw_bad_array_new_length()'
        self.build_system.flags_from_environ = False
        if self.current_environ.name in ['PrgEnv-gnu', 'PrgEnv-gnu-A64FX']:
            self.prebuild_cmds = [
                'module rm gnu10/10.2.0 binutils/10.2.0',
                # dom: 'module load cray-hdf5-parallel',
                #'module load hdf5/1.13.0',
            ]
        elif self.current_environ.name in ['PrgEnv-nvidia', 'PrgEnv-nvidia-A64FX']:
            self.prebuild_cmds = [
                'sed -i "s@-fno-math-errno@@" CMakeLists.txt',
                'sed -i "s@-Wno-unknown-pragmas@-w@" domain/test/coord_samples/CMakeLists.txt',
                'sed -i "s@-Wno-unknown-pragmas@-w@" domain/test/integration_mpi/CMakeLists.txt',
                #'sed -i "s@-Wno-unknown-pragmas@-w@" domain/test/unit/CMakeLists.txt',
                'sed -i "s@-Wno-unknown-pragmas@-w@" ryoanji/test/cpu/CMakeLists.txt',
                'echo > src/evrard/CMakeLists.txt',
                # 1 catastrophic error detected in the compilation of
                # "src/evrard/evrard.cpp".
                'echo > domain/test/unit/CMakeLists.txt',
                'echo > ryoanji/test/cpu/CMakeLists.txt',
                '## echo > src/analytical_solutions/CMakeLists.txt',
                # sedov_solution/main.cpp", line 134: error: namespace "std"
                # has no member "setw"
                # TODO: domain/test/integration_mpi/CMakeLists.txt / 
                # mpi_wrappers.hpp, line 115: internal error: assertion failed:
                # missing rescan info (exprutil.cpp, line 4772 in
                # get_expr_rescan_info)
                'sed -i "s@addMpiTest(exchange_focus.cpp@#addMpiTest(exchange_focus.cpp@" domain/test/integration_mpi/CMakeLists.txt',
                'sed -i "s@addMpiTest(exchange_general.cpp@#addMpiTest(exchange_general.cpp@" domain/test/integration_mpi/CMakeLists.txt',
                # avoid warnings:
                'echo >> domain/include/cstone/cuda/annotation.hpp',
                'echo >> domain/include/cstone/traversal/collisions.hpp',
                'echo >> domain/include/cstone/tree/btree.cuh',
                'echo >> domain/include/cstone/traversal/peers.hpp',
                'echo >> domain/test/performance/timing.cuh',
                'echo >> ryoanji/src/ryoanji/cpu/multipole.hpp',
                'echo >> domain/include/cstone/cuda/gather.cu',
            ]
        elif self.current_environ.name in ['PrgEnv-arm-N1', 'PrgEnv-arm-TX2', 'PrgEnv-arm-A64FX']:
            self.prebuild_cmds = [
                'sed -i "s@inline static constexpr std::array fieldNames@inline static std::array fieldNames@" include/particles_data.hpp',
            ]

        info_flag = {
            'PrgEnv-gnu': '-fopt-info-vec-missed',
            'PrgEnv-gnu-A64FX': '-fopt-info-vec-missed',
            #
            # -fsave-optimization-record
            'PrgEnv-arm-N1': '-Rpass-analysis=loop-vectorize',
            'PrgEnv-arm-TX2': '-Rpass-analysis=loop-vectorize',
            'PrgEnv-arm-A64FX': '-Rpass-analysis=loop-vectorize',
            #
            'PrgEnv-nvidia': '-Minfo',
            'PrgEnv-nvidia-A64FX': '-Minfo',
        }
        compiler_info_flag = ''
        if self.use_info:
            compiler_info_flag = info_flag[self.current_environ.name]

        self.prebuild_cmds += [
            'module list',
            'mpicxx --version || true',
            'nvcc --version || true',
            'rm -fr docs LICENSE Makefile README.* scripts test tools',
            'sed -i "s@project(sphexa CXX C)@project(sphexa CXX)@" CMakeLists.txt',
            f'sed -i "s@-march=native@{compiler_flags[self.current_partition.name][self.current_environ.name]} {compiler_info_flag}@" CMakeLists.txt',
            'sed -i "s@constexpr operator MPI_Datatype@operator MPI_Datatype@" domain/include/cstone/primitives/mpi_wrappers.hpp',
        ]
# --partition=Ampere --> -mcpu=neoverse-n1
# --partition=TX2    --> -mcpu=thunderx2t99
# --partition=A64fx  --> -mcpu=a64fx+sve or -mcpu=armv8-a+sve ?
        # if self.current_partition.name in ['neoverse-n1']:
        # if self.current_partition.name in ['TX2']:
        # if self.current_partition.name in ['A64FX']:
        # self.current_environ.name
#       # 'unset CPATH'
        if self.current_partition.name in ['A64FX']:
            self.build_system.nvcc = ''
#             if self.current_environ.name in ['PrgEnv-gnu-A64FX']:
#                 self.prebuild_cmds += [
#                     'module rm /sw/wombat/ARM_Compiler/20.0/modulefiles/ThunderX2CN99/RHEL/7/gcc-9.2.0/armpl/20.0.0',
#                     'module load /sw/wombat/ARM_Compiler/20.3/modulefiles/A64FX/RHEL/8/gcc-9.3.0/armpl/20.3.0',
#                     'module rm gcc/11.1.0 ;module load gcc/11.1.0',
#                 ]

        self.build_system.builddir = 'build'
        # self.executable = f'{self.mypath}/sedov-cuda'
        # self.executable_name = self.executable.split("/")[-1]
        # self.build_system.config_opts = ['-DCMAKE_CXX_COMPILER=mpicxx',
        self.build_system.config_opts = [
            #'-DCMAKE_CXX_COMPILER=CC',
            #"-DCMAKE_CUDA_FLAGS='-ccbin cc'",
            '-DCMAKE_CXX_COMPILER=mpicxx',
            "-DCMAKE_CUDA_FLAGS='-ccbin mpicxx'",
            #'-DCMAKE_CUDA_COMPILER=`which nvcc`',
            # f'-DCMAKE_CUDA_COMPILER={self.hasnvcc}',
            '-DBUILD_TESTING=ON',
            '-DBUILD_ANALYTICAL=ON',
            '-DSPH_EXA_WITH_HIP=OFF',
            '-DBUILD_RYOANJI=ON',
            '-DCMAKE_INSTALL_PREFIX=$PWD/JG',
            #'-DCMAKE_BUILD_TYPE=Debug',
            '-DCMAKE_BUILD_TYPE=Release',
            # '-DCMAKE_CXX_FLAGS_RELEASE="-O3 -fno-math-errno -march=armv8-a -DNDEBUG"',
            # '-DCMAKE_CUDA_FLAGS="-arch=sm_80 -ccbin mpicxx -DNDEBUG -std=c++17"',
            # '-DCMAKE_BUILD_TYPE=Release',
            # -DCMAKE_CXX_COMPILER=mpicxx -DCMAKE_CUDA_COMPILER=nvcc -DBUILD_TESTING=OFF -DBUILD_ANALYTICAL=OFF -DSPH_EXA_WITH_HIP=OFF
            # -DBUILD_RYOANJI=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_FLAGS="-arch=sm_80 -ccbin mpicxx -DNDEBUG -std=c++17" -DUSE_PROFILING=ON
        ]

        if self.use_armpl == 'with_armpl':
            if self.current_environ.name in ['PrgEnv-arm-N1', 'PrgEnv-arm-TX2', 'PrgEnv-arm-A64FX']:
                self.build_system.config_opts += ["-DCMAKE_EXE_LINKER_FLAGS=-armpl"]
            else:
                if self.current_environ.name in ['PrgEnv-nvidia', 'PrgEnv-nvidia-A64FX']:
                    self.skip_if(self.use_armpl == 'with_armpl', 'no armpl with nvhpc compilers')
                    self.build_system.config_opts += ["-DCMAKE_EXE_LINKER_FLAGS='-lgfortran -larmpl'"]
                else:
                    self.build_system.config_opts += ["-DCMAKE_EXE_LINKER_FLAGS='-larmpl'"]

        if self.use_tool:
            self.build_system.config_opts += ['-DUSE_PROFILING=ON']
        else:
            self.build_system.config_opts += ['-DUSE_PROFILING=OFF']

        self.build_system.max_concurrency = 10
        self.build_system.make_opts = ['sedov'] # ['install']
        if self.use_info:
            self.build_system.make_opts = ['hilbert_perf']

#{{{
#         if self.current_environ.name in ['PrgEnv-nvidia', 'PrgEnv-nvidia-A64FX']:
#             self.build_system.make_opts = ['octree_perf', 'hilbert_perf', 'scan_perf']
#             self.postbuild_cmds += [
#                 'mkdir -p JG/sbin/performance',
#                 'cp domain/test/performance/octree_perf JG/sbin/performance',
#                 'cp domain/test/performance/hilbert_perf JG/sbin/performance',
#                 'cp domain/test/performance/scan_perf JG/sbin/performance',
#             ]
#         else:
#             self.build_system.make_opts = ['install']
#             #'install',
#             #'octree_perf', 'VERBOSE=1',
#             # self.executable_name,
#             # 'sedov',
#             # 'sedov_solution',
#}}}

        self.postbuild_cmds += [
            'ldd domain/test/performance/octree_perf |grep armpl || true',
        ]
    #}}}

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_not_found('error', self.stdout),
        ])
#}}}
