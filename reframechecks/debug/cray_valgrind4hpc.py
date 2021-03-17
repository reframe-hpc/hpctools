# Copyright 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.hooks as hooks
from reframe.core.backends import getlauncher


# {{{ class SphExaValgrind4hpcCheck
@rfm.simple_test
class SphExa_Valgrind4hpc_Check(rfm.RegressionTest, hooks.setup_pe,
                                hooks.setup_code):
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
    steps = parameter([0])  # overhead is high -> 0 is recommended
    compute_node = parameter([1])
    np_per_c = parameter([1e2])  # overhead is high -> small is recommended

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'cpeGNU'
            # 'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            # 'PrgEnv-aocc', 'cpeGNU', 'cpeIntel', 'cpeCray', 'cpeAMD',
        ]
        # NOTE: dom (slurm/20.11.4) is failing
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.tool = 'valgrind4hpc'
        self.modules = [self.tool]
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype', 'debugging'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.sourcepath = f'{self.testname}.cpp'
        # TODO: self.prgenv_flags = -O0
        self.executable = self.tool
        self.target_executable = './mpi+omp'
        # self.sourcepath = f'{self.testname}.cpp'
        # self.target_executable = f'./{self.testname}.exe'
        # self.postbuild_cmds = [f'mv {self.tool} {self.target_executable}']
        # }}}

        # {{{ run
        self.time_limit = '10m'
        self.variables = {
            'PKG_CONFIG_PATH':
                '$VALGRIND4HPC_INSTALL_DIR/lib/pkgconfig:$PKG_CONFIG_PATH',
        }
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prerun_cmds = [
            f'which {self.tool} &> {self.which_rpt}',
            f'srun --version > {self.version_rpt}',
            # f'{self.tool} --version >> {self.version_rpt}',
            f'pkg-config --variable=prefix valgrind >> {self.version_rpt}',
            f'echo VALGRIND4HPC_L=$VALGRIND4HPC_LEVEL >> {self.version_rpt}',
            f'grep PACKAGE_VERSION $VALGRIND4HPC_INSTALL_DIR/include/'
            f'valgrind/config.h >> {self.version_rpt}',
        ]
        # }}}

        # {{{ sanity
        sanity_1 = r'Conditional jump or move depends on uninitialised value'
        sanity_2 = r'Uninitialised value was created by a \S+ allocation'
        sanity_3 = r'All heap blocks were freed -- no leaks are possible'
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_found(sanity_1, self.stdout),
            sn.assert_found(sanity_2, self.stdout),
            # sn.assert_found(sanity_3, self.stdout),
        ])
        # }}}

        # {{{ performance
        # the tool flushes stdout hence we need this trick:
        self.time_rpt = 'time.rpt'
        self.rpt_dep = self.time_rpt
        self.prerun_cmds += [f'echo starttime=`date +%s` > {self.time_rpt}']
        self.postrun_cmds += [
            f'echo stoptime=`date +%s` >> {self.time_rpt}',
        ]
        # see common/sphexa/hooks.py
        # }}}
#         # {{{ perf_patterns:
#         basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
#         tool_perf_patterns = \
#           sn.evaluate(sphsvalgrind.vhpc_perf_patterns(self))
#         self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
#         # }}}
#         # {{{ reference:
#         self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
#         self.reference = sn.evaluate(sphsvalgrind.vhpc_tool_reference(self))
#         # }}}

    # {{{ hooks
    # {{{ set_launcher
    @rfm.run_before('run')
    def set_launcher(self):
        # The job launcher has to be changed because
        # the tool can be called without srun
        self.job.launcher = getlauncher('local')()
    # }}}

    # {{{ set_opts
    @rfm.run_before('run')
    def set_opts(self):
        self.tool_opts = (
            f' -n{self.num_tasks}'
            f' --valgrind-args="--track-origins=yes --leak-check=summary"'
            f' --from-ranks=0-0 '
            # f' --from-ranks=0-{self.num_tasks-1} '
            # f' --launcher-args=""'
        )
        self.executable_opts = [
            self.tool_opts, self.target_executable, '--',
        ]
    # }}}
    # }}}
# }}}
