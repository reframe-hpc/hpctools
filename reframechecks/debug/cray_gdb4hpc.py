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
# mpi_tasks = [12, 24, 48, 240]
mpi_tasks = [12]
cubeside_dict = {1: 10, 12: 20, 24: 30, 48: 36, 240: 62}
steps_dict = {1: 1, 12: 1, 24: 1, 48: 1, 240: 1}


# {{{ class SphExaGdb4hpcCheck
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExaGdb4hpcCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Cray gdb4hpc
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
        self.tool = 'gdb4hpc'
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
        self.postbuild_cmds = [f'mv {self.tool} {self.target_executable}']
        # }}}

        # {{{ run
        ompthread = 1
        # gdb4hpc will launch the parallel job
        self.num_tasks = 1
        self.mpi_task = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_gdb4hpc_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
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
        }
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.gdb_slm = './gdb4hpc.slm'
        self.gdb_dir = 'GDB4HPC'
        self.gdb_in = 'gdb4hpc.in'
        self.gdb_rpt = './gdb4hpc.rpt'
        self.executable_opts = [f'-b {self.gdb_in}']
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version >> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            'echo starttime=`date +%s`',
            '# Everything between the "#cray_debug" lines will be ignored',
            '#cray_debug_start',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Shutting down debugger and killing application',
                            self.stdout),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.postrun_cmds += [
            '#cray_debug_stop',
            'echo stoptime=`date +%s`',
        ]
        # }}}

        # {{{ perf_patterns:
        # basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # tool_perf_patterns = sn.evaluate(sphsgdb4hpc.perf_patterns(self))
        # self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        #   {{{ reference:
        # self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # self.reference = sn.evaluate(sphsgdb4hpc.tool_reference(self))
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_before('run')
    def set_tool_commands(self):
        # create self.gdb_in:
        debug_commands = (
            f'sed -e "s@AA@{self.mpi_task}@" '
            f'-e "s@BB@{self.target_executable}@" '
            f'-e "s@CC@{self.gdb_slm}@" '
            f'-e "s@DD@-s {self.steps} -n {self.cubeside}@" '
            f'{self.gdb_dir}/{self.gdb_in}'
            f' > {self.gdb_in}'
        )
        self.prerun_cmds += [debug_commands]

    @rfm.run_before('run')
    def set_tool_jobscript(self):
        self.prerun_cmds += [
            # create self.gdb_slm:
            f'egrep -v "^gdb4hpc|egrep|^mv|^which|^sed" '
            f'{self.job.script_filename} '
            f'|sed "s@--ntasks=1@--ntasks={self.mpi_task}@" &> {self.gdb_slm}',
        ]

    @rfm.run_before('run')
    def set_launcher(self):
        # The job launcher has to be changed because
        # the tool can be called without srun
        self.job.launcher = getlauncher('local')()
    # }}}
# }}}
