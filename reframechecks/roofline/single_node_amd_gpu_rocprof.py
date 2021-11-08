import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher

import os


# {{{ rocprof_stats
@rfm.simple_test
class rocprof_stats(rfm.RunOnlyRegressionTest):
    """
    module use /scratch/shared/spack/share/spack/modules/linux-sle_hpc15-zen
    # module use ~/git/spack.git/share/spack/modules/linux-sle_hpc15-zen
    # module use ~/git/spack.git/share/spack/modules/linux-sle_hpc15-zen2
    """
    # omp_threads = parameter([12, 24])
    omp_threads = parameter([12])
    # mpi_rks = parameter([1, 2])
    np_per_c = parameter([
        1.0e6, 2.0e6, 3.0e6, 4.0e6, 6.0e6, 8.0e6, 10.0e6, 11.0e6,
        # 1.0e6,
        # 2.0e6, 2.2e6, 2.4e6, 2.6e6, 2.8e6,
        # 3.0e6, 3.2e6, 3.4e6, 3.6e6, 3.8e6,
        # 4.0e6, 4.2e6, 4.4e6, 4.6e6, 4.8e6,
        # 5.0e6, 5.2e6, 5.4e6, 5.6e6, 5.8e6,
        # 6.0e6, 6.2e6, 6.4e6, 6.6e6, 6.8e6 # oom: 6.8e6,
        # 7.0e6, 8.0e6, 9.0e6, 10.0e6, 11.0e6, 12.0e6
        # 12.0e6, 12.2e6, 12.4e6, 12.6e6, 12.8e6,
    ])
    mpi_rks = parameter([1])
    # np_per_c = parameter([1e6])
    steps = variable(str, value='3')
    # steps = variable(str, value='0')
    exe_path = variable(str, value='/home/jgpiccinal/git/SPH-EXA_mini-app.git')
    rpt_file = variable(str, value='results.stats.csv')

    valid_systems = ['*']
    valid_prog_environs = ['*']
    # modules = ['cdt-cuda/21.05', 'cudatoolkit/11.2.0_3.39-2.1__gf93aa1c']
    # sourcesdir = None
    prerun_cmds = [
        'mpirun --version',
        # './smi.sh &',
    ]
    # prerun_cmds = ['module list']
    # postrun_cmds = [
    #     r"sleep 1",  # give jobreport a chance
    #     r"pid=`ps x |grep smi.sh |grep -v grep |awk '{print $1}'`",
    #     r"for i in $pid ;do kill $i ;done",
    # ]
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
    def set_profiler(self):
        # mpirun -np 1 <self.job.launcher.options> ./myexe ...
        self.job.launcher.options = ['rocprof', '--basenames', 'on', '--stats']

#     @run_before('run')
#     def pre_launch(self):
#         cmd = self.job.launcher.run_command(self.job)
#         self.prerun_cmds = [
#             f'{cmd} -n {n} {self.executable}'
#             for n in range(1, self.num_tasks)
#         ]

    @run_before('run')
    def set_num_threads(self):
        # num_threads = self.cores.get(self.current_partition.fullname, 1)
        # self.num_cpus_per_task = num_threads
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = self.omp_threads
        self.variables = {
            'LD_LIBRARY_PATH': f'{self.exe_path}:$LD_LIBRARY_PATH',
            'HIP_VISIBLE_DEVICES': '0',
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
    def np(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function('s')
    def elapsed(self):
        regex = r'# Total execution time of \d+ iterations of \S+: (\S+)s'
        return sn.extractsingle(regex, self.stdout, 1, float)

    # computeMomentumAndEnergyIAD / findNeighborsKernel / computeIAD / density
    @performance_function('%')
    def rocprof_stats_computeMomentumAndEnergyIAD(self):
        """
        "Name","Calls","TotalDurationNs","AverageNs","Percentage"
        "findNeighborsKernel",192,2334058542,12156554,47.20607754469413
        "computeMomentumAndEnergyIAD",64,1796800226,28075003,36.34008713774581
        """
        # regex = '^\"(\S+)\",.*,(\S+)\d$'
        regex = r'^\"computeMomentumAndEnergyIAD\",.*,(\S+)\d$'
        rpt = os.path.join(self.stagedir, self.rpt_file)
        return sn.round(sn.extractsingle(regex, rpt, 1, float), 1)
        # return sn.round(sn.extractall(regex, rpt, 2, float)[0], 1)

    @performance_function('%')
    def rocprof_stats_findNeighborsKernel(self):
        regex = r'^\"findNeighborsKernel\",.*,(\S+)\d$'
        rpt = os.path.join(self.stagedir, self.rpt_file)
        return sn.round(sn.extractsingle(regex, rpt, 1, float), 1)

    @performance_function('%')
    def rocprof_stats_computeIAD(self):
        regex = r'^\"computeIAD\",.*,(\S+)\d$'
        rpt = os.path.join(self.stagedir, self.rpt_file)
        return sn.round(sn.extractsingle(regex, rpt, 1, float), 1)

    @performance_function('%')
    def rocprof_stats_density(self):
        regex = r'^\"density\",.*,(\S+)\d$'
        rpt = os.path.join(self.stagedir, self.rpt_file)
        return sn.round(sn.extractsingle(regex, rpt, 1, float), 1)

#     @performance_function('B')
#     def max_gpu_memory_b(self):
#         # GPU[0] : VRAM Total Used Memory (B): 2228006912
#         regex = r'VRAM Total Used Memory \(B\): (\d+)'
#         rpt = os.path.join(self.stagedir, self.rpt_file)
#         return sn.max(sn.extractall(regex, rpt, 1, int))
#
#     @performance_function('MB/s', perf_key='Triad')
    # }}}
# }}}


# {{{ rocprof_roofline_data
@rfm.simple_test
class rocprof_roofline_data(rfm.RunOnlyRegressionTest):
    """
    ~/R -c single_node_gpu_rocprof.py -n rocprof_roofline -r -p PrgEnv-gnu
    """
    # omp_threads = parameter([12, 24])
    omp_threads = parameter([12])
    # mpi_rks = parameter([1, 2])
    np_per_c = parameter([
        6.0e6, 8.0e6,
        # 1.0e6, 2.0e6, 3.0e6, 4.0e6, 6.0e6, 8.0e6, 10.0e6, 11.0e6,
        # 1.0e5,
        # 2.0e6, 2.2e6, 2.4e6, 2.6e6, 2.8e6,
        # 3.0e6, 3.2e6, 3.4e6, 3.6e6, 3.8e6,
        # 4.0e6, 4.2e6, 4.4e6, 4.6e6, 4.8e6,
        # 5.0e6, 5.2e6, 5.4e6, 5.6e6, 5.8e6,
        # 6.0e6, 6.2e6, 6.4e6, 6.6e6, 6.8e6 # oom: 6.8e6,
        # 7.0e6, 8.0e6, 9.0e6, 10.0e6, 11.0e6, 12.0e6
        # 12.0e6, 12.2e6, 12.4e6, 12.6e6, 12.8e6,
    ])
    mpi_rks = parameter([1])
    # np_per_c = parameter([1e6])
    steps = variable(str, value='4')
    # steps = variable(str, value='0')
    exe_path = variable(str, value='/home/jgpiccinal/git/SPH-EXA_mini-app.git')
    metric_file = variable(str, value='pmc.txt')
    rpt_file = variable(str, value='results.stats.csv')

    # time_limit = '60m'
    valid_systems = ['*']
    valid_prog_environs = ['*']
    # modules = ['cdt-cuda/21.05', 'cudatoolkit/11.2.0_3.39-2.1__gf93aa1c']
    # sourcesdir = None
    # postrun_cmds = [
    #     r"sleep 1",  # give jobreport a chance
    #     r"pid=`ps x |grep smi.sh |grep -v grep |awk '{print $1}'`",
    #     r"for i in $pid ;do kill $i ;done",
    # ]
    # Number of cores for each system
    cores = variable(dict, value={
        'daint:gpu': 12,
        'lumi:login': 12,  # 128
    })

    @run_before('run')
    def set_tool_input(self):
        self.prerun_cmds = [
            'mpirun --version', 'module list',
            '# {{{ pmc.txt:',
            f'echo "pmc : FetchSize SQ_INSTS_VALU" > {self.metric_file}',
            f'echo "pmc : WriteSize SQ_INSTS_SALU" >> {self.metric_file}',
            f'echo "range:" >> {self.metric_file}',
            f'echo "gpu: 0" >> {self.metric_file}',
            f'echo "kernel:" >> {self.metric_file}',
            '# }}}',
        ]

    @run_before('run')
    def set_cubeside(self):
        phys_core_per_node = self.cores.get(self.current_partition.fullname, 1)
        # total_np = (phys_core_per_node * self.np_per_c)
        total_np = (phys_core_per_node * self.mpi_rks * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        # self.executable = f'{self.exe_path}/sedov-cuda'
        # self.executable_opts += [f"-n {self.cubeside}", f"-s {self.steps}"]

    @run_before('run')
    def set_profiler(self):
        # mpirun ko: orte_ess_init failed
        # --> Returned value No permission (-17) instead of ORTE_SUCCESS
        # [mpirun -np 1 <self.job.launcher.options>] ./myexe ...
        # https://github.com/open-mpi/ompi/issues/6981
        # https://github.com/open-mpi/ompi/issues/8017
        self.job.launcher = getlauncher('local')()
        self.executable = 'rocprof'
        self.executable_opts += [
            '-i', self.metric_file, '--timestamp', 'on', '--basenames', 'on',
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
            'OMP_NUM_THREADS': str(self.omp_threads),
            # 'OMP_PLACES': 'cores'
        }

    @sanity_function
    def check_execution(self):
        regex = r'Total execution time of \d+ iterations of \S+'
        return sn.assert_found(regex, self.stdout)

    # {{{ performance
    # {{{ metadata:
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
    def np(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function('s')
    def elapsed(self):
        regex = r'# Total execution time of \d+ iterations of \S+: (\S+)s'
        return sn.extractsingle(regex, self.stdout, 1, float)
    # }}}

    # {{{ regex:
    # computeMomentumAndEnergyIAD / findNeighborsKernel / computeIAD / density
    # {{{ columns of pmc.csv:
    # 1 Index           571                 560
    # 2 KernelName      computeMomentum...  findNeighborsKernel
    # 3 gpu-id          0                   0
    # 4 queue-id        0                   1
    # 5 queue-index     283                 273
    # 6 pid             12880               12880
    # 7 tid             12894               12897
    # 8 grd             18688               1191168
    # 9 wgr             256                 256
    # 10 lds            0                   0
    # 11 scr            260                 240
    # 12 vgpr           64                  64
    # 13 sgpr           112                 80
    # 14 fbar           31680               200128
    # 15 sig            0x0                 0x0
    # 16 obj            0x149024670e00      0x149024671000
    # 17 FetchSize      36315               27649
    # 18 SQ_INSTS_VALU  23752915            21379598
    # 19 WriteSize      4900                4887
    # 20 SQ_INSTS_SALU  7940266             8113797
    # 21 DispatchNs     928849855178699     928849846016292
    # 22 BeginNs        928849857054103     928849846361163
    # 23 EndNs          928849858195060     928849848208519
    # 24 CompleteNs     928849858205531     928849848210456
    # }}}
    # Metric Name	Metric Unit
    # SQ_INSTS_SALU	inst
    # SQ_INSTS_VALU	inst
    # FetchSize	        bytes
    # WriteSize	        bytes
    # time	        us
    #
    def set_regex(self, name):
        if name == 'computem':
            regex = (
                r'^\d+,\"computeMomentumAndEnergyIAD\",(?:\d+,){12}'
                r'(?:\d+x\d+,\d+x\S+)'
                r'(?:e\d+)*,(?P<m1>\d+),(?P<m2>\d+),(?P<m3>\d+),(?P<m4>\d+)'
                r'(?:,\d+,)(?P<begin>\d+),(?P<end>\d+),'
            )
        elif name == 'findn':
            regex = (
                r'^\d+,\"findNeighborsKernel\",(?:\d+,){12}(?:\d+x\d+,\d+x\S+)'
                r'(?:e\d+)*,(?P<m1>\d+),(?P<m2>\d+),(?P<m3>\d+),(?P<m4>\d+)'
                r'(?:,\d+,)(?P<begin>\d+),(?P<end>\d+),'
            )
        elif name == 'iad':
            regex = (
                r'^\d+,\"computeIAD\",(?:\d+,){12}(?:\d+x\d+,\d+x\S+)'
                r'(?:e\d+)*,(?P<m1>\d+),(?P<m2>\d+),(?P<m3>\d+),(?P<m4>\d+)'
                r'(?:,\d+,)(?P<begin>\d+),(?P<end>\d+),'
            )
        elif name == 'density':
            regex = (
                r'^\d+,\"density\",(?:\d+,){12}(?:\d+x\d+,\d+x\S+)'
                r'(?:e\d+)*,(?P<m1>\d+),(?P<m2>\d+),(?P<m3>\d+),(?P<m4>\d+)'
                r'(?:,\d+,)(?P<begin>\d+),(?P<end>\d+),'
            )
        # FIXME: 0x14830e670e00 meaning ?
        else:
            regex = r''

        # print(regex)
        return regex
    # }}}

    # {{{ computeMomentumAndEnergyIAD_FetchSize: 43269.0 bytes
    # computeMomentumAndEnergyIAD_SQ_INSTS_VALU: 17155362.0 inst
    # computeMomentumAndEnergyIAD_WriteSize: 15724.0 bytes
    # computeMomentumAndEnergyIAD_SQ_INSTS_SALU: 7080943.0 inst
    # computeMomentumAndEnergyIAD_ns: 1133863.0 ns
    @performance_function('bytes')
    def computeMomentumAndEnergyIAD_FetchSize(self):
        regex = self.set_regex('computem')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm1', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm1', int)), 0)

    @performance_function('inst')
    def computeMomentumAndEnergyIAD_SQ_INSTS_VALU(self):
        regex = self.set_regex('computem')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm2', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm2', int)), 0)

    @performance_function('bytes')
    def computeMomentumAndEnergyIAD_WriteSize(self):
        regex = self.set_regex('computem')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm3', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm3', int)), 0)

    @performance_function('inst')
    def computeMomentumAndEnergyIAD_SQ_INSTS_SALU(self):
        regex = self.set_regex('computem')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm4', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm4', int)), 0)

    @performance_function('ns')
    def computeMomentumAndEnergyIAD_ns(self):
        regex = self.set_regex('computem')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        begin_ns = sn.extractall(regex, rpt, 'begin', int)
        end_ns = sn.extractall(regex, rpt, 'end', int)
        ns_list = [zz[1] - zz[0] for zz in zip(begin_ns, end_ns)]
        return sn.round(sn.avg(ns_list), 0)
    # }}}

    # {{{ findNeighborsKernel_FetchSize: 43269.0 bytes
    @performance_function('bytes')
    def findNeighborsKernel_FetchSize(self):
        regex = self.set_regex('findn')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm1', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm1', int)), 0)

    @performance_function('inst')
    def findNeighborsKernel_SQ_INSTS_VALU(self):
        regex = self.set_regex('findn')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm2', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm2', int)), 0)

    @performance_function('bytes')
    def findNeighborsKernel_WriteSize(self):
        regex = self.set_regex('findn')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm3', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm3', int)), 0)

    @performance_function('inst')
    def findNeighborsKernel_SQ_INSTS_SALU(self):
        regex = self.set_regex('findn')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm4', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm4', int)), 0)

    @performance_function('ns')
    def findNeighborsKernel_ns(self):
        regex = self.set_regex('findn')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        begin_ns = sn.extractall(regex, rpt, 'begin', int)
        end_ns = sn.extractall(regex, rpt, 'end', int)
        ns_list = [zz[1] - zz[0] for zz in zip(begin_ns, end_ns)]
        return sn.round(sn.avg(ns_list), 0)
    # }}}

    # {{{ computeIAD_FetchSize: 43269.0 bytes
    @performance_function('bytes')
    def computeIAD_FetchSize(self):
        regex = self.set_regex('iad')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm1', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm1', int)), 0)

    @performance_function('inst')
    def computeIAD_SQ_INSTS_VALU(self):
        regex = self.set_regex('iad')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm2', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm2', int)), 0)

    @performance_function('bytes')
    def computeIAD_WriteSize(self):
        regex = self.set_regex('iad')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm3', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm3', int)), 0)

    @performance_function('inst')
    def computeIAD_SQ_INSTS_SALU(self):
        regex = self.set_regex('iad')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm4', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm4', int)), 0)

    @performance_function('ns')
    def computeIAD_ns(self):
        regex = self.set_regex('iad')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        begin_ns = sn.extractall(regex, rpt, 'begin', int)
        end_ns = sn.extractall(regex, rpt, 'end', int)
        ns_list = [zz[1] - zz[0] for zz in zip(begin_ns, end_ns)]
        return sn.round(sn.avg(ns_list), 0)
    # }}}

    # {{{ density_FetchSize: 43269.0 bytes
    @performance_function('bytes')
    def density_FetchSize(self):
        regex = self.set_regex('density')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm1', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm1', int)), 0)

    @performance_function('inst')
    def density_SQ_INSTS_VALU(self):
        regex = self.set_regex('density')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm2', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm2', int)), 0)

    @performance_function('bytes')
    def density_WriteSize(self):
        regex = self.set_regex('density')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm3', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm3', int)), 0)

    @performance_function('inst')
    def density_SQ_INSTS_SALU(self):
        regex = self.set_regex('density')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        return sn.round(sn.max(sn.extractall(regex, rpt, 'm4', int)), 0)
        # return sn.round(sn.avg(sn.extractall(regex, rpt, 'm4', int)), 0)

    @performance_function('ns')
    def density_ns(self):
        regex = self.set_regex('density')
        rpt = os.path.join(self.stagedir,
                           self.metric_file.replace(".txt", ".csv"))
        begin_ns = sn.extractall(regex, rpt, 'begin', int)
        end_ns = sn.extractall(regex, rpt, 'end', int)
        ns_list = [zz[1] - zz[0] for zz in zip(begin_ns, end_ns)]
        return sn.round(sn.avg(ns_list), 0)
    # }}}
    # }}}
# }}}
