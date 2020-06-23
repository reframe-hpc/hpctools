# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.sanity as sphs
import sphexa.sanity_scorep as sphsscorep
import sphexa.sanity_scorep_openacc as sphsscacc


@rfm.parameterized_test(*[[mpitask, steps, cycles, rumetric]
                          for mpitask in [1, 2, 4]  # , 8, 16]
                          for steps in [1]
                          for cycles in [0]
                          for rumetric in ['ru_maxrss,ru_utime']
                          ])
class SphExaNativeCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Score-P (MPI+OpenACC):

    4 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.
    :arg cycles: Compiler-instrumented code is required for OpenACC (regions
        obtained via sampling/unwinding cannot be filtered) => cycles is set to
        0.
    :arg rumetric: Record Linux Resource Usage Counters to provide information
        about consumed resources and operating system events such as
        user/system time, maximum resident set size, and number of page faults:
        man getrusage
    '''
    # }}}

    def __init__(self, mpitask, steps, cycles, rumetric):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-pgi']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'gpu', 'openacc'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
        self.prebuild_cmds = ['module rm xalt']
        self.prgenv_flags = {
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DNDEBUG', '-DUSE_MPI', '-DUSE_ACC',
                           '-DUSE_STD_MATH_IN_KERNELS',
                           '-acc', '-ta=tesla:managed,cc60'],  # -mp
        }
        # ---------------------------------------------------------------- tool
        self.modules = ['craype-accel-nvidia60']
        tc_ver = '19.10'
        tool_ver = '6.0'
        postproc_tool_ver = '4ef9d3f'
        postproc_tool_serial = 'otf-profiler'
        self.postproc_tool = 'otf-profiler-mpi'
        self.tool_modules = {
            'PrgEnv-pgi': ['Score-P/%s-CrayPGI-%s' % (tool_ver, tc_ver)]
        }
        # ---------------------------------------------------------------- tool
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'scorep-CC'
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
        # weak scaling = 10^6 p/cn:
        size_dict = {1: 100, 2: 126, 4: 159, 8: 200, 16: 252, 32: 318,
                     64: 400, 128: 504, 256: 635}
        cubesize = size_dict[mpitask]
        self.name = \
            'openacc_scorepT_{}_{:03d}mpi_{:03d}omp_{}n_{}steps_{}cycles_{}'. \
            format(self.testname, mpitask, ompthread, cubesize, steps, cycles,
                   rumetric)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 1
# {{{ ht:
        # self.num_tasks_per_node = mpitask if mpitask < 36 else 36   # noht
        # self.use_multithreading = False  # noht
        # self.num_tasks_per_core = 1      # noht

        # self.num_tasks_per_node = mpitask if mpitask < 72 else 72
        # self.use_multithreading = True # ht
        # self.num_tasks_per_core = 2    # ht
# }}}
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'SCOREP_OPENACC_ENABLE': 'yes',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'SCOREP_WRAPPER_INSTRUMENTER_FLAGS': '"--mpp=mpi --openacc"',
            'SCOREP_ENABLE_PROFILING': 'false',
            'SCOREP_ENABLE_TRACING': 'true',
            'SCOREP_FILTERING_FILE': 'myfilt',
            'SCOREP_VERBOSE': 'true',
            # Needed to avoid "No free memory page available"
            'SCOREP_TOTAL_MEMORY': '1G',
            # Adding some performance metrics:
            # http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/docs/
            # => scorep-6.0/html/measurement.html#rusage_counters
            # => https://vampir.eu/public/files/pdf/spcheatsheet_letter.pdf
            #   'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
            #   'SCOREP_METRIC_RUSAGE': 'ru_maxrss,ru_utime',
            #   'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
            #   'SCOREP_METRIC_RUSAGE': '',
            'SCOREP_METRIC_RUSAGE': rumetric,
            'SCOREP_METRIC_PAPI': 'PAPI_TOT_INS,PAPI_TOT_CYC',
        }
        self.rusage_name = sn.evaluate(sphsscacc.otf2cli_metric_name(self))
        if cycles > 0:
            self.variables['SCOREP_SAMPLING_EVENTS'] \
                = 'perf_cycles@%s' % cycles

        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'scorep-info.rpt'
        self.rpt = 'rpt'
        self.rpt_jsn = 'result.json'
        self.rpt_inclusive = '%s.inclusive' % self.rpt
        self.rpt_exclusive = '%s.exclusive' % self.rpt
        self.tool = 'scorep'
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps]
        self.prerun_cmds = [
            'module rm xalt',
            '%s --version &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
            'scorep-info config-summary &> %s' % self.info_rpt,
        ]
        self.postrun_cmds = [
            # otf-profiler is needed for postprocessing but i managed to
            # compile only gnu version => removing CubeLib to avoid conflict
            # with CrayPGI:
            'module rm CubeLib',
            'module load otf2_cli_profile/%s-CrayGNU-%s' %
            (postproc_tool_ver, tc_ver),
            # report post-processing tools version
            '%s --version' % postproc_tool_serial,
            # OTF-Profiler version 2.0.0
            'which %s %s' % (postproc_tool_serial, self.postproc_tool),
            # create result.json performance report from tracefile
            # see otf_profiler method (@run_after)
        ]
# }}}

# {{{ sanity
        # sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version and configuration:
            sn.assert_true(sphsscorep.scorep_version(self)),
            # Needed when using papi counters:
            # sn.assert_true(sphsscorep.scorep_info_papi_support(self)),
            sn.assert_true(sphsscorep.scorep_info_perf_support(self)),
            sn.assert_true(sphsscorep.scorep_info_unwinding_support(self)),
        ])
# }}}

# {{{ performance
        # {{{ internal timers
        # use linux date as timer:
        self.prerun_cmds += ['echo starttime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphsscacc.otf2cli_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        self.reference = sn.evaluate(sphsscacc.otf2cli_tool_reference(self))
# }}}
# }}}

# {{{ run_before/run_after
    @rfm.run_before('compile')
    def setflags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_after('setup')
    def launcher_cmd(self):
        self.launcher_cmd = ' '.join(self.job.launcher.command(self.job))

    @rfm.run_after('setup')
    def otf_profiler(self):
        '''
        If SCOREP_METRIC_RUSAGE is defined then set otf-profiler flags
        accordingly. Examples are:

        .. code-block::

          > otf-profiler --help
          'SCOREP_METRIC_RUSAGE': '',                   # 0 metric
          'SCOREP_METRIC_RUSAGE': 'ru_maxrss',          # 1 metric
          'SCOREP_METRIC_RUSAGE': 'ru_maxrss,ru_utime', # 2 metrics
          will give:
          "HardwareCounters": [],                       # 0 and >1 metrics
          "HardwareCounters": [                         # 1 metric
            "ru_maxrss",
            195656
          ],
        '''
        self.postrun_cmds += [
            'echo stoptime=`date +%s`',
            'echo start_pproc=`date +%s`',
            '%s %s -i scorep-*/traces.otf2 --json %s' %
            (self.launcher_cmd, self.postproc_tool,
             sn.evaluate(sphsscacc.otf2cli_metric_flag(self))),
            'echo stop_pproc=`date +%s`',
        ]
# }}}
