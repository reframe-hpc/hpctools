import os
import reframe as rfm
import reframe.utility.sanity as sn
# import reframe.core.launchers as launchers
import sphexa.sanity as sphs


class setup_pe(rfm.RegressionMixin):
    # {{{ set_src
    @rfm.run_before('compile')
    def set_src(self):
        # self.sourcesdir = None
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'SPH-EXA_mini-app.git')
        src_files_list = [
            'bigfiles',
            'CMakeLists.txt',
            'docs',
            'domain',
            # 'include',
            'LICENSE',
            'Makefile',
            'mk.sh',
            'parse_dat_file.py',
            'plot.py',
            'README-DAINT.txt',
            'README.hdf5',
            'README.md',
            'rn.sh',
            'scripts',
            # 'src',
            'test',
            'tools'
        ]
        self.readonly_files = src_files_list
        src_files_remove = src_files_list.copy()
        src_files_remove.remove('Makefile')
        src_files_remove.remove('domain')
        # src_files_remove.remove('include')
        # src_files_remove.remove('src')
        sed_ifdef = (r'"s-#include \"cuda/sph.cuh\"-#ifdef USE_CUDA\n'
                     r'#include \"cuda/sph.cuh\"\n#endif-"')
        self.prebuild_cmds += [
            'module rm xalt',
            'module list',
            'rm -fr .git*',
            f'rm -f {" ".join(src_files_remove)}',
            '#',
            f'sed -i {sed_ifdef} include/sph/findNeighbors.hpp',
            f'sed -i {sed_ifdef} include/sph/density.hpp',
            f'sed -i {sed_ifdef} include/sph/IAD.hpp',
            f'sed -i {sed_ifdef} include/sph/momentumAndEnergyIAD.hpp',
        ]
    # }}}

    # {{{ set_prgenv_flags
    # @rfm.run_after('setup')
    @rfm.run_before('compile')
    def set_prgenv_flags(self):
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++17', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG', '-fopenmp'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++17', '-g', '-O3',
                             '-DUSE_MPI', '-DNDEBUG', '-qopenmp'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-Ofast',
                            '-DUSE_MPI', '-DNDEBUG', '-fopenmp'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++17', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG', '-mp'],
            'PrgEnv-aocc': ['-I.', '-I./include', '-std=c++17', '-g', '-O3',
                            '-DUSE_MPI', '-DNDEBUG', '-fopenmp'],
        }
        self.prgenv_flags['cpeGNU'] = self.prgenv_flags['PrgEnv-gnu']
        self.prgenv_flags['cpeIntel'] = self.prgenv_flags['PrgEnv-intel']
        self.prgenv_flags['cpeAMD'] = self.prgenv_flags['PrgEnv-aocc']
        self.prgenv_flags['cpeCray'] = self.prgenv_flags['PrgEnv-cray']
        # {{{ scorep/scalasca
        if hasattr(self, 'scorep_flags') and self.scorep_flags:
            mpicxx = ('scorep --mpp=mpi --nocompiler CC '
                      '-I$CRAY_MPICH_DIR/include')
        else:
            mpicxx = 'CC'
        # }}}

        # {{{ debug
        if hasattr(self, 'debug_flags') and self.debug_flags:
            for kk in self.prgenv_flags.keys():
                tmp_l = [ww.replace("O3", "O0")
                         for ww in self.prgenv_flags[kk]]
                tmp_l = [ww.replace("fast", "O0") for ww in tmp_l]
                self.prgenv_flags[kk] = tmp_l.copy()
        # }}}

        # {{{ gperftools
        if hasattr(self, 'gperftools_flags') and self.gperftools_flags:
            self.build_system.cxxflags += ['`pkg-config --libs libprofiler`']
        # }}}

        # {{{ mpip
        if hasattr(self, 'mpip_flags') and self.mpip_flags:
            self.build_system.cxxflags += \
                ['-L$EBROOTMPIP/lib', '-Wl,--whole-archive -lmpiP',
                 '-Wl,--no-whole-archive -lunwind', '-lbfd -liberty -ldl -lz']
        # }}}

        self.build_system.cxxflags += \
            self.prgenv_flags[self.current_environ.name]
        # If self.executable is not set, ReFrame will set it to self.name:
        # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html
        if self.executable[2:] == self.name:
            self.executable = 'mpi+omp'

        if not hasattr(self, 'target_executable'):
            self.target_executable = 'mpi+omp'

        self.build_system.options = [
            self.target_executable, f'MPICXX="{mpicxx}"',
            'SRCDIR=.', 'BUILDDIR=.', 'BINDIR=.',
            # NOTE: self.build_system.cxx is empty
        ]
        self.postbuild_cmds += [
            f'mv {self.target_executable}.app {self.target_executable}'
        ]
    # }}}

    # {{{ set_system_attributes
    # @rfm.run_before('run')
    @rfm.run_after('compile')
    def set_system_attributes(self):
        cs = self.current_system.name  # cs=dom
        cpf = self.current_partition.fullname  # cpf=dom:gpu
        cp = self.current_partition
        if cp.processor.arch is None:
            processor = {
                'eiger:mc': {
                    'arch': 'zen2', 'num_cpus': 256, 'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 128, 'num_sockets': 2,
                    'num_cores': 128, 'num_cores_per_socket': 64,
                    'num_numa_nodes': 8, 'num_cores_per_numa_node': 16,
                },
                'daint:mc': {
                    'arch': 'broadwell', 'num_cpus': 72,
                    'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 36, 'num_sockets': 2,
                    'num_cores': 36, 'num_cores_per_socket': 18,
                    'num_numa_nodes': 2, 'num_cores_per_numa_node': 18,
                },
                'daint:gpu': {
                    'arch': 'haswell', 'num_cpus': 24, 'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 24, 'num_sockets': 1,
                    'num_cores': 12, 'num_cores_per_socket': 12,
                    'num_numa_nodes': 1, 'num_cores_per_numa_node': 12,
                },
            }
            processor['pilatus:mc'] = processor['eiger:mc'].copy()
            processor['dom:mc'] = processor['daint:mc'].copy()
            processor['dom:gpu'] = processor['daint:gpu'].copy()
            #
            self.arch = processor[cpf]['arch']
            self.num_cpus = processor[cpf]['num_cpus']
            self.num_cpus_per_core = processor[cpf]['num_cpus_per_core']
            self.num_cpus_per_socket = processor[cpf]['num_cpus_per_socket']
            self.num_sockets = processor[cpf]['num_sockets']
            self.num_cores = processor[cpf]['num_cores']
            self.num_cores_per_socket = processor[cpf]['num_cores_per_socket']
            self.num_numa_nodes = processor[cpf]['num_numa_nodes']
            self.num_cores_per_numa_node = \
                processor[cpf]['num_cores_per_numa_node']
        else:
            self.arch = cp.processor.arch
            self.num_cpus = cp.processor.num_cpus
            self.num_cpus_per_core = cp.processor.num_cpus_per_core
            self.num_cpus_per_socket = cp.processor.num_cpus_per_socket
            self.num_sockets = cp.processor.num_sockets
            self.num_cores = cp.processor.num_cores
            self.num_cores_per_socket = cp.processor.num_cores_per_socket
            # self.num_numa_nodes = cp.processor.num_numa_nodes
            # self.num_cores_per_numa_node = \
            #    cp.processor.num_cores_per_numa_node

        self.num_tasks = self.compute_node * self.num_sockets
        self.num_tasks_per_node = self.num_cores // self.num_cores_per_socket
# {{{
#         if cs in {'pilatus', 'eiger'}:
#             # {{{ arch=zen2 # 'AMD EPYC 7742 64-Core Processor'
#             # num_cpus=256
#             # num_cpus_per_core=2
#             # num_cpus_per_socket=128
#             # num_sockets=2
#             # +num_cores=128
#             # +num_cores_per_socket=64
#             # +num_numa_nodes=None
#             # +num_cores_per_numa_node=None }}}
# #             self.arch = 'zen2'
# #             self.num_cpus = 256
# #             self.num_cpus_per_core = 2
# #             self.num_cpus_per_socket = 128
# #             self.num_sockets = 2
#             #
#             self.num_numa_nodes = 8
#             self.num_cores_per_numa_node = 16
#         elif cp in {'dom:mc', 'daint:mc'}:
#             # {{{ arch=broadwell # 'Intel(R) Xeon(R) CPU E5-2695 v4'
#             # num_cpus=72
#             # num_cpus_per_core=2
#             # num_cpus_per_socket=36
#             # num_sockets=2
#             # +num_cores=
#             # +num_cores_per_socket=
#             # +num_numa_nodes=None
#             # +num_cores_per_numa_node=None }}}
# #             self.arch = 'broadwell'
# #             self.num_cpus = 72
# #             self.num_cpus_per_core = 2
# #             self.num_cpus_per_socket = 36
# #             self.num_sockets = 2
#             #
#             self.num_numa_nodes = 2
#             self.num_cores_per_numa_node = 18
#         elif cp in {'dom:gpu', 'daint:gpu'}:
#             # {{{ arch=haswell # 'Intel(R) Xeon(R) CPU E5-2690 v3'
#             # num_cpus=24
#             # num_cpus_per_core=2
#             # num_cpus_per_socket=24
#             # num_sockets=1
#             # +num_cores=
#             # +num_cores_per_socket=
#             # +num_numa_nodes=None
#             # +num_cores_per_numa_node=None }}}
# #             self.arch = 'haswell'
# #             self.num_cpus = 24
# #             self.num_cpus_per_core = 2
# #             self.num_cpus_per_socket = 24
# #             self.num_sockets = 1
#             #
#             self.num_numa_nodes = 1
#             self.num_cores_per_numa_node = 12
# }}}

        self.num_tasks_per_core = 1
        self.omp_threads = self.num_cores // self.num_tasks_per_node
        # self.num_cpus_per_task = self.num_cores // self.num_tasks_per_node
        # self.use_multithreading = False
        self.exclusive = True
        if not hasattr(self, 'variables'):
            self.variables += {
                'CRAYPE_LINK_TYPE': 'dynamic',
                'OMP_NUM_THREADS': str(self.omp_threads),
                # 'OMP_NUM_THREADS': str(self.num_cpus_per_task),
                #   'OMP_DISPLAY_AFFINITY': 'TRUE',
                #   'OMP_PROC_BIND': 'spread',
            }
        else:
            self.variables['CRAYPE_LINK_TYPE'] = 'dynamic'
            self.variables['OMP_NUM_THREADS'] = str(self.omp_threads)
            # self.variables['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)
            # 'echo "# JOBID=$SLURM_JOBID"',

    @rfm.run_after('compile')
    # @rfm.run_before('run')
    def set_cpu_binding(self):
        self.job.launcher.options = ['--cpu-bind=verbose']
    # }}}


class setup_code(rfm.RegressionMixin):
    # {{{ set_cubeside
    # @rfm.run_after('setup')
    @rfm.run_before('run')
    def set_cubeside(self):
        self.modules += ['hwloc']
        total_np = (self.compute_node * self.num_tasks_per_node *
                    self.omp_threads * self.np_per_c)
        # TODO: larger
        # total_np = (self.num_tasks_per_node * self.num_cpus_per_task *
        #             self.compute_node * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        self.executable_opts += [f"-n {self.cubeside}", f"-s {self.steps}"]
        self.prerun_cmds += [
            'module rm xalt', 'module list',
            'echo "# JOBID=$SLURM_JOBID"',
            'srun --version',
        ]
        # TODO: if srun: r'srun --version'  # (slurm 20.11.4)
        self.affinity_rpt = 'affinity.rpt'
        self.postrun_cmds += [
            f'# exes:|{self.executable}|{self.target_executable}|',
            # TODO: do this in python
            f'grep ^cpu-bind= {self.stderr} |'
            'awk \'{print $5,$9}\' |sort -nk1 |'
            'awk \'{print "echo "$2" |hwloc-calc -H core |grep Core: |'
            'sed \'s-Core:--g\'"}\' |sh '
            f'&> {self.affinity_rpt}',
            f'cat {self.affinity_rpt}'
        ]
    # }}}

    # {{{ set_timers
    @rfm.run_before('run')
    def set_timers(self):
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
    # }}}

    # {{{ set_perf_patterns:
    @rfm.run_after('sanity')
    def set_perf_patterns(self):
        # if not skip_perf_report:
        self.perf_patterns = {
            'Elapsed': sphs.seconds_elaps(self),
            '_Elapsed': sphs.elapsed_time_from_date(self),
            #
            'domain_sync': sphs.seconds_timers(self, 1),
            'updateTasks': sphs.seconds_timers(self, 2),
            'FindNeighbors': sphs.seconds_timers(self, 3),
            'Density': sphs.seconds_timers(self, 4),
            'EquationOfState': sphs.seconds_timers(self, 5),
            'mpi_synchronizeHalos': sphs.seconds_timers(self, 6),
            'IAD': sphs.seconds_timers(self, 7),
            'MomentumEnergyIAD': sphs.seconds_timers(self, 8),
            'Timestep': sphs.seconds_timers(self, 9),
            'UpdateQuantities': sphs.seconds_timers(self, 10),
            'EnergyConservation': sphs.seconds_timers(self, 11),
            'UpdateSmoothingLength': sphs.seconds_timers(self, 12),
            # 'domain_distribute'
            # 'BuildTree'
        }
        # top%
        self.perf_patterns.update({
            '%MomentumEnergyIAD':    sphs.pctg_MomentumEnergyIAD(self),
            '%mpi_synchronizeHalos': sphs.pctg_mpi_synchronizeHalos(self),
            '%FindNeighbors':        sphs.pctg_FindNeighbors(self),
            '%IAD':                  sphs.pctg_IAD(self),
        })

    # }}}

    # {{{ set_reference:
    @rfm.run_after('sanity')
    def set_reference(self):
        # if not skip_perf_report:
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        self.reference = {
            '*': {
                'Elapsed': (0, None, None, 's'),
                '_Elapsed': (0, None, None, 's'),
                # timers
                'domain_sync': myzero_s,
                'updateTasks': myzero_s,
                'FindNeighbors': myzero_s,
                'Density': myzero_s,
                'EquationOfState': myzero_s,
                'mpi_synchronizeHalos': myzero_s,
                'IAD': myzero_s,
                'MomentumEnergyIAD': myzero_s,
                'Timestep': myzero_s,
                'UpdateQuantities': myzero_s,
                'EnergyConservation': myzero_s,
                'UpdateSmoothingLength': myzero_s,
                # top%
                '%MomentumEnergyIAD': myzero_p,
                '%mpi_synchronizeHalos': myzero_p,
                '%FindNeighbors': myzero_p,
                '%IAD': myzero_p,
            }
        }
    # }}}
