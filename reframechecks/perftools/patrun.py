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
import sphexa.sanity_perftools as sphsperft


# NOTE: jenkins restricted to 1 cnode but this check needs 2
mpi_tasks = [48]
cubeside_dict = {24: 100, 48: 125}
steps_dict = {24: 5, 48: 5}


# {{{ class SphExaPatRunCheck
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaPatRunCheck(sphsperft.PerftoolsBaseTest):
    # {{{
    '''This class runs the test code with CrayPAT (Cray Performance Measurement
    and Analysis toolset):

        * https://pubs.cray.com (Cray Perftools)
        * man pat_run
        * man intro_craypat
        * ``pat_help``

    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.

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
        self.tags = {'sph', 'hpctools', 'cpu', 'latestpe'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.modules = ['perftools-preload']
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
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
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}'],
            'PrgEnv-intel': [f'CrayIntel/.{tc_ver}'],
            'PrgEnv-cray': [f'CrayCCE/.{tc_ver}'],
            'PrgEnv-pgi': [f'CrayPGI/.{tc_ver}'],
        }
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'CC'
        self.sourcepath = f'{self.testname}.cpp'
        self.target_executable = f'./{self.testname}.exe'
        self.tool = 'pat_run'
        self.executable = self.tool
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_patrun_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
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
        # -r: generate a report upon successful execution
        # TODO: use rpt-files/RUNTIME.rpt
        self.executable_opts = ['-r', self.target_executable,
                                f"-n {self.cubeside}", f"-s {self.steps}",
                                '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.csv_rpt = 'csv.rpt'
        # needed for sanity functions:
        self.rpt = 'rpt'
        csv_options = ('-v -O load_balance_group -s sort_by_pe=\'yes\' '
                       '-s show_data=\'csv\' -s pe=\'ALL\'')
        self.prerun_cmds = [
            'module rm xalt',
            f'mv {self.executable} {self.target_executable}',
            f'{self.tool} -V &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            # 'rm -fr $HOME/.craypat/*',
        ]
        self.postrun_cmds += [
            # patrun_num_of_compute_nodes
            f'ls -1 {self.target_executable}+*s/xf-files/',
            f'cp *_job.out {self.rpt}',
            f'pat_report {csv_options} %s+*s/index.ap2 &> %s' %
            (self.target_executable, self.csv_rpt)
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns_l = [
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout)
        ]
        # will also silently call patrun_version (in sanity_perftools.py)
        self.sanity_patterns = sn.all(self.sanity_patterns_l)
        # }}}

        # {{{ performance (see sanity.py)
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

#     @rfm.run_before('sanity')
#     def cp_stdout(self):
#         self.postrun_cmds = ['cp *_job.out %s' % self.rpt]
    # }}}
# }}}
