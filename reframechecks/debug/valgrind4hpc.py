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
import sphexa.sanity_valgrind as sphsvalgrind
from reframe.core.backends import getlauncher


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [12]
cubeside_dict = {1: 10, 12: 20, 24: 30}
steps_dict = {1: 0, 12: 0, 24: 0}


# {{{ class SphExaValgrind4hpcCheck
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExaValgrind4hpcCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Cray valgrind4hpc
    : m time-n10
    :        JobID    JobName   NTasks ElapsedRaw      State
    : ------------ ---------- -------- ---------- ----------
    : 1112805      rfm_sphex+                  21  COMPLETED
    : 1112805.bat+      batch        1         21  COMPLETED
    : 1112805.ext+     extern        1         21  COMPLETED
    : 1112805.0    valgrind4+       12         15  COMPLETED
    : 1112805.1    cti_be_da+        1          8  COMPLETED
    : m time-n20
    :        JobID    JobName   NTasks ElapsedRaw      State
    : ------------ ---------- -------- ---------- ----------
    : 1112807      rfm_sphex+                  29  COMPLETED
    : 1112807.bat+      batch        1         29  COMPLETED
    : 1112807.ext+     extern        1         29  COMPLETED
    : 1112807.0    valgrind4+       12         24  COMPLETED
    : 1112807.1    cti_be_da+        1         18  COMPLETED
    : m time-n30
    :        JobID    JobName   NTasks ElapsedRaw      State
    : ------------ ---------- -------- ---------- ----------
    : 1112806      rfm_sphex+                  74  COMPLETED
    : 1112806.bat+      batch        1         74  COMPLETED
    : 1112806.ext+     extern        1         74  COMPLETED
    : 1112806.0    valgrind4+       12         68  COMPLETED
    : 1112806.1    cti_be_da+        1         61  COMPLETED
    '''
    # }}}

    def __init__(self, mpi_task):
        # super().__init__()
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
        self.tool = 'valgrind4hpc'
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-O0',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        tc_ver = '20.08'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}', self.tool],
            'PrgEnv-intel': [f'CrayIntel/.{tc_ver}', self.tool],
            'PrgEnv-cray': [f'CrayCCE/.{tc_ver}', self.tool],
            'PrgEnv-pgi': [f'CrayPGI/.{tc_ver}', self.tool],
        }
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = self.tool
        self.target_executable = f'./{self.testname}.exe'
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_valgrind4hpc_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps)
        self.num_tasks_per_node = 12
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'PKG_CONFIG_PATH':
                '$VALGRIND4HPC_INSTALL_DIR/lib/pkgconfig:$PKG_CONFIG_PATH',
        }
        self.tool_opts = (
            f' -n{self.num_tasks}'
            # f' --launcher-args=""'
            f' --valgrind-args="--track-origins=yes --leak-check=full"'
        )
        # valgrind4hpc -n32 --launcher-args="-N16 -j2"
        # --valgrind-args="--track-origins=yes --leak-check=full" ./a.out
        # -- arg1 arg2
        self.executable_opts = [
            self.tool_opts, self.target_executable,
            f'-- -n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            f'mv {self.executable} {self.target_executable}',
            f'echo $VALGRIND4HPC_VERSION > {self.version_rpt}',
            f'grep PACKAGE_VERSION $VALGRIND4HPC_INSTALL_DIR/include/'
            f'valgrind/config.h >> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        # }}}

        # {{{ sanity
        sanity_1 = r'Conditional jump or move depends on uninitialised value'
        sanity_2 = r'Uninitialised value was created by a heap allocation'
        sanity_3 = r'All heap blocks were freed -- no leaks are possible'
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_found(sanity_1, self.stdout),
            sn.assert_found(sanity_2, self.stdout),
            sn.assert_found(sanity_3, self.stdout),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.time_rpt = 'time.rpt'
        # the tool flushes stdout hence we need this trick:
        self.prerun_cmds += [f'echo starttime=`date +%s` > {self.time_rpt}']
        self.postrun_cmds += [
            f'echo stoptime=`date +%s` >> {self.time_rpt}',
            f'cat {self.time_rpt}']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphsvalgrind.vhpc_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        self.reference = sn.evaluate(sphsvalgrind.vhpc_tool_reference(self))
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_before('run')
    def set_launcher(self):
        # The job launcher has to be changed because
        # valgrind4hpc can not be called with srun
        self.job.launcher = getlauncher('local')()
    # }}}
# }}}
