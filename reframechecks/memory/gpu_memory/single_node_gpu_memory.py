import reframe as rfm
import reframe.utility.sanity as sn
import os
# import numpy as np


# {{{ gpu memory
@rfm.simple_test
class np_max_test(rfm.RunOnlyRegressionTest):
    """
    # spack load environment-modules
    source /data/home/jgpiccinal/git/spack.git/opt/spack/linux-sle_hpc15-zen/gcc-7.5.0/environment-modules*/init/bash
    module use /scratch/shared/spack/share/spack/modules/linux-sle_hpc15-zen
    # module use ~/git/spack.git/share/spack/modules/linux-sle_hpc15-zen
    # module use ~/git/spack.git/share/spack/modules/linux-sle_hpc15-zen2
    """
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

    # {{{
#     @run_after('init')
#     def set_variables(self):
#         self.array_size = (self.num_bytes >> 3) // 3
#         self.ntimes = 100*1024*1024 // self.array_size
#         self.descr = (
#             f'STREAM test (array size: {self.array_size}, '
#             f'ntimes: {self.ntimes})'
#         )
# 
#     @run_before('compile')
#     def set_compiler_flags(self):
#         self.build_system.cppflags = [f'-DSTREAM_ARRAY_SIZE={self.array_size}',
#                                       f'-DNTIMES={self.ntimes}']
#         environ = self.current_environ.name
#         self.build_system.cflags = self.flags.get(environ, [])
# }}}

    @run_before('run')
    def set_cubeside(self):
        phys_core_per_node = self.cores.get(self.current_partition.fullname, 1)
        # total_np = (phys_core_per_node * self.np_per_c)
        total_np = (phys_core_per_node * self.mpi_rks * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        # self.executable = '/scratch/snx3000/piccinal/SPH-EXA_mini-app.git/JG/src/sedov/sedov-cuda'
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
        return  sn.extractsingle(regex, self.stdout, 1, int)
        # n_particles = sn.evaluate(sn.extractsingle(regex, self.stdout, 1, int))
        # return f'{n_particles:.1E}'
        # the value extracted for performance variable 'daint:gpu:nparticles' is not a number: 1.2E+07
        # return np.format_float_scientific(n_particles, precision=2, exp_digits=1)

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

#     @performance_function('MB/s', perf_key='Triad')
#     def extract_triad_bw(self):
#         return sn.extractsingle(r'Triad:\s+(\S+)\s+.*', self.stdout, 1, float)
    # }}}
# }}}


# {{{ no tool
@rfm.simple_test
class np_max_test_notool(rfm.RunOnlyRegressionTest):
    """
    # spack load environment-modules
    source /data/home/jgpiccinal/git/spack.git/opt/spack/linux-sle_hpc15-zen/gcc-7.5.0/environment-modules*/init/bash
    module use /scratch/shared/spack/share/spack/modules/linux-sle_hpc15-zen
    # module use ~/git/spack.git/share/spack/modules/linux-sle_hpc15-zen
    # module use ~/git/spack.git/share/spack/modules/linux-sle_hpc15-zen2
    """
    # omp_threads = parameter([12, 24])
    # omp_threads = parameter([1, 2, 3, 4, 6, 8, 10, 12, 16, 32, 64])
    # omp_threads = parameter([64, 80, 96, 112, 128])
    omp_threads = parameter([1, 4, 8, 16, 32, 64, 96, 128])
    # omp_threads = parameter([1, 12, 16, 32, 48, 64, 80, 96, 112, 128])
    # omp_threads = parameter([12])
    # mpi_rks = parameter([1, 2])
    np_per_c = parameter([
        # 1.0e6, # 1.8e6,
        # 2.0e6,
        # 2.0e6, 2.2e6, 2.4e6, 2.6e6, 2.8e6,
        # 3.0e6, 3.2e6, 3.4e6, 3.6e6, 3.8e6,
        # 4.0e6, 4.2e6, 4.4e6, 4.6e6, 4.8e6,
        # 5.0e6, 5.2e6, 5.4e6, 5.6e6, 5.8e6,
        5.4e6,
        # 6.0e6, 6.2e6, 6.4e6, 6.6e6, 6.8e6 # oom: 6.8e6,
        # 7.0e6, 8.0e6, 9.0e6, 10.0e6, 11.0e6, 12.0e6
        # 12.0e6, 12.2e6, 12.4e6, 12.6e6, 12.8e6,
    ])
    mpi_rks = parameter([1])
    # np_per_c = parameter([1e6])
    steps = variable(str, value='9')
    exe_path = variable(str, value='/home/jgpiccinal/git/SPH-EXA_mini-app.git')

    # --bind-to socket
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcesdir = None
    prerun_cmds = [
        'mpirun --version',
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
        # self.executable = '/scratch/snx3000/piccinal/SPH-EXA_mini-app.git/JG/src/sedov/sedov-cuda'
        # self.executable = f'{self.exe_path}/sedov-cuda'
        self.executable = f' '
        self.executable_opts += [
            # --report-bindings
            '--bind-to', 'none', 'numactl', '--interleave=all',
            # '--bind-to socket',
            f'{self.exe_path}/sedov-cuda',
            f"-n {self.cubeside}", f"-s {self.steps}"
        ]

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
        return  sn.extractsingle(regex, self.stdout, 1, int)
        # n_particles = sn.evaluate(sn.extractsingle(regex, self.stdout, 1, int))
        # return f'{n_particles:.1E}'
        # the value extracted for performance variable 'daint:gpu:nparticles' is not a number: 1.2E+07
        # return np.format_float_scientific(n_particles, precision=2, exp_digits=1)

    @performance_function('s')
    def elapsed(self):
        regex = r'# Total execution time of \d+ iterations of \S+: (\S+)s'
        return sn.extractsingle(regex, self.stdout, 1, float)
    # }}}
# }}}
