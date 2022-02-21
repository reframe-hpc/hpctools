# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

# import contextlib
import reframe as rfm
import reframe.utility.sanity as sn
# from reframe.core.launchers import LauncherWrapper

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
    compute_nodes = parameter([1])
    steps = parameter([200]) # 10
    # compute_nodes = parameter([0, 1, 2, 4])
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
    valid_systems = ['wombat:gpu', 'dom:gpu']
    valid_prog_environs = ['builtin', 'PrgEnv-gnu', 'PrgEnv-arm', 'PrgEnv-arm-TX2', 'PrgEnv-nvidia']
    # modules = ['gcc/10.3.0', 'Score-P/7.1-CrayNvidia-21.09'] # , 'gcc/9.3.0']
    # modules = ['Nsight-Systems/2022.1.1', 'Nsight-Compute/2022.1.0']
    # sedov-cuda': corrupted double-linked list: 0x000000000084f570 ***
    # --> load PrgEnv-cray + gcc
    # valid_prog_environs = ['PrgEnv-gnu']
    # modules = ['daint-gpu', 'ParaView']
    # modules = ['CMake',] # 'PrgEnv-cray', 'gcc/9.3.0']
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
            self.np_per_c = 10e6
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
            'echo SLURMD_NODENAME=$SLURMD_NODENAME',
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
            self.executable_opts += [f'-w', '{self.steps}']
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

    #{{{ performance_function
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

    def report_region(self, index):
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

# 00_init
# 00_box
# -g runs ok
# cube_stat
# cube_calltree -m time -i  profile.cubex -a -c / ok on juwels
#}}}


# ~/Ampere -c sedov_cuda.py -n build_sedov -p PrgEnv-arm$ -r
# ~/TX2 -c sedov_cuda.py -n build_sedov -p PrgEnv-arm-TX2 -r
# ~/A64FX -c sedov_cuda.py -n build_sedov -p PrgEnv-arm-A64FX -r
# ~/R -c sedov_cuda.py -n build -p PrgEnv-gnu -r -m cudatoolkit/21.5_11.3 -m gcc/9.3.0
#{{{ build
@rfm.simple_test
class build_sedov(rfm.CompileOnlyRegressionTest):
    # use_tool = variable(bool, value=False)
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
    # steps = parameter([10]) # 10
    # insitu = parameter(['none', 'Catalyst'])
    valid_systems = ['wombat:gpu', 'dom:gpu']
    valid_prog_environs = ['builtin', 'PrgEnv-gnu', 'PrgEnv-arm', 'PrgEnv-nvidia', 'PrgEnv-arm-TX2', 'PrgEnv-arm-A64FX']
    # modules = ['gcc/10.3.0', 'Score-P/7.1-CrayNvidia-21.09'] # , 'gcc/9.3.0']
    # modules = ['Nsight-Systems/2022.1.1', 'Nsight-Compute/2022.1.0']
    # sedov-cuda': corrupted double-linked list: 0x000000000084f570 ***
    # --> load PrgEnv-cray + gcc
    # valid_prog_environs = ['PrgEnv-gnu']
    # modules = ['daint-gpu', 'ParaView']
    # modules = ['CMake',] # 'PrgEnv-cray', 'gcc/9.3.0']
    # time_limit = '25m'
    # use_multithreading = False
    # strict_check = False
    # executable = variable(str, value='$HOME/sedov-cuda')

    #{{{ compile
    @run_before('compile')
    def set_compile(self):
        self.build_system = 'CMake'
        self.prebuild_cmds = [
            'module list',
            'rm -fr docs LICENSE Makefile README.* scripts test tools',
        ]
        if self.current_environ.name in ['PrgEnv-nvidia', 'builtin']:
            self.prebuild_cmds += [
                'sed -i "s@-fno-math-errno@@" CMakeLists.txt',
                # 'unset CPATH'
            ]
        elif self.current_environ.name in ['PrgEnv-arm', 'PrgEnv-arm-TX2']:
            self.prebuild_cmds += [
                'sed -i "s@-march=native@-march=armv8-a@" CMakeLists.txt',
                'sed -i "s@constexpr operator MPI_Datatype@operator MPI_Datatype@" domain/include/cstone/primitives/mpi_wrappers.hpp',
            ]
        elif self.current_environ.name in ['PrgEnv-arm-A64FX']:
            self.prebuild_cmds += [
                'sed -i "s@-march=native@-march=armv8-a+sve@" CMakeLists.txt',
                'sed -i "s@constexpr operator MPI_Datatype@operator MPI_Datatype@" domain/include/cstone/primitives/mpi_wrappers.hpp',
            ]

        self.build_system.builddir = 'build'
        # self.executable = f'{self.mypath}/sedov-cuda'
        # self.executable_name = self.executable.split("/")[-1]
        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            self.executable_name = 'sedov'
        else:
            self.executable_name = 'sedov-cuda'

        #     self.build_system.config_opts = ['-DCMAKE_CXX_COMPILER=mpicxx',
        self.build_system.config_opts = [
            # '-DCMAKE_CXX_COMPILER=mpicxx',
            '-DCMAKE_CUDA_COMPILER=nvcc',
            '-DBUILD_TESTING=OFF',
            '-DBUILD_ANALYTICAL=ON',
            '-DSPH_EXA_WITH_HIP=OFF',
            '-DBUILD_RYOANJI=OFF',
            '-DCMAKE_BUILD_TYPE=Release',
            # '-DCMAKE_CXX_FLAGS_RELEASE="-O3 -fno-math-errno -march=armv8-a -DNDEBUG"',
            # '-DCMAKE_CUDA_FLAGS="-arch=sm_80 -ccbin mpicxx -DNDEBUG -std=c++17"',
            # '-DCMAKE_BUILD_TYPE=Release',
            # -DCMAKE_CXX_COMPILER=mpicxx -DCMAKE_CUDA_COMPILER=nvcc -DBUILD_TESTING=OFF -DBUILD_ANALYTICAL=OFF -DSPH_EXA_WITH_HIP=OFF
            # -DBUILD_RYOANJI=OFF -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_FLAGS="-arch=sm_80 -ccbin mpicxx -DNDEBUG -std=c++17" -DUSE_PROFILING=ON
        ]

        if self.use_tool:
            self.build_system.config_opts += ['-DUSE_PROFILING=ON']
        else:
            self.build_system.config_opts += ['-DUSE_PROFILING=OFF']

        self.build_system.make_opts = [
            self.executable_name,
            'sedov_solution',
            # VERBOSE=1,
        ]
        self.build_system.max_concurrency = 20
        # self.postbuild_cmds = []
    #}}}

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_not_found('error', self.stdout),
        ])
#}}}
