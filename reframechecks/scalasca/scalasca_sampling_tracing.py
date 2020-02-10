import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.sanity as sphs
import sphexa.sanity_scorep as sphsscorep
import sphexa.sanity_scalasca as sphssca
from reframe.core.launchers import LauncherWrapper


@rfm.parameterized_test(*[[mpitask, steps, cycles]
                          for mpitask in [24]
                          for steps in [4]
                          for cycles in [5000000]
                          ])
class SphExaNativeCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Scalasca (mpi only):

    3 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.
    :arg cycles: sampling sources generate interrupts that trigger a sample.
         SCOREP_SAMPLING_EVENTS sets the sampling source:
         see $EBROOTSCOREMINP/share/doc/scorep/html/sampling.html .
         Very large values will produce unreliable performance report,
         very small values will have a large runtime overhead.

    Typical performance reporting:

    .. literalinclude::
      ../../reframechecks/scalasca/res/scalasca_sampling_tracing.res
      :lines: 1-31
      :emphasize-lines: 26
    '''
    # }}}

    def __init__(self, mpitask, steps, cycles):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel',
                                    'PrgEnv-cray', 'PrgEnv-cray_classic',
                                    'PrgEnv-pgi']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
        self.prebuild_cmd = ['module rm xalt']
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-Ofast',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray_classic': ['-I.', '-I./include', '-hstd=c++14', '-g',
                                    '-O3', '-hnoomp', '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        # ---------------------------------------------------------------- tool
        tool_ver = '2.5'
        tc_ver = '19.10'
        self.tool_modules = {
            'PrgEnv-gnu': ['Scalasca/%s-CrayGNU-%s' % (tool_ver, tc_ver)],
            'PrgEnv-intel': ['Scalasca/%s-CrayIntel-%s' % (tool_ver, tc_ver)],
            'PrgEnv-cray': ['Scalasca/%s-CrayCCE-%s' % (tool_ver, tc_ver)],
            'PrgEnv-cray_classic': ['Scalasca/%s-CrayCCE-%s-classic' %
                                    (tool_ver, tc_ver)],
            'PrgEnv-pgi': ['Scalasca/%s-CrayPGI-%s' % (tool_ver, tc_ver)]
        }
        # ---------------------------------------------------------------- tool
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'scorep --mpp=mpi --nocompiler CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.executable = '%s.exe' % self.testname
# {{{ openmp:
# 'PrgEnv-intel': ['-qopenmp'],
# 'PrgEnv-gnu': ['-fopenmp'],
# 'PrgEnv-pgi': ['-mp'],
# 'PrgEnv-cray_classic': ['-homp'],
# 'PrgEnv-cray': ['-fopenmp'],
# # '-homp' if lang == 'F90' else '-fopenmp',
# }}}
# }}}

# {{{ run
        ompthread = 1
        # This dictionary sets cubesize = f(mpitask), for instance:
        # if mpitask == 24:
        #     cubesize = 100
        size_dict = {24: 100, 48: 125, 96: 157, 192: 198, 384: 250, 480: 269,
                     960: 340, 1920: 428, 3840: 539, 7680: 680, 15360: 857,
                     6: 30,
                     }
        cubesize = size_dict[mpitask]
        self.name = \
            'sphexa_scalascaS+T_{}_{:03d}mpi_{:03d}omp_{}n_{}steps_{}cycles'. \
            format(self.testname, mpitask, ompthread, cubesize, steps, cycles)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 24  # 72
# {{{ ht:
        # self.num_tasks_per_node = mpitask if mpitask < 36 else 36   # noht
        # self.use_multithreading = False  # noht
        # self.num_tasks_per_core = 1      # noht

        # self.num_tasks_per_node = mpitask if mpitask < 72 else 72
        # self.use_multithreading = True # ht
        # self.num_tasks_per_core = 2    # ht
# }}}
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 2
        self.use_multithreading = True
        self.exclusive = True
        self.time_limit = (0, 10, 0)
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'SCOREP_ENABLE_PROFILING': 'false',
            'SCOREP_ENABLE_TRACING': 'true',
            'SCOREP_ENABLE_UNWINDING': 'true',
            'SCOREP_SAMPLING_EVENTS': 'perf_cycles@%s' % cycles,
            # 'SCOREP_SAMPLING_EVENTS': 'PAPI_TOT_CYC@1000000',
            # 'SCOREP_SAMPLING_EVENTS': 'PAPI_TOT_CYC@%s' % cycles,
            # export SCOREP_SAMPLING_EVENTS=PAPI_TOT_CYC@1000000
            # empty SCOREP_SAMPLING_EVENTS will profile mpi calls only:
            # ok: 'SCOREP_SAMPLING_EVENTS': '',
            # 'SCOREP_METRIC_PAPI': 'PAPI_TOT_INS,PAPI_TOT_CYC',
            # 'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
            # 'SCOREP_TIMER': 'clock_gettime',
            # 'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '1',
            # 'SCOREP_VERBOSE': 'true',
            # To avoid "No free memory page available":
            'SCOREP_TOTAL_MEMORY': '1G',
            # Advanced performance metrics:
            'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
            'SCOREP_METRIC_PAPI': 'PAPI_TOT_INS,PAPI_TOT_CYC',
        }
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'info.rpt'
        self.rpt = 'rpt'
        # must use scorep.score:
        self.score_rpt = '%s.postproc' % self.rpt
        self.stat_rpt = 'scorep_%s_%s_trace/trace.stat' % \
                        (self.testname, self.num_tasks)
        # self.rpt_inclusive = '%s.inclusive' % self.rpt
        # self.rpt_exclusive = '%s.exclusive' % self.rpt
        self.tool = 'scalasca'
        # self.cubetool = 'cube_calltree'
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps]
        self.pre_run = [
            'module rm xalt',
            '%s -V &> %s' % (self.tool, self.version_rpt),
            'scorep --version >> %s' % self.version_rpt,
            'which %s &> %s' % (self.tool, self.which_rpt),
            'which scorep >> %s' % self.which_rpt,
            'scorep-info config-summary &> %s' % self.info_rpt,
        ]
        cubetree = 'cube_calltree -m time -p -t 1'
        self.post_run = [
            # can't test directly from vampir gui, dumping tracefile content:
            'otf2-print scorep_*_trace/traces.otf2 > %s' % self.rpt
            # 'otf2-print scorep-*/traces.otf2 > %s' % self.rpt
        ]
# }}}

# {{{ sanity
        # sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version and configuration:
            sn.assert_true(sphsscorep.scorep_version(self)),
            sn.assert_true(sphsscorep.scorep_info_papi_support(self)),
            sn.assert_true(sphsscorep.scorep_info_perf_support(self)),
            sn.assert_true(sphsscorep.scorep_info_unwinding_support(self)),
            # check the report:
            sn.assert_eq(sphsscorep.program_begin_count(self), self.num_tasks),
            sn.assert_eq(sphsscorep.program_end_count(self), self.num_tasks),
            # check the summary report:
            # sn.assert_found(r'^S=C=A=N: \S+ complete\.', self.stderr)
        ])
# }}}

# {{{ performance
        # {{{ internal timers
        # use linux date as timer:
        self.pre_run += ['echo starttime=`date +%s`']
        self.post_run += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # tool: scalasca
        tool_perf_patterns = sn.evaluate(sphssca.rpt_trace_stats_d(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # tool: scorep
        self.perf_patterns.update({
            'max_ipc_rk0': sphsscorep.ipc_rk0(self),
            'max_rumaxrss_rk0': sphsscorep.ru_maxrss_rk0(self),
        })
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool
        myzero_n = (0, None, None, 'count')
        myzero_ipc = (0, None, None, 'ins/cyc')
        myzero_kb = (0, None, None, 'kilobytes')
        # tool
        self.reference['*:mpi_latesender'] = myzero_n
        self.reference['*:mpi_latesender_wo'] = myzero_n
        self.reference['*:mpi_latereceiver'] = myzero_n
        self.reference['*:mpi_wait_nxn'] = myzero_n
        self.reference['*:max_ipc_rk0'] = myzero_ipc
        self.reference['*:max_rumaxrss_rk0'] = myzero_kb
        # self.reference['*:scorep_elapsed'] = (0, None, None, 's')
        # self.reference['*:%scorep_USR'] = (0, None, None, '%')
        # self.reference['*:%scorep_MPI'] = (0, None, None, '%')
        # top1_name = sphsscorep.scorep_top1_name(self)
        # self.reference['*:scorep_top1'] = (0, None, None, top1_name)
        # self.reference['*:%scorep_Energy_exclusive'] = (0, None, None, '%')
        # self.reference['*:%scorep_Energy_inclusive'] = (0, None, None, '%')
# }}}
# }}}

    @rfm.run_before('compile')
    def set_pe(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_before('run')
    def set_runflags(self):
        '''https://reframe-hpc.readthedocs.io/en/stable/pipeline.html
        '''
        self.tool_options = ['-analyze -t']
        self.job.launcher = LauncherWrapper(self.job.launcher,
                                            '%s' % self.tool,
                                            self.tool_options)
