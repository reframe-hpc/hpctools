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


# {{{ class SphExa_Scalasca_User_Profiling_Check
@rfm.simple_test
class SphExa_Scalasca_Profiling_User_Check(rfm.RegressionTest, hooks.setup_pe,
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
    # steps = parameter([4])
    # compute_node = parameter([1])  # standard vampir license up to 256
    # np_per_c = parameter([1e4])
    # weak scaling:
    steps = parameter([2])
    compute_node = parameter([2])
    # compute_node = parameter([1, 2, 4, 8, 16, 32])
    np_per_c = parameter([1e5])
    # cycles = parameter([5000000])
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
        self.executable = 'mpi+omp'
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
            f'which cube_remap2 >> {self.which_rpt}',
            f'which cube_dump >> {self.which_rpt}',
            f'which {self.cubetool} >> {self.which_rpt}',
            # f'which vampir >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
            f'# step1: prepare executable with: scalasca -instrument (skin)',
            f'# step2: run executable with: scalasca -analyze (scan)',
            f'# step3: explore report with: scalasca -examine (square)',
            f'# step4: get calltree with: cube_calltree'
        ]
        # }}}

        # {{{ run
        self.variables = {
            # 'SCOREP_ENABLE_UNWINDING': 'true',
            # 'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            # 'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            'SCOREP_TOTAL_MEMORY': '1G',
            # 'SCOREP_TIMER': 'gettimeofday',
            'SCAN_ANALYZE_OPTS': '--time-correct',
        }
        self.rpt = 'rpt'
        self.rpt_score = 'scorep-score.rpt'
        self.rpt_exclusive = 'cube_calltree_exclusive.rpt'
        self.rpt_inclusive = 'cube_calltree_inclusive.rpt'
        #
        cubetree = 'cube_calltree -m time -p -t 1'
        self.postrun_cmds += [
            '# {{{ --- Postprocessing steps: ---',
            f'# -------------------------------------------------------------',
            '# profile.cubex - scalasca -examine -s = square -> scorep.score:',
            f'# ({self.rpt_score} is used by sanity checks)',
            f'scalasca -examine -s scorep_*sum/profile.cubex &> {self.rpt}',
            f'cp scorep_*_sum/scorep.score {self.rpt_score}',
            '# --------------------------------------------------------------',
            '# transform metric tree into metric hierarchy with remap2',
            '# profile.cubex - cube_remap2 (slow)          -> summary.cubex: ',
            f'# time -p cube_remap2 -d -o summary.cubex */profile.cubex',
            f'# scorep-score summary.cubex &> {self.rpt_score}',
            '# --------------------------------------------------------------',
            '# exclusive time: summary.cubex - cubetree -> rpt_exclusive:',
            f'# ({cubetree} scorep_*_sum/summary.cubex ;rm -f core*) &>'
            f' {self.rpt_exclusive}',
            '# --------------------------------------------------------------',
            '# inclusive time: summary.cubex - cubetree -i -> rpt_inclusive:',
            f'# ({cubetree} -i scorep_*_sum/summary.cubex ;rm -f core*) &>'
            f' {self.rpt_inclusive}',
            '# -m metricname -- print out values for the metric <metricname>',
            '# -i            -- calculate inclusive values instead of',
            '#                  exclusive',
            '# -t treshold   -- print out only call path with a value larger',
            '#                  than <treshold>%',
            '# -p            -- diplay percent value',
            '# --------------------------------------------------------- }}}',
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
    # {{{ instrument
    @run_before('compile')
    def set_instrumentation(self):
        srcfile = 'src/sedov/sedov.cpp'
        # {{{
        instr0 = '#include "scorep/SCOREP_User.h"'
        sed0 = f'9s@.*@&\\n{instr0}@'
        instr1 = '    SCOREP_RECORDING_OFF() // must be _after_ mpi_init'
        sed1 = f'26s@.*@&\\n{instr1}@'
        instr2 = '    SCOREP_RECORDING_ON()'
        sed2 = f'88s@.*@&\\n{instr2}@'
        #
        instr3 = '        {SCOREP_USER_REGION("domain.sync.jg", '
        instr4 = '        {SCOREP_USER_REGION("updateTasks.jg", '
        instr5 = '        {SCOREP_USER_REGION("FindNeighbors.jg", '
        instr6 = '        {SCOREP_USER_REGION("Density.jg", '
        instr7 = '        {SCOREP_USER_REGION("EquationOfState.jg", '
        instr8 = '        {SCOREP_USER_REGION("mpi.synchronizeHalos.jg", '
        instr9 = '        {SCOREP_USER_REGION("IAD.jg", '
        instr10 = '        {SCOREP_USER_REGION("mpi.synchronizeHalos.jg", '
        instr11 = '        {SCOREP_USER_REGION("MomentumEnergyIAD.jg", '
        instr12 = '        {SCOREP_USER_REGION("Timestep.jg", '
        instr13 = '        {SCOREP_USER_REGION("UpdateQuantities.jg", '
        instr14 = '        {SCOREP_USER_REGION("EnergyConservation.jg", '
        instr15 = '        {SCOREP_USER_REGION("UpdateSmoothingLength.jg", '
        instr_type = 'SCOREP_USER_REGION_TYPE_COMMON)'
        #
        sed3 = f'92s@.*@{instr3}{instr_type}\\n&@'
        sed4 = f'96s@.*@{instr4}{instr_type}\\n&@'
        sed5 = f'106s@.*@{instr5}{instr_type}\\n&@'
        sed6 = f'108s@.*@{instr6}{instr_type}\\n&@'
        sed7 = f'110s@.*@{instr7}{instr_type}\\n&@'
        sed8 = f'112s@.*@{instr8}{instr_type}\\n&@'
        sed9 = f'114s@.*@{instr9}{instr_type}\\n&@'
        sed10 = f'116s@.*@{instr10}{instr_type}\\n&@'
        sed11 = f'118s@.*@{instr11}{instr_type}\\n&@'
        sed12 = f'120s@.*@{instr12}{instr_type}\\n&@'
        sed13 = f'122s@.*@{instr13}{instr_type}\\n&@'
        sed14 = f'124s@.*@{instr14}{instr_type}\\n&@'
        sed15 = f'126s@.*@{instr15}{instr_type}\\n&@'
        #
        instr_ = '        }'
        sed3_ = f'94s@.*@{instr_}\\n// &@'
        sed4_ = f'105s@.*@{instr_}\\n// &@'
        sed5_ = f'107s@.*@{instr_}\\n// &@'
        sed6_ = f'109s@.*@{instr_}\\n// &@'
        sed7_ = f'111s@.*@{instr_}\\n// &@'
        sed8_ = f'113s@.*@{instr_}\\n// &@'
        sed9_ = f'115s@.*@{instr_}\\n// &@'
        sed10_ = f'117s@.*@{instr_}\\n// &@'
        sed11_ = f'119s@.*@{instr_}\\n// &@'
        sed12_ = f'121s@.*@{instr_}\\n// &@'
        sed13_ = f'123s@.*@{instr_}\\n// &@'
        sed14_ = f'125s@.*@{instr_}\\n// &@'
        sed15_ = f'127s@.*@{instr_}\\n// &@'
        # NOTE: SCOREP_RECORDING_OFF() before mpi_finalize will report
        # negative values (wrong): mpi_finalize must be profiled/traced.
        # }}}
        self.prebuild_cmds += [
            f'sed -i '
            f'-e \'{sed0}\' \\\n'
            f'-e \'{sed1}\' \\\n'
            f'-e \'{sed2}\' \\\n'
            f'-e \'{sed3}\' -e \'{sed3_}\' \\\n'
            f'-e \'{sed4}\' -e \'{sed4_}\' \\\n'
            f'-e \'{sed5}\' -e \'{sed5_}\' \\\n'
            f'-e \'{sed6}\' -e \'{sed6_}\' \\\n'
            f'-e \'{sed7}\' -e \'{sed7_}\' \\\n'
            f'-e \'{sed8}\' -e \'{sed8_}\' \\\n'
            f'-e \'{sed9}\' -e \'{sed9_}\' \\\n'
            f'-e \'{sed10}\' -e \'{sed10_}\' \\\n'
            f'-e \'{sed11}\' -e \'{sed11_}\' \\\n'
            f'-e \'{sed12}\' -e \'{sed12_}\' \\\n'
            f'-e \'{sed13}\' -e \'{sed13_}\' \\\n'
            f'-e \'{sed14}\' -e \'{sed14_}\' \\\n'
            f'-e \'{sed15}\' -e \'{sed15_}\' \\\n'
            f'{srcfile}',
        ]
    # }}}

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
        self.perf_patterns = {}
        perf_patterns = {
            'scorep_elapsed': sphsscorep.scorep_elapsed(self),
            '%scorep_USR': sphsscorep.scorep_usr_pct(self),
            '%scorep_MPI': sphsscorep.scorep_mpi_pct(self),
            '%scorep_COM': sphsscorep.scorep_com_pct(self),
            '%scorep_OMP': sphsscorep.scorep_omp_pct(self),
            # '%scorep_Energy_exclusive':
            #     sphsscorep.scorep_exclusivepct_energy(self),
            # '%scorep_Energy_inclusive':
            #     sphsscorep.scorep_inclusivepct_energy(self),
            # 'scorep_top1_tracebuffersize':
            #     sphsscorep.scorep_top1_tracebuffersize(self),
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
        # self.reference['*:%scorep_Energy_exclusive'] = myzero_p
        # self.reference['*:%scorep_Energy_inclusive'] = myzero_p
        # top1_name = 'B ' + sphsscorep.scorep_top1_tracebuffersize_name(self)
        # self.reference['*:scorep_top1_tracebuffersize'] = \
        #     (0, None, None, top1_name)
    # }}}
    # }}}
# }}}


# {{{ class SphExaCuda_Scalasca_User_Profiling_Check
@rfm.simple_test
class SphExaCuda_Scalasca_Profiling_User_Check(rfm.RegressionTest,
                                               hooks.setup_pe,
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
    # steps = parameter([4])
    # compute_node = parameter([1])  # standard vampir license up to 256
    # np_per_c = parameter([1e4])
    # weak scaling:
    steps = parameter([10])
    # compute_node = parameter([1, 2])
    compute_node = parameter([1, 2, 4, 8, 16])
    np_per_c = parameter([5e6])
    # cycles = parameter([5000000])
    # module_info = parameter(util.find_modules('Score-P/7'))
    scorep_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        # self.modules = ['Scalasca']
        self.modules = [
            'cdt-cuda', 'craype-accel-nvidia60', 'cudatoolkit', 'Scalasca']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'gpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.time_limit = '30m'
        self.executable = 'mpi+omp+cuda'
        self.target_executable = 'mpi+omp+cuda'
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
            f'which cube_remap2 >> {self.which_rpt}',
            f'which cube_dump >> {self.which_rpt}',
            f'which {self.cubetool} >> {self.which_rpt}',
            # f'which vampir >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
            f'# step1: prepare executable with: scalasca -instrument (skin)',
            f'# step2: run executable with: scalasca -analyze (scan)',
            f'# step3: explore report with: scalasca -examine (square)',
            f'# step4: get calltree with: cube_calltree'
        ]
        # }}}

        # {{{ run
        self.variables = {
            # 'SCOREP_ENABLE_UNWINDING': 'true',
            # 'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            # 'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            'SCOREP_TOTAL_MEMORY': '1G',
            # 'SCOREP_TIMER': 'gettimeofday',
            'SCAN_ANALYZE_OPTS': '--time-correct',
        }
        self.rpt = 'rpt'
        self.rpt_score = 'scorep-score.rpt'
        self.rpt_exclusive = 'cube_calltree_exclusive.rpt'
        self.rpt_inclusive = 'cube_calltree_inclusive.rpt'
        #
        cubetree = 'cube_calltree -m time -p -t 1'
        self.postrun_cmds += [
            '# {{{ --- Postprocessing steps: ---',
            f'# -------------------------------------------------------------',
            '# profile.cubex - scalasca -examine -s = square -> scorep.score:',
            f'# ({self.rpt_score} is used by sanity checks)',
            f'scalasca -examine -s scorep_*sum/profile.cubex &> {self.rpt}',
            f'cp scorep_*_sum/scorep.score {self.rpt_score}',
            '# --------------------------------------------------------------',
            f'cube_remap2 -d scorep_*sum/profile.cubex # -> remap.cubex',
            f'cube_stat -m time -% remap.cubex > remap.cubex.csv',
            f'# cube_dump -m time remap.cubex -c level=1 '
            f'> remap.cubex.regions',
            f'# cube_dump -m time remap.cubex -c level=1 -s csv2 -z incl '
            f'> remap.cubex.csv',
            '# --------------------------------------------------------------',
            '# transform metric tree into metric hierarchy with remap2',
            '# profile.cubex - cube_remap2 (slow)          -> summary.cubex: ',
            f'# time -p cube_remap2 -d -o summary.cubex */profile.cubex',
            f'# scorep-score summary.cubex &> {self.rpt_score}',
            '# --------------------------------------------------------------',
            '# exclusive time: summary.cubex - cubetree -> rpt_exclusive:',
            f'# ({cubetree} scorep_*_sum/summary.cubex ;rm -f core*) &>'
            f' {self.rpt_exclusive}',
            '# --------------------------------------------------------------',
            '# inclusive time: summary.cubex - cubetree -i -> rpt_inclusive:',
            f'# ({cubetree} -i scorep_*_sum/summary.cubex ;rm -f core*) &>'
            f' {self.rpt_inclusive}',
            '# -m metricname -- print out values for the metric <metricname>',
            '# -i            -- calculate inclusive values instead of',
            '#                  exclusive',
            '# -t treshold   -- print out only call path with a value larger',
            '#                  than <treshold>%',
            '# -p            -- diplay percent value',
            '# --------------------------------------------------------- }}}',
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
    # {{{ instrument
    @run_before('compile')
    def set_instrumentation(self):
        srcfile = 'src/sedov/sedov.cpp'
        # {{{
        instr0 = '#include "scorep/SCOREP_User.h"'
        sed0 = f'9s@.*@&\\n{instr0}@'
        instr1 = '    SCOREP_RECORDING_OFF() // must be _after_ mpi_init'
        sed1 = f'26s@.*@&\\n{instr1}@'
        instr2 = '    SCOREP_RECORDING_ON()'
        sed2 = f'88s@.*@&\\n{instr2}@'
        #
        instr3 = '        {SCOREP_USER_REGION("domain.sync.jg", '
        instr4 = '        {SCOREP_USER_REGION("updateTasks.jg", '
        instr5 = '        {SCOREP_USER_REGION("FindNeighbors.jg", '
        instr6 = '        {SCOREP_USER_REGION("Density.jg", '
        instr7 = '        {SCOREP_USER_REGION("EquationOfState.jg", '
        instr8 = '        {SCOREP_USER_REGION("mpi.synchronizeHalos1.jg", '
        instr9 = '        {SCOREP_USER_REGION("IAD.jg", '
        instr10 = '        {SCOREP_USER_REGION("mpi.synchronizeHalos2.jg", '
        instr11 = '        {SCOREP_USER_REGION("MomentumEnergyIAD.jg", '
        instr12 = '        {SCOREP_USER_REGION("Timestep.jg", '
        instr13 = '        {SCOREP_USER_REGION("UpdateQuantities.jg", '
        instr14 = '        {SCOREP_USER_REGION("EnergyConservation.jg", '
        instr15 = '        {SCOREP_USER_REGION("UpdateSmoothingLength.jg", '
        instr_type = 'SCOREP_USER_REGION_TYPE_COMMON)'
        #
        sed3 = f'92s@.*@{instr3}{instr_type}\\n&@'
        sed4 = f'96s@.*@{instr4}{instr_type}\\n&@'
        sed5 = f'106s@.*@{instr5}{instr_type}\\n&@'
        sed6 = f'108s@.*@{instr6}{instr_type}\\n&@'
        sed7 = f'110s@.*@{instr7}{instr_type}\\n&@'
        sed8 = f'112s@.*@{instr8}{instr_type}\\n&@'
        sed9 = f'114s@.*@{instr9}{instr_type}\\n&@'
        sed10 = f'116s@.*@{instr10}{instr_type}\\n&@'
        sed11 = f'118s@.*@{instr11}{instr_type}\\n&@'
        sed12 = f'120s@.*@{instr12}{instr_type}\\n&@'
        sed13 = f'122s@.*@{instr13}{instr_type}\\n&@'
        sed14 = f'124s@.*@{instr14}{instr_type}\\n&@'
        sed15 = f'126s@.*@{instr15}{instr_type}\\n&@'
        #
        instr_ = '        }'
        sed3_ = f'94s@.*@{instr_}\\n// &@'
        sed4_ = f'105s@.*@{instr_}\\n// &@'
        sed5_ = f'107s@.*@{instr_}\\n// &@'
        sed6_ = f'109s@.*@{instr_}\\n// &@'
        sed7_ = f'111s@.*@{instr_}\\n// &@'
        sed8_ = f'113s@.*@{instr_}\\n// &@'
        sed9_ = f'115s@.*@{instr_}\\n// &@'
        sed10_ = f'117s@.*@{instr_}\\n// &@'
        sed11_ = f'119s@.*@{instr_}\\n// &@'
        sed12_ = f'121s@.*@{instr_}\\n// &@'
        sed13_ = f'123s@.*@{instr_}\\n// &@'
        sed14_ = f'125s@.*@{instr_}\\n// &@'
        sed15_ = f'127s@.*@{instr_}\\n// &@'
        # NOTE: SCOREP_RECORDING_OFF() before mpi_finalize will report
        # negative values (wrong): mpi_finalize must be profiled/traced.
        # }}}
        self.prebuild_cmds += [
            f'sed -i '
            f'-e \'{sed0}\' \\\n'
            f'-e \'{sed1}\' \\\n'
            f'-e \'{sed2}\' \\\n'
            f'-e \'{sed3}\' -e \'{sed3_}\' \\\n'
            f'-e \'{sed4}\' -e \'{sed4_}\' \\\n'
            f'-e \'{sed5}\' -e \'{sed5_}\' \\\n'
            f'-e \'{sed6}\' -e \'{sed6_}\' \\\n'
            f'-e \'{sed7}\' -e \'{sed7_}\' \\\n'
            f'-e \'{sed8}\' -e \'{sed8_}\' \\\n'
            f'-e \'{sed9}\' -e \'{sed9_}\' \\\n'
            f'-e \'{sed10}\' -e \'{sed10_}\' \\\n'
            f'-e \'{sed11}\' -e \'{sed11_}\' \\\n'
            f'-e \'{sed12}\' -e \'{sed12_}\' \\\n'
            f'-e \'{sed13}\' -e \'{sed13_}\' \\\n'
            f'-e \'{sed14}\' -e \'{sed14_}\' \\\n'
            f'-e \'{sed15}\' -e \'{sed15_}\' \\\n'
            f'{srcfile}',
        ]
    # }}}

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
        self.perf_patterns = {}
        perf_patterns = {
            'scorep_elapsed': sphsscorep.scorep_elapsed(self),
            '%scorep_USR': sphsscorep.scorep_usr_pct(self),
            '%scorep_MPI': sphsscorep.scorep_mpi_pct(self),
            '%scorep_COM': sphsscorep.scorep_com_pct(self),
            '%scorep_OMP': sphsscorep.scorep_omp_pct(self),
            # '%scorep_Energy_exclusive':
            #     sphsscorep.scorep_exclusivepct_energy(self),
            # '%scorep_Energy_inclusive':
            #     sphsscorep.scorep_inclusivepct_energy(self),
            # 'scorep_top1_tracebuffersize':
            #     sphsscorep.scorep_top1_tracebuffersize(self),
            'scregion_domain.sync': sphsscorep.cube_dump(self, 1),
            'scregion_updateTasks': sphsscorep.cube_dump(self, 2),
            'scregion_FindNeighbors': sphsscorep.cube_dump(self, 3),
            'scregion_Density': sphsscorep.cube_dump(self, 4),
            'scregion_EquationOfState': sphsscorep.cube_dump(self, 5),
            'scregion_synchronizeHalos1': sphsscorep.cube_dump(self, 6),
            'scregion_IAD': sphsscorep.cube_dump(self, 7),
            'scregion_synchronizeHalos2': sphsscorep.cube_dump(self, 8),
            'scregion_MomentumEnergyIAD': sphsscorep.cube_dump(self, 9),
            'scregion_Timestep': sphsscorep.cube_dump(self, 10),
            'scregion_UpdateQuantities': sphsscorep.cube_dump(self, 11),
            'scregion_EnergyConservation': sphsscorep.cube_dump(self, 12),
            'scregion_UpdateSmoothingLength': sphsscorep.cube_dump(self, 13),
            'scregion_findNeighborsSfc': sphsscorep.cube_dump(self, 14),
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
        # self.reference['*:%scorep_Energy_exclusive'] = myzero_p
        # self.reference['*:%scorep_Energy_inclusive'] = myzero_p
        # top1_name = 'B ' + sphsscorep.scorep_top1_tracebuffersize_name(self)
        # self.reference['*:scorep_top1_tracebuffersize'] = \
        #     (0, None, None, top1_name)
        self.reference['*:domain.sync'] = myzero_s
        self.reference['*:scregion_domain.sync'] = myzero_s
        self.reference['*:scregion_updateTasks'] = myzero_s
        self.reference['*:scregion_FindNeighbors'] = myzero_s
        self.reference['*:scregion_Density'] = myzero_s
        self.reference['*:scregion_EquationOfState'] = myzero_s
        self.reference['*:scregion_synchronizeHalos1'] = myzero_s
        self.reference['*:scregion_IAD'] = myzero_s
        self.reference['*:scregion_synchronizeHalos2'] = myzero_s
        self.reference['*:scregion_MomentumEnergyIAD'] = myzero_s
        self.reference['*:scregion_Timestep'] = myzero_s
        self.reference['*:scregion_UpdateQuantities'] = myzero_s
        self.reference['*:scregion_EnergyConservation'] = myzero_s
        self.reference['*:scregion_UpdateSmoothingLength'] = myzero_s
        self.reference['*:scregion_findNeighborsSfc'] = myzero_s
    # }}}
    # }}}
# }}}


# {{{ class SphExaCuda_Scalasca_Off_Check
@rfm.simple_test
class SphExaCuda_Scalasca_Off_Check(rfm.RegressionTest, hooks.setup_pe,
                                    hooks.setup_code):
    # weak scaling:
    steps = parameter([1])
    compute_node = parameter([1, 2, 4, 8, 16])
    np_per_c = parameter([5e6])
    scorep_flags = variable(bool, value=False)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = [
            'cdt-cuda', 'craype-accel-nvidia60', 'cudatoolkit', 'Scalasca']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'gpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.time_limit = '20m'
        self.executable = 'mpi+omp+cuda'
        self.target_executable = 'mpi+omp+cuda'
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
            f'which cube_remap2 >> {self.which_rpt}',
            f'which cube_dump >> {self.which_rpt}',
            f'which {self.cubetool} >> {self.which_rpt}',
            # f'which vampir >> {self.which_rpt}',
            f'scorep-info config-summary &> {self.info_rpt}',
            f'# step1: prepare executable with: scalasca -instrument (skin)',
            f'# step2: run executable with: scalasca -analyze (scan)',
            f'# step3: explore report with: scalasca -examine (square)',
            f'# step4: get calltree with: cube_calltree'
        ]
        # }}}

        # {{{ run
        self.variables = {
            # 'SCOREP_ENABLE_UNWINDING': 'true',
            # 'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
            # 'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
            'SCOREP_TOTAL_MEMORY': '1G',
            # 'SCOREP_TIMER': 'gettimeofday',
            'SCAN_ANALYZE_OPTS': '--time-correct',
        }
        self.rpt = 'rpt'
        self.rpt_score = 'scorep-score.rpt'
        self.rpt_exclusive = 'cube_calltree_exclusive.rpt'
        self.rpt_inclusive = 'cube_calltree_inclusive.rpt'
        #
        cubetree = 'cube_calltree -m time -p -t 1'
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
        ])
        # }}}

    # {{{ hooks
    # {{{ performance
    @run_before('performance')
    def set_tool_perf_patterns(self):
        self.perf_patterns = {}
        if self.perf_patterns:
            self.perf_patterns.update(perf_patterns)
        else:
            self.perf_patterns = perf_patterns
    # }}}
    # }}}
# }}}
