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

# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {24: 100}
steps_dict = {24: 4}
cycles_dict = {24: 5000000}


@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaScorepProfilingCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Score-P (mpi only):

    3 parameters can be set for simulation:

    :arg mpi_task: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.
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
        self.tool = 'scorep'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        tool_ver = '6.0'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'Score-P/{tool_ver}-CrayGNU-{tc_ver}'],
            'PrgEnv-intel': [f'Score-P/{tool_ver}-CrayIntel-{tc_ver}'],
            'PrgEnv-cray': [f'Score-P/{tool_ver}-CrayCCE-{tc_ver}'],
            'PrgEnv-pgi': [f'Score-P/{tool_ver}-CrayPGI-{tc_ver}'],
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
            'sphexa_scorepS+P_{}_{:03d}mpi_{:03d}omp_{}n_{}steps_{}cycles'. \
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
            'SCOREP_ENABLE_PROFILING': 'true',
            'SCOREP_ENABLE_TRACING': 'false',
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
            # 'SCOREP_TOTAL_MEMORY': '1G',
        }
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.info_rpt = 'info.rpt'
        self.rpt = 'rpt'
        self.rpt_inclusive = '%s.inclusive' % self.rpt
        self.rpt_exclusive = '%s.exclusive' % self.rpt
        self.executable_opts = [
            f'-n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            'scorep-info config-summary &> %s' % self.info_rpt,
        ]
        cubetree = 'cube_calltree -m time -p -t 1'
        # -m metricname -- print out values for the metric <metricname>
        # -i            -- calculate inclusive values instead of exclusive
        # -t treshold   -- print out only call path with a value larger
        #                  than <treshold>%
        # -p            -- diplay percent value
        self.postrun_cmds = [
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
            sn.assert_true(sphsscorep.scorep_version(self)),
            sn.assert_true(sphsscorep.scorep_info_papi_support(self)),
            sn.assert_true(sphsscorep.scorep_info_perf_support(self)),
            sn.assert_true(sphsscorep.scorep_info_unwinding_support(self)),
            # check the summary report:
            sn.assert_found(r'Estimated aggregate size of event trace',
                            self.rpt)
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # tool
        self.perf_patterns.update({
            'scorep_elapsed': sphsscorep.scorep_elapsed(self),
            '%scorep_USR': sphsscorep.scorep_usr_pct(self),
            '%scorep_MPI': sphsscorep.scorep_mpi_pct(self),
            'scorep_top1': sphsscorep.scorep_top1_pct(self),
            '%scorep_Energy_exclusive':
            sphsscorep.scorep_exclusivepct_energy(self),
            '%scorep_Energy_inclusive':
            sphsscorep.scorep_inclusivepct_energy(self),
        })
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool:
        self.reference['*:scorep_elapsed'] = (0, None, None, 's')
        self.reference['*:%scorep_USR'] = (0, None, None, '%')
        self.reference['*:%scorep_MPI'] = (0, None, None, '%')
        top1_name = sphsscorep.scorep_top1_name(self)
        # TODO: self.reference['*:scorep_top1'] = (0, None, None, top1_name)
        self.reference['*:scorep_top1'] = (0, None, None, '')
        self.reference['*:%scorep_Energy_exclusive'] = (0, None, None, '%')
        self.reference['*:%scorep_Energy_inclusive'] = (0, None, None, '%')
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
    # }}}

    # TODO:
    # def setup(self, partition, environ, **job_opts):
    #     super().setup(partition, environ, **job_opts)
    #     partitiontype = partition.fullname.split(':')[1]
    #     if partitiontype == 'gpu':
    #         self.job.options = ['--constraint="gpu&perf"']
    #     elif partitiontype == 'mc':
    #         self.job.options = ['--constraint="mc&perf"']
