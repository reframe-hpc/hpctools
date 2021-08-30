import hostlist
import os
import reframe as rfm
import reframe.utility.sanity as sn
# import reframe.core.launchers as launchers
import sphexa.sanity as sphs


class setup_pe(rfm.RegressionMixin):
    # {{{ set_src
    @run_before('compile')
    def set_src(self):
        # self.sourcesdir = None
        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'SPH-EXA_mini-app.git')
        src_files_list = [
            # comment out for copying the dir instead of symlinks
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
            # src is always copied by reframe
            'test',
            'tools'
        ]
        self.readonly_files = src_files_list
        src_files_remove = src_files_list.copy()
        # use symlinks instead of copy:
        src_files_remove.remove('Makefile')
        src_files_remove.remove('domain')
        # src_files_remove.remove('include')
        # src_files_remove.remove('src')
        # sed_ifdef = (r'"s-#include \"cuda/sph.cuh\"-#ifdef USE_CUDA\n'
        #              r'#include \"cuda/sph.cuh\"\n#endif-"')
        if self.current_environ.name not in ['PrgEnv-nvidia', 'PrgEnv-pgi']:
            self.prebuild_cmds += [
                'module load cray-mpich',
                'module load cray-libsci',
            ]

        self.prebuild_cmds += [
            'module rm xalt',
            'module list',
            'rm -fr .git*',
            f'rm -f {" ".join(src_files_remove)}',
            '#',
            # f'sed -i {sed_ifdef} include/sph/findNeighbors.hpp',
            # f'sed -i {sed_ifdef} include/sph/density.hpp',
            # f'sed -i {sed_ifdef} include/sph/IAD.hpp',
            # f'sed -i {sed_ifdef} include/sph/momentumAndEnergyIAD.hpp',
        ]
    # }}}

    # {{{ get_gpu_specs
    @run_before('compile')
    def get_gpu_specs(self):
        self.gpu_specs = {
            'P100': {
                'capability': 'sm_60', 'sms': 'SMS=60',
                'multiprocessors': 56,
                'maximum_number_of_threads_per_multiprocessor': 2048,
                'maximum_number_of_threads_per_block': 1024,
                'warp_size': 32,
            },
            'V100': {
                'capability': 'sm_70', 'sms': 'SMS=70',
                'multiprocessors': 80,
                'maximum_number_of_threads_per_multiprocessor': 2048,
                'maximum_number_of_threads_per_block': 1024,
                'warp_size': 32,
            },
            'nogpu': {
                'sms': '',
            },
        }
    # }}}

    # {{{ set_prgenv_flags
    @run_before('compile')
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
            'PrgEnv-nvidia': ['-I.', '-I./include', '-std=c++17', '-g', '-O3',
                              '-DUSE_MPI', '-DNDEBUG', '-mp', '-w',
                              '-DUSE_GCC_ATOMICS',
                              '-D__GCC_ATOMIC_TEST_AND_SET_TRUEVAL=1'],  # -w
            'PrgEnv-aocc': ['-I.', '-I./include', '-std=c++17', '-g', '-O3',
                            '-DUSE_MPI', '-DNDEBUG', '-fopenmp'],
        }
        self.prgenv_flags['cpeGNU'] = self.prgenv_flags['PrgEnv-gnu']
        self.prgenv_flags['cpeIntel'] = self.prgenv_flags['PrgEnv-intel']
        self.prgenv_flags['cpeAMD'] = self.prgenv_flags['PrgEnv-aocc']
        self.prgenv_flags['cpeCray'] = self.prgenv_flags['PrgEnv-cray']
        mpicxx = self._current_environ.cxx
        # {{{ scorep/scalasca
        if hasattr(self, 'scorep_flags') and self.scorep_flags:
            # mpicxx = ('scorep --mpp=mpi --nocompiler '
            # --nocompiler: reduces overhead
            mpicxx = ('scorep --mpp=mpi --user --nocompiler '
                      f'{self._current_environ.cxx} '
                      '-I$CRAY_MPICH_DIR/include')
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
        # {{{ semiprof
        if hasattr(self, 'semiprof_flags') and self.semiprof_flags:
            self.build_system.cxxflags += [
                f'-DSEMIPROF -I$EBROOTSEMIPROF/include"',
                # trick to set ldflags:
                f'LIB="-L$EBROOTSEMIPROF/lib64 -lsemiprof']
            # TODO: pkg-config
            # self.build_system.cxxflags += ['`pkg-config --libs libprofiler`']
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

        # {{{ gpu_compute_capability
        self.gpu_compute_capability = {
            'dom:gpu': 'SMS=60',  # P100
            'dom:mc': 'SMS=',
            'daint:gpu': 'SMS=60',  # P100
            'daint:mc': 'SMS=',
            'eiger:mc': 'SMS=',
            'pilatus:mc': 'SMS=',
            'puthi:mc': 'SMS=',
            'archer2:compute': 'SMS=',
        }
        partname = self.current_partition.fullname
        gpu_compute_capability = self.gpu_compute_capability[partname]
        # }}}
        if mpicxx:
            self.build_system.options = [
                self.target_executable, f'MPICXX="{mpicxx}"',
                'SRCDIR=.', 'BUILDDIR=.', 'BINDIR=.',
                "NVCCFLAGS='-std=c++17 $(GENCODE_FLAGS) -O2'",
                # "NVCCFLAGS='-std=c++17 $(GENCODE_FLAGS) -g'",
                gpu_compute_capability,
                # NOTE: self.build_system.cxx is empty
            ]
        else:
            self.build_system.options = [
                self.target_executable,
                'SRCDIR=.', 'BUILDDIR=.', 'BINDIR=.',
                "NVCCFLAGS='-std=c++17 $(GENCODE_FLAGS) -g'",
                gpu_compute_capability,
            ]
            # NOTE: why:
            # --expt-relaxed-constexpr -rdc=true -Wno-deprecated-gpu-targets

        self.postbuild_cmds += [
            f'mv {self.target_executable}.app {self.target_executable}'
        ]
    # }}}

    # {{{ set_system_attributes
    # @rfm.run_before('run')
    @run_after('compile')
    def set_system_attributes(self):
        cs = self.current_system.name  # cs=dom
        cpf = self.current_partition.fullname  # cpf=dom:gpu
        cp = self.current_partition
        if cp.processor.arch is None:
            processor = {
                'puthi:mc': {
                    # cascadelake
                    'arch': 'Gold6230', 'num_cpus': 40, 'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 20, 'num_sockets': 2,
                    'num_cores': 20, 'num_cores_per_socket': 10,
                    'num_numa_nodes': 2, 'num_cores_per_numa_node': 10,
                    'gpu': 'nogpu',
                },
                'archer2:compute': {
                    'arch': 'zen2', 'num_cpus': 256, 'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 128, 'num_sockets': 2,
                    'num_cores': 128, 'num_cores_per_socket': 64,
                    'num_numa_nodes': 8, 'num_cores_per_numa_node': 16,
                    'gpu': 'nogpu',
                },
                'eiger:mc': {
                    'arch': 'zen2', 'num_cpus': 256, 'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 128, 'num_sockets': 2,
                    'num_cores': 128, 'num_cores_per_socket': 64,
                    'num_numa_nodes': 8, 'num_cores_per_numa_node': 16,
                    'gpu': 'nogpu',
                },
                'daint:mc': {
                    'arch': 'broadwell', 'num_cpus': 72,
                    'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 36, 'num_sockets': 2,
                    'num_cores': 36, 'num_cores_per_socket': 18,
                    'num_numa_nodes': 2, 'num_cores_per_numa_node': 18,
                    'gpu': 'nogpu',
                },
                'daint:gpu': {
                    'arch': 'haswell', 'num_cpus': 24, 'num_cpus_per_core': 2,
                    'num_cpus_per_socket': 24, 'num_sockets': 1,
                    'num_cores': 12, 'num_cores_per_socket': 12,
                    'num_numa_nodes': 1, 'num_cores_per_numa_node': 12,
                    'gpu': 'P100',
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
                # 'OMP_PROC_BIND': 'spread',
            }
        else:
            self.variables['CRAYPE_LINK_TYPE'] = 'dynamic'
            self.variables['OMP_NUM_THREADS'] = str(self.omp_threads)
            # self.variables['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)

        if self.num_tasks <= 2:
            # Imitating slurm '--cpu-bind=verbose' with OMP_AFFINITY_FORMAT:
            # "cpu-bind=MASK - r01c01, task  1  1 [66597]: mask 0x2 set"
            omp_affinity_format = (
                # [%P] fails with some compilers -> removing it
                # https://www.openmp.org/spec-html/5.0/openmpse62.html
                r'"omp-bind=MASK - %H, task %n %n [xxx]: mask xxx set '
                r'thread_affinity=%A %Nthds %a"'
            )
            self.variables['OMP_AFFINITY_FORMAT'] = omp_affinity_format
            self.variables['OMP_DISPLAY_AFFINITY'] = 'true'
            # {{{ NOTE: Associating the OMP_AFFINITY_FORMAT hexadecimal with
            # affinity is wrong:
            #  it is the thread ID in the system so the handle that Linux gives
            #  to the OpenMP runtime as the thread ID for the POSIX thread that
            #  is registered in the kernel
            #
            # https://www.openmp.org/spec-html/5.0/openmpse62.html
            # t   team_num    The value returned by omp_get_team_num().
            # T   num_teams   The value returned by omp_get_num_teams().
            # L   nesting_level   The value returned by omp_get_level().
            # n*  thread_num  The value returned by omp_get_thread_num().
            # N*  num_threads The value returned by omp_get_num_threads().
            # a   ancestor_tnum   The value returned by
            #       omp_get_ancestor_thread_num(level),
            #       where level is omp_get_level() minus 1.
            # H*  host
            #     The name for the host machine on which the OpenMP
            #     program is running.
            # P*  process_id
            #     The process identifier used by the implementation.
            # i*  native_thread_id
            #     The native thread identifier used by the implementation.
            # A*  thread_affinity The list of numerical identifiers on which a
            #     thread may execute
            #
            # https://docs.nersc.gov/jobs/affinity/
            # self.variables['KMP_AFFINITY'] = 'verbose'  # intel
            # self.variables['CRAY_OMP_CHECK_AFFINITY'] = 'TRUE'  # cce
            # cpu-bind=MASK - r01c01, task  1  1 [66597]: mask 0x2 set
            # }}}
            self.affinity_rpt = 'affinity.rpt'
            self.postrun_cmds += [
                f'# exes:|{self.executable}|{self.target_executable}|',
                '# --- report affinity from OMP_DISPLAY_AFFINITY:',
                # f'grep "task 0 0" {self.stdout} &> {self.affinity_rpt}',
                # rpt file is needed because stderr is a _DeferredExpression:
                f'grep --no-filename bind=MASK {self.stdout} {self.stderr} '
                f'&> {self.affinity_rpt}',
                # TODO: do this in python (using bits_from_string - slurm only)
                # --- also possible with hwloc-calc (module required):
                # f'grep ^cpu-bind= {self.stderr} |'
                # 'awk \'{print $5,$9}\' |sort -nk1 |'
                # 'awk \'{print "echo "$2" |hwloc-calc -H core |grep Core: |'
                # 'sed \'s-Core:--g\'"}\' |sh '
                # f'&> {self.affinity_rpt}',
                # f'cat {self.affinity_rpt}'
            ]

    @run_after('compile')
    def set_cpu_binding(self):
        # cpu-bind=MASK - r01c01, task  1  1 [66597]: mask 0x2 set
        self.job.launcher.options = ['--cpu-bind=verbose']
    # }}}

    # {{{ bits_from_string_hpctools: (affinity_hostlist)
    @deferrable
    def bits_from_string_hpctools(self, mask):
        ret = []
        mask_int = int(mask, 0)
        index = 0
        while mask_int:
            if mask_int & 1:
                # ret.append(index)
                ret.append(str(index))

            index += 1
            mask_int >>= 1

        # return ret
        return hostlist.collect_hostlist(ret)
    # }}}

    # {{{ sanity_function: affinity_hostlist
    @run_before('performance')
    def affinity_hostlist(self):
        '''Reports affinity as a hostlist

        .. code-block::

          * slurm_mask_rk: 0 [0-63,128-191] (rank 0)
          * openmp_mask_rk: -1 ['64-127,192-255', '0-63,128-191'] (all ranks)
        '''
        if (
            self.current_partition.launcher_type.registered_name == "srun"
            and not hasattr(self, "debug_flags")
            and self.num_tasks <= 2
        ):
            rptf = os.path.join(self.stagedir, self.affinity_rpt)
            # --- slurm output:
            # cpu-bind=MASK - nid001194, task  0  0 [221956]: mask 0xf set
            regex_slurm = r'^cpu-bind=MASK.*task\s+0\s+0.*mask (?P<aff>\S+) se'
            self.slm_hexmask = sn.extractsingle(
                regex_slurm, rptf, 'aff',
                conv=lambda x: self.bits_from_string_hpctools(x)
            )
            # --- openmp output:
            # omp-bind=MASK - nid001194, task 0 0 [221957]: mask xxx set ...
            # ... thread_affinity=64-127,192-255 18thds 0
            regex_omp = (r'^omp-bind=MASK.*task\s+0\s+0.*'
                         r'thread_affinity=(?P<aff>\S+| \d+-\d+ \d+-\d+) ')
            self.omp_hexmask = sn.extractall(regex_omp, rptf, 'aff')
            #                            ^^^
        else:
            self.slm_hexmask = ''
            self.omp_hexmask = ''

    # }}}


class setup_code(rfm.RegressionMixin):
    # {{{ set_cubeside
    # @run_after('setup')
    @run_before('run')
    def set_cubeside(self):
        # self.modules += ['hwloc']
        # weak scaling:
        total_np = (self.compute_node * self.num_tasks_per_node *
                    self.omp_threads * self.np_per_c)
        # strong scaling:
        # total_np = (1 * self.num_tasks_per_node *
        #             self.omp_threads * self.np_per_c)
        # = 2 * 64 * 1e4
        # SphExa_Timers_Check_100_8_10000_0 nLocalParticles 118800
        # SphExa_Timers_Check_100_4_10000_0 nLocalParticles 216000
        # SphExa_Timers_Check_100_2_10000_0 nLocalParticles 388800
        # SphExa_Timers_Check_100_1_10000_0 nLocalParticles 699840
        # TODO: larger
        # total_np = (self.num_tasks_per_node * self.num_cpus_per_task *
        #             self.compute_node * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        self.executable_opts += [f"-n {self.cubeside}", f"-s {self.steps}"]
        if self.current_environ.name not in ['PrgEnv-nvidia', 'PrgEnv-pgi']:
            self.prerun_cmds += [
                'module load cray-mpich',
                'module load cray-libsci',
            ]

        self.prerun_cmds += [
            f'ldd {self.target_executable}',
            # ---------------------------
            'module rm xalt', 'module list',
            'echo "# JOBID=$SLURM_JOBID"',
            'srun --version',
        ]
    # }}}

    # {{{ set_timers
    @run_before('run')
    def set_timers(self):
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
    # }}}

    # {{{ set_perf_patterns:
    @run_before('performance')
    def set_perf_patterns(self):
        perf_patterns = {
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
        # if not skip_perf_report:
        if self.perf_patterns:
            self.perf_patterns.update(perf_patterns)
        else:
            self.perf_patterns = perf_patterns

        # top%
        self.perf_patterns.update({
            '%MomentumEnergyIAD':    sphs.pctg_MomentumEnergyIAD(self),
            '%mpi_synchronizeHalos': sphs.pctg_mpi_synchronizeHalos(self),
            '%FindNeighbors':        sphs.pctg_FindNeighbors(self),
            '%IAD':                  sphs.pctg_IAD(self),
        })
        if self.num_tasks <= 2 and \
           self.current_partition.launcher_type.registered_name == 'srun':
            self.perf_patterns.update({
                'slurm_mask_rk': sn.extractsingle_s(r'\d', '0', conv=int),  # 0
                'openmp_mask_rk': sn.extractsingle_s(r'\S+', '-1', conv=int),
            })

    # }}}

    # {{{ set_reference:
    @run_before('performance')
    def set_reference(self):
        # if not skip_perf_report:
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        # elapsed
        self.reference['*:Elapsed'] = myzero_s
        self.reference['*:_Elapsed'] = myzero_s
        # timers
        self.reference['*:domain_sync'] = myzero_s
        self.reference['*:updateTasks'] = myzero_s
        self.reference['*:FindNeighbors'] = myzero_s
        self.reference['*:Density'] = myzero_s
        self.reference['*:EquationOfState'] = myzero_s
        self.reference['*:mpi_synchronizeHalos'] = myzero_s
        self.reference['*:IAD'] = myzero_s
        self.reference['*:MomentumEnergyIAD'] = myzero_s
        self.reference['*:Timestep'] = myzero_s
        self.reference['*:UpdateQuantities'] = myzero_s
        self.reference['*:EnergyConservation'] = myzero_s
        self.reference['*:UpdateSmoothingLength'] = myzero_s
        # top%
        self.reference['*:%MomentumEnergyIAD'] = myzero_p
        self.reference['*:%mpi_synchronizeHalos'] = myzero_p
        self.reference['*:%FindNeighbors'] = myzero_p
        self.reference['*:%IAD'] = myzero_p
        # needed only when self.perf_patterns is set ("if" not needed here)
        self.reference['*:slurm_mask_rk'] = (0, None, None, self.slm_hexmask)
        self.reference['*:openmp_mask_rk'] = (
            # use "set" to get a unique list
            0, None, None, list(set(self.omp_hexmask))
        )

    # }}}
