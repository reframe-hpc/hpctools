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
# NOTE: 3 steps minimum to avoid "delay timeout" error + cubeside >= 40
mpi_tasks = [2]
cubeside_dict = {2: 80, 20: 172}
steps_dict = {2: 3, 20: 3}
# cycles_dict = {2: 5000000}


# {{{ SphExaScorepCudaCheck
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaScorepCudaCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Score-P (mpi+cuda):

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
    '''
    # }}}

    def __init__(self, mpi_task):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'gpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.tool = 'scorep'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        tool_ver = '6.0'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'Score-P/{tool_ver}-CrayGNU-{tc_ver}-cuda'],
        }
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.build_system.nvcc = 'nvcc'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'./{self.testname}.exe'
        self.target_executable = 'mpi+omp+cuda'
        self.build_system.cxx = 'scorep --mpp=mpi --cuda --nocompiler CC'
        self.build_system.nvcc = 'scorep --cuda --nocompiler nvcc'
        self.build_system.options = [
            self.target_executable, f'MPICXX="{self.build_system.cxx}"',
            'SRCDIR=.', 'BUILDDIR=.', 'BINDIR=.', 'CXXFLAGS=-std=c++14',
            'CUDA_PATH=$CUDATOOLKIT_HOME',
            # The makefile adds -DUSE_MPI
        ]
        self.postbuild_cmds = [f'mv {self.target_executable}.app '
                               f'{self.executable}']
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        # cycles = cycles_dict[mpi_task]
        self.name = \
            'sphexa_scorep+cuda_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps)
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'SCOREP_ENABLE_PROFILING': 'false',
            'SCOREP_ENABLE_TRACING': 'true',
            'SCOREP_CUDA_ENABLE': 'yes',
            'SCOREP_ENABLE_UNWINDING': 'true',
            # 'SCOREP_SAMPLING_EVENTS': 'perf_cycles@%s' % cycles,
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
        self.executable_opts = [
            f'-n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            'scorep-info config-summary &> %s' % self.info_rpt,
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
            sn.assert_true(sphsscorep.scorep_info_cuda_support(self)),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
    # }}}
