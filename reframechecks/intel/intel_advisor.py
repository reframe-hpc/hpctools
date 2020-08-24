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
import sphexa.sanity_intel as sphsintel


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {24: 100}
steps_dict = {24: 0}


@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaIntelAdvisorCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Intel Advisor (mpi only):
    https://software.intel.com/en-us/advisor

    Available analysis types are: ``advixe-cl -h collect``

    .. code-block:: none

      survey       - Discover efficient vectorization and/or threading
      dependencies - Identify and explore loop-carried dependencies for loops
      map          - Identify and explore complex memory accesses
      roofline     - Run the Survey analysis + Trip Counts & FLOP analysis
      suitability  - Check predicted parallel performance
      tripcounts   - Identify the number of loop iterations.

    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.

    Typical performance reporting:

    .. code-block:: none

      PERFORMANCE REPORT
      --------------------------------------------------
      sphexa_inspector_sqpatch_024mpi_001omp_100n_0steps
      - dom:gpu
         - PrgEnv-gnu
            * num_tasks: 24
            * Elapsed: 3.6147 s
            ...
            * advisor_elapsed: 2.13 s
            * advisor_loop1_line: 94 (momentumAndEnergyIAD.hpp)
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
        self.tool = 'advixe-cl'
        self.modules = ['advisor']
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.tool_v = '2020_update2'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}',
                           f'{self.modules[0]}/{self.tool_v}'],
            'PrgEnv-intel': [f'CrayIntel/.{tc_ver}',
                             f'{self.modules[0]}/{self.tool_v}'],
            'PrgEnv-cray': [f'CrayCCE/.{tc_ver}',
                            f'{self.modules[0]}/{self.tool_v}'],
            'PrgEnv-pgi': [f'CrayPGI/.{tc_ver}',
                           f'{self.modules[0]}/{self.tool_v}'],
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
        # self.build_system.cxx = 'CC'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = self.tool
        self.target_executable = f'./{self.testname}.exe'
        self.postbuild_cmds = [f'mv {self.tool} {self.target_executable}']
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_advisor_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
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
            # to avoid core when reporting (venv/jenkins):
            'LANG': 'C',
            'LC_ALL': 'C',
        }
        self.dir_rpt = 'rpt'
        self.tool_opts = '--collect=survey --search-dir src:rp=. ' \
                         '--data-limit=0 --no-auto-finalize --trace-mpi ' \
                         '--project-dir=%s -- ' % self.dir_rpt
        self.executable_opts = [self.tool_opts, self.target_executable,
                                f'-n {self.cubeside}', f'-s {self.steps}',
                                '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.summary_rpt = 'summary.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version >> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        self.postrun_cmds = [
            f'cd {self.dir_rpt} ;ln -s nid?????.000 e000 ;cd -',
            f'{self.tool} --report=survey --project-dir={self.dir_rpt} '
            f'&> {self.summary_rpt}',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version:
            sn.assert_true(sphsintel.advisor_version(self)),
            # check the summary report:
            sn.assert_found(r'advixe: This data has been saved',
                            self.summary_rpt),
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
            'advisor_elapsed': sphsintel.advisor_elapsed(self),
            'advisor_loop1_line': sphsintel.advisor_loop1_line(self),
        })
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool:
        self.reference['*:advisor_elapsed'] = (0, None, None, 's')
        # TODO: fix loop1_fname to avoid error with --report-file:
        # "Object of type '_DeferredExpression' is not JSON serializable"
        # loop1_fname = sphsintel.advisor_loop1_filename(self)
        loop1_fname = ''
        self.reference['*:advisor_loop1_line'] = (0, None, None, loop1_fname)
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
    # }}}
