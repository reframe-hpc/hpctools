# Copyright 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility as util
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.hooks as hooks
import sphexa.sanity as sphs
import sphexa.sanity_scorep as sphsscorep
import sphexa.sanity_scalasca as sphssca
from reframe.core.launchers import LauncherWrapper


# {{{ class SphExa_Scalasca_Profiling_Check
@rfm.simple_test
class SphExa_Scalasca_Profiling_Check(rfm.RegressionTest, hooks.setup_pe,
                                      hooks.setup_code):
    # {{{
    '''
    This class runs the test code with Score-P (mpi+openmp):
    Parameters can be set for this simulation:

    :arg cycles: sampling sources generate interrupts that trigger a sample.
         SCOREP_SAMPLING_EVENTS sets the sampling source:
         see $EBROOTSCOREMINP/share/doc/scorep/html/sampling.html .
         Very large values will produce unreliable performance report,
         very small values will have a large runtime overhead.

    Typical performance reporting:

    .. code-block:: none

       sphexa_scorepS+P_sqpatch_024mpi_001omp_100n_10steps_1000000cycles
       - dom:gpu
          - PrgEnv-gnu
             * num_tasks: 24
             * Elapsed: 46.9216 s
             * MomentumEnergyIAD: 14.1238 s
             * Timestep: 8.0414 s
             * %MomentumEnergyIAD: 30.1 %
             * %Timestep: 17.14 %
             * scorep_elapsed: 47.9408 s
             * %scorep_USR: 71.5 %
             * %scorep_MPI: 23.2 %
             * scorep_top1: 30.9 % (sph::computeMomentumAndEnergyIADImpl)
             * %scorep_Energy_exclusive: 30.913 %
             * %scorep_Energy_inclusive: 30.913 %
    '''
    # }}}
    steps = parameter([4])
    compute_node = parameter([1])  # standard vampir license up to 256
    # compute_node = parameter([100, 200, 300, 400, 500])
    np_per_c = parameter([1e4])
    cycles = parameter([5000000])
    # module_info = parameter(util.find_modules('Score-P/7'))
    scorep_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['Scalasca']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.tool = 'scalasca'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'info.rpt'
        self.cubetool = 'cube_calltree'
        self.prebuild_cmds = [
            f'{self.tool} -V &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'scorep --version >> {self.version_rpt}',
            f'which scorep >> {self.which_rpt}',
            f'which vampir >> {self.which_rpt}',
            f'which {self.cubetool} >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
            f'# step1: prepare executable with: scalasca -instrument (skin)',
            f'# step2: run executable with: scalasca -analyze (scan)',
            f'# step3: explore report with: scalasca -examine (square)',
            f'# step4: get calltree with: cube_calltree'
        ]
        # }}}

        # {{{ run
        self.variables = {
            'SCOREP_ENABLE_UNWINDING': 'true',
            'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            'SCOREP_TOTAL_MEMORY': '1G',
        }
        self.rpt = 'rpt'
        self.rpt_score = 'scorep-score.rpt'
        self.rpt_exclusive = 'cube_calltree_exclusive.rpt'
        self.rpt_inclusive = 'cube_calltree_inclusive.rpt'
        #
        cubetree = 'cube_calltree -m time -p -t 1'
        # -m metricname -- print out values for the metric <metricname>
        # -i            -- calculate inclusive values instead of exclusive
        # -t treshold   -- print out only call path with a value larger
        #                  than <treshold>%
        # -p            -- diplay percent value
        self.postrun_cmds += [
            f'# -------------------------------------------------------------',
            # generate summary.cubex from profile.cubex with: scalasca -examine
            # (it will report scoring too)
            f'{self.tool} -examine -s scorep_*sum/profile.cubex &> {self.rpt}',
            # rpt will always be written to scorep.score, not into self.rpt
            f'rm -f core*',
            # this file is used for sanity checks:
            f'cp scorep_*_sum/scorep.score {self.rpt_score}',
            # exclusive time:
            f'({cubetree} scorep_*_sum/summary.cubex ;rm -f core*) &>'
            f' {self.rpt_exclusive}',
            # inclusive time:
            f'({cubetree} -i scorep_*_sum/summary.cubex ;rm -f core*) &>'
            f' {self.rpt_inclusive}',
            f'# -------------------------------------------------------------',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version and configuration:
            # sn.assert_true(sphsscorep.scorep_assert_version(self)),
            sn.assert_true(sphsscorep.scorep_info_papi_support(self)),
            sn.assert_true(sphsscorep.scorep_info_perf_support(self)),
            sn.assert_true(sphsscorep.scorep_info_unwinding_support(self)),
            # check the tool report:
            sn.assert_found(r'Estimated aggregate size of event trace',
                            self.rpt_score),
            sn.assert_found(r'^S=C=A=N: \S+ complete\.', self.stderr)
        ])
        # }}}

    # {{{ hooks
    # {{{ run
    @run_before('run')
    def set_runflags(self):
        self.tool_options = ['-analyze -s']
        self.job.launcher = LauncherWrapper(self.job.launcher, self.tool,
                                            self.tool_options)
    # }}}

    # {{{ performance
    @run_before('performance')
    def set_tool_perf_patterns(self):
        perf_patterns = {
            'scorep_elapsed': sphsscorep.scorep_elapsed(self),
            '%scorep_USR': sphsscorep.scorep_usr_pct(self),
            '%scorep_MPI': sphsscorep.scorep_mpi_pct(self),
            '%scorep_COM': sphsscorep.scorep_com_pct(self),
            '%scorep_OMP': sphsscorep.scorep_omp_pct(self),
            '%scorep_Energy_exclusive':
                sphsscorep.scorep_exclusivepct_energy(self),
            '%scorep_Energy_inclusive':
                sphsscorep.scorep_inclusivepct_energy(self),
            'scorep_top1_tracebuffersize':
                sphsscorep.scorep_top1_tracebuffersize(self),
        }
        if self.perf_patterns:
            self.perf_patterns.update(perf_patterns)
        else:
            self.perf_patterns = perf_patterns

    @run_before('performance')
    def set_tool_perf_reference(self):
        myzero_b = (0, None, None, 'B')
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        self.reference['*:scorep_elapsed'] = myzero_s
        self.reference['*:%scorep_USR'] = myzero_p
        self.reference['*:%scorep_MPI'] = myzero_p
        self.reference['*:%scorep_COM'] = myzero_p
        self.reference['*:%scorep_OMP'] = myzero_p
        self.reference['*:%scorep_Energy_exclusive'] = myzero_p
        self.reference['*:%scorep_Energy_inclusive'] = myzero_p
        top1_name = 'B ' + sphsscorep.scorep_top1_tracebuffersize_name(self)
        self.reference['*:scorep_top1_tracebuffersize'] = \
            (0, None, None, top1_name)
    # }}}
    # }}}

    # TODO:
    # def setup(self, partition, environ, **job_opts):
    #     super().setup(partition, environ, **job_opts)
    #     partitiontype = partition.fullname.split(':')[1]
    #     if partitiontype == 'gpu':
    #         self.job.options = ['--constraint="gpu&perf"']
    #     elif partitiontype == 'mc':
    #         self.job.options = ['--constraint="mc&perf"']
# }}}


# {{{ class SphExa_Scalasca_Tracing_Check
@rfm.simple_test
class SphExa_Scalasca_Tracing_Check(rfm.RegressionTest, hooks.setup_pe,
                                    hooks.setup_code):
    steps = parameter([4])
    compute_node = parameter([1])  # standard vampir license up to 256
    # compute_node = parameter([100, 200, 300, 400, 500])
    np_per_c = parameter([1e4])
    cycles = parameter([5000000])
    scorep_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['Scalasca']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.tool = 'scalasca'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'info.rpt'
        self.cubetool = 'cube_calltree'
        self.prebuild_cmds = [
            f'{self.tool} -V &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'scorep --version >> {self.version_rpt}',
            f'which scorep >> {self.which_rpt}',
            f'which vampir >> {self.which_rpt}',
            f'which {self.cubetool} >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
            f'# step1: prepare executable with: scalasca -instrument (skin)',
            f'# step2: run executable with: scalasca -analyze (scan)',
            f'# step3: explore report with: scalasca -examine (square)',
            f'# step4: get calltree with: cube_calltree'
        ]
        # }}}

        # {{{ run
        self.variables = {
            'SCOREP_ENABLE_UNWINDING': 'true',
            'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            # To avoid "No free memory page available":
            'SCOREP_TOTAL_MEMORY': '1G',
            # Advanced performance metrics:
            # 'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
            # 'SCOREP_METRIC_PAPI': 'PAPI_TOT_INS,PAPI_TOT_CYC',
        }
        self.rpt_score = 'scorep-score.rpt'
        self.rpt_inclusive = 'cube_calltree_inclusive.rpt'
        self.rpt_exclusive = 'cube_calltree_exclusive.rpt'
        self.rpt_otf2 = 'otf2-print.rpt'
        #
        cubetree = 'cube_calltree -m time -p -t 1'
        # -m metricname -- print out values for the metric <metricname>
        # -i            -- calculate inclusive values instead of exclusive
        # -t treshold   -- print out only call path with a value larger
        #                  than <treshold>%
        # -p            -- diplay percent value
        self.postrun_cmds += [
            f'# -------------------------------------------------------------',
            f'scorep-score -r scorep*_trace/profile.cubex > {self.rpt_score}',
            # exclusive time (+ workaround memory crash):
            f'({cubetree} scorep*_trace/profile.cubex ;rm -f core*) &>'
            f' {self.rpt_exclusive}',
            # inclusive time (+ workaround memory crash):
            f'({cubetree} -i scorep*_trace/profile.cubex ;rm -f core*) &>'
            f' {self.rpt_inclusive}',
            # can't test directly vampir gui hence dumping tracefile content:
            f'otf2-print scorep*_trace/traces.otf2 > {self.rpt_otf2}',
            f'# -------------------------------------------------------------',
        ]
        # }}}

    # {{{ hooks
    # {{{ run
    @run_before('run')
    def set_runflags(self):
        self.tool_options = ['-analyze -t']
        self.job.launcher = LauncherWrapper(self.job.launcher, self.tool,
                                            self.tool_options)
    # }}}

    # {{{ sanity
    @run_before('sanity')
    def set_tool_sanity(self):
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version and configuration:
            # sn.assert_true(sphsscorep.scorep_assert_version(self)),
            sn.assert_true(sphsscorep.scorep_info_papi_support(self)),
            sn.assert_true(sphsscorep.scorep_info_perf_support(self)),
            sn.assert_true(sphsscorep.scorep_info_unwinding_support(self)),
            # check the tool report:
            sn.assert_found(r'^S=C=A=N: \S+ complete\.', self.stderr),
            sn.assert_eq(
                sphsscorep.program_begin_count(self), self.num_tasks,
                msg='sphsscorep.program_begin_count failed: {0} != {1}'),
            sn.assert_eq(
                sphsscorep.program_end_count(self), self.num_tasks,
                msg='sphsscorep.program_end_count failed: {0} != {1}'),
        ])
    # }}}

    # {{{ performance
    @run_before('performance')
    def set_tool_perf_patterns(self):
        self.stat_rpt = (f'scorep_mpi+omp_{self.num_tasks}x'
                         f'{self.omp_threads}_trace/trace.stat')
        perf_patterns = {
            'scorep_elapsed': sphsscorep.scorep_elapsed(self),
            '%scorep_USR': sphsscorep.scorep_usr_pct(self),
            '%scorep_MPI': sphsscorep.scorep_mpi_pct(self),
            '%scorep_COM': sphsscorep.scorep_com_pct(self),
            '%scorep_OMP': sphsscorep.scorep_omp_pct(self),
            '%scorep_Energy_exclusive':
                sphsscorep.scorep_exclusivepct_energy(self),
            '%scorep_Energy_inclusive':
                sphsscorep.scorep_inclusivepct_energy(self),
            'sca_ompbarrier': sphssca.rpt_tracestats_omp(self)['omp_ibarrier'],
            'sca_omplock': sphssca.rpt_tracestats_omp(self)['omp_lock'],
        }
        if self.perf_patterns:
            self.perf_patterns.update(perf_patterns)
        else:
            self.perf_patterns = perf_patterns

    @run_before('performance')
    def set_tool_perf_reference(self):
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        self.reference['*:scorep_elapsed'] = myzero_s
        self.reference['*:%scorep_USR'] = myzero_p
        self.reference['*:%scorep_MPI'] = myzero_p
        self.reference['*:%scorep_COM'] = myzero_p
        self.reference['*:%scorep_OMP'] = myzero_p
        self.reference['*:%scorep_Energy_exclusive'] = myzero_p
        self.reference['*:%scorep_Energy_inclusive'] = myzero_p
        self.reference['*:sca_ompbarrier'] = myzero_s
        self.reference['*:sca_omplock'] = myzero_s
    # }}}
    # }}}

    # TODO:
    # def setup(self, partition, environ, **job_opts):
    #     super().setup(partition, environ, **job_opts)
    #     partitiontype = partition.fullname.split(':')[1]
    #     if partitiontype == 'gpu':
    #         self.job.options = ['--constraint="gpu&perf"']
    #     elif partitiontype == 'mc':
    #         self.job.options = ['--constraint="mc&perf"']
# }}}
