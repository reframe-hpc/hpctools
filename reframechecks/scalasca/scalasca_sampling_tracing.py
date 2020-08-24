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
import sphexa.sanity_scalasca as sphssca
from reframe.core.launchers import LauncherWrapper


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {24: 100}
steps_dict = {24: 4}
cycles_dict = {24: 5000000}


@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaScalascaTracingCheck(rfm.RegressionTest):
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

    def __init__(self, mpi_task):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi',
                                    'PrgEnv-cray']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.tool = 'scalasca'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        tool_ver = '2.5'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'Scalasca/{tool_ver}-CrayGNU-{tc_ver}'],
            'PrgEnv-intel': [f'Scalasca/{tool_ver}-CrayIntel-{tc_ver}'],
            'PrgEnv-cray': [f'Scalasca/{tool_ver}-CrayCCE-{tc_ver}'],
            'PrgEnv-pgi': [f'Scalasca/{tool_ver}-CrayPGI-{tc_ver}'],
        }
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-Ofast',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'scorep --mpp=mpi --nocompiler CC'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'./{self.testname}.exe'
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        cycles = cycles_dict[mpi_task]
        self.name = \
            'sphexa_scalascaS+T_{}_{:03d}mpi_{:03d}omp_{}n_{}steps_{}cycles'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps, cycles)
        self.num_tasks_per_node = 24
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
        self.time_limit = '10m'
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
        # self.cubetool = 'cube_calltree'
        self.executable_opts = [
            f'-n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} -V &> {self.version_rpt}',
            f'scorep --version >> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'which scorep >> {self.which_rpt}',
            # f'which {self.cubetool} >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
        ]
        cubetree = 'cube_calltree -m time -p -t 1'
        # -m metricname -- print out values for the metric <metricname>
        # -i            -- calculate inclusive values instead of exclusive
        # -t treshold   -- print out only call path with a value larger
        #                  than <treshold>%
        # -p            -- diplay percent value
        self.postrun_cmds = [
            # can't test directly from vampir gui, dumping tracefile content:
            'otf2-print scorep_*_trace/traces.otf2 > %s' % self.rpt
            # 'otf2-print scorep-*/traces.otf2 > %s' % self.rpt
        ]
        # }}}

        # {{{ sanity
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
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
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

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
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
    # }}}
