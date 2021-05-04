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


# {{{ class SphExa_Scorep_Profiling_Check
# @rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
# class SphExa_Scorep_Profiling_Check(rfm.RegressionTest):
@rfm.simple_test
class SphExa_Scorep_Profiling_Check(rfm.RegressionTest, hooks.setup_pe,
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
        # self.valid_prog_environs = ['PrgEnv-gnu']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['Score-P']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.tool = 'scorep'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'info.rpt'
        self.prebuild_cmds = [
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'which vampir >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
        ]
        # }}}

        # {{{ run
        self.variables = {
            # 'CRAYPE_LINK_TYPE': 'dynamic',
            # 'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'SCOREP_ENABLE_PROFILING': 'true',
            'SCOREP_ENABLE_TRACING': 'false',
            'SCOREP_ENABLE_UNWINDING': 'true',
            'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            # 'SCOREP_SAMPLING_EVENTS': 'PAPI_TOT_CYC@1000000',
            # 'SCOREP_SAMPLING_EVENTS': 'PAPI_TOT_CYC@%s' % cycles,
            # export SCOREP_SAMPLING_EVENTS=PAPI_TOT_CYC@1000000
            # empty SCOREP_SAMPLING_EVENTS will profile mpi calls only:
            # ok: 'SCOREP_SAMPLING_EVENTS': '',
            # 'SCOREP_METRIC_PAPI': 'PAPI_TOT_INS,PAPI_TOT_CYC',
            # 'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
            # 'SCOREP_TIMER': 'clock_gettime',
            # 'SCOREP_VERBOSE': 'true',
            'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            'SCOREP_TOTAL_MEMORY': '1G',
            # 'PATH': f'{tool_path}:{cube_path}:$PATH',
        }
        self.rpt = 'rpt'
        self.rpt_inclusive = '%s.inclusive' % self.rpt
        self.rpt_exclusive = '%s.exclusive' % self.rpt
        cubetree = 'cube_calltree -m time -p -t 1'
        # -m metricname -- print out values for the metric <metricname>
        # -i            -- calculate inclusive values instead of exclusive
        # -t treshold   -- print out only call path with a value larger
        #                  than <treshold>%
        # -p            -- diplay percent value
        self.postrun_cmds += [
            # working around memory crash in scorep-score:
            '(scorep-score -r scorep-*/profile.cubex ;rm -f core*) > %s' \
            % self.rpt,
            '(%s    scorep-*/profile.cubex ;rm -f core*) >> %s' \
            % (cubetree, self.rpt_exclusive),
            '(%s -i scorep-*/profile.cubex ;rm -f core*) >> %s' \
            % (cubetree, self.rpt_inclusive),
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
            # check the summary report:
            sn.assert_found(r'Estimated aggregate size of event trace',
                            self.rpt)
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('performance')
    def set_tool_perf_patterns(self):
        self.perf_patterns.update({
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
        })

    @rfm.run_before('performance')
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
        # top1_name = sphsscorep.scorep_top1_name(self)
        # TODO: self.reference['*:scorep_top1'] = (0, None, None, top1_name)
        # self.reference['*:scorep_top1'] = (0, None, None, '')

#     @rfm.run_before('compile')
#     def set_compiler_flags(self):
#         self.modules += ['Score-P']
#         # self.modules += self.tool_modules[self.current_environ.name]
#         # self.build_system.cxxflags = \
#         #     self.prgenv_flags[self.current_environ.name]
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


# {{{ class SphExa_Scorep_Tracing_Check
@rfm.simple_test
class SphExa_Scorep_Tracing_Check(rfm.RegressionTest, hooks.setup_pe,
                                  hooks.setup_code):
    # {{{
    '''
    This class runs the test code with Score-P (tracing mpi+openmp)
    '''
    # }}}
    steps = parameter([4])
    compute_node = parameter([1])  # standard vampir license up to 256
    np_per_c = parameter([1e4])
    cycles = parameter([5000000])
    scorep_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['Score-P']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.tool = 'scorep'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'info.rpt'
        self.prebuild_cmds = [
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'which vampir >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
            f'vampir --version >> {self.version_rpt}'
        ]
        # }}}

        # {{{ run
        self.variables = {
            'SCOREP_ENABLE_PROFILING': 'false',
            'SCOREP_ENABLE_TRACING': 'true',
            'SCOREP_ENABLE_UNWINDING': 'true',
            'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            'SCOREP_TOTAL_MEMORY': '1G',
            'SCOREP_METRIC_PAPI': 'PAPI_TOT_INS,PAPI_TOT_CYC',
            'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
        }
        self.rpt = 'rpt'
        self.postrun_cmds += [
            # can't test directly from vampir gui:
            'otf2-print scorep-*/traces.otf2 > %s' % self.rpt
        ]
        # }}}

        # {{{ sanity
        # }}}

    # {{{ hooks
    @rfm.run_before('sanity')
    def set_tool_sanity(self):
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_true(sphsscorep.scorep_info_papi_support(self)),
            sn.assert_true(sphsscorep.scorep_info_perf_support(self)),
            sn.assert_true(sphsscorep.scorep_info_unwinding_support(self)),
            # check the report:
            sn.assert_eq(
                sphsscorep.program_begin_count(self), self.num_tasks,
                msg='sphsscorep.program_begin_count failed: {0} != {1}'),
            sn.assert_eq(
                sphsscorep.program_end_count(self), self.num_tasks,
                msg='sphsscorep.program_end_count failed: {0} != {1}'),
            # TODO: create derived metric (ipc) in cube
        ])

    @rfm.run_before('performance')
    def set_tool_perf_patterns(self):
        self.perf_patterns.update({
            'max_ipc_rk0': sphsscorep.ipc_rk0(self),
            'max_rumaxrss_rk0': sphsscorep.ru_maxrss_rk0(self),
        })

    @rfm.run_before('performance')
    def set_tool_perf_reference(self):
        self.reference['*:max_ipc_rk0'] = (0, None, None, 'ins/cyc')
        self.reference['*:max_rumaxrss_rk0'] = (0, None, None, 'kilobytes')
    # }}}
# }}}
