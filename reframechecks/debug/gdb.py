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
# import sphexa.sanity as sphs


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [1]
cubeside_dict = {1: 15}
steps_dict = {1: 0}


# {{{ class SphExaGDBCheck
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExaGDBCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with gdb (serial),
    3 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks,
    :arg cubesize: size of the cube in the 3D square patch test,
    :arg steps: number of simulation steps.
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
        self.tags = {'sph', 'hpctools', 'debug'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}'],
            'PrgEnv-intel': [f'CrayIntel/.{tc_ver}'],
            'PrgEnv-cray': [f'CrayCCE/.{tc_ver}'],
            'PrgEnv-pgi': [f'CrayPGI/.{tc_ver}'],
        }
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
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.target_executable = f'./{self.testname}.exe'
        self.executable = 'gdb'
        self.prebuild_cmds = ['module rm xalt', 'module list -t',
                              'ln -s GDB/* .']
        self.postbuild_cmds = [
            f'mv {self.executable} {self.target_executable}',
        ]
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_gdb_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '5m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.tool_input = 'gdb.input'
        tool_init = 'gdbinit'
        self.prerun_cmds = [
            'module rm xalt',
            f'sed -i -e "s@-s 0@-s {self.steps}@" '
            f'-e "s@-n 15@-n {self.cubeside}@" {self.tool_input}',
        ]
        self.executable_opts = ['--nh', '--init-command ./%s' % tool_init,
                                '--batch', '--command=./%s' % self.tool_input,
                                self.target_executable]
    # }}}

    # {{{ hooks:
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_before('run')
    def set_sanity_pgi(self):
        if self.current_environ.name == 'PrgEnv-pgi':
            regex = r'sed -ie "s-print domain.clist\[1\]-print domain.clist-"'
            self.prerun_cmds += ['%s %s' % (regex, self.tool_input)]
            pretty_printer_regex = \
                r'^\s+members of std::_Vector_base::_Vector_impl: $'
            pvector_type_regex = r'^Element type = int \*'
        else:
            pretty_printer_regex = \
                r'^\$1 = std::vector of length \d+, capacity \d+ = {0,'
            pvector_type_regex = r'^Element type = std::_Vector_base<'

        pvector_regex = \
            r'^elem\[2\]: \$3 = 2\n^elem\[3\]: \$4 = 3\n^elem\[4\]: \$5 = 4$'
        self.sanity_patterns = sn.all([
            # --- check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # --- check the tool output:
            #     -> 'print domain.clist[1]'
            #   $1 = std::vector of length 3375, capacity 3375 = {0, ...
            #   OR
            #   pgi: members of std::_Vector_base::_Vector_impl: ...
            sn.assert_found(pretty_printer_regex, self.stdout),
            #
            # --- check the tool output (pvector):
            #     -> 'pvector domain.clist 2 4'
            #   elem[2]: $3 = 2
            #   elem[3]: $4 = 3
            #   elem[4]: $5 = 4
            sn.assert_found(pvector_regex, self.stdout),
            #
            # --- check the tool output (pvector size/capacity/type):
            #     -> 'pvector domain.clist 2 4'
            #   Vector size = 3375
            #   Vector capacity = 3375
            sn.assert_found(r'^Vector size = \d+\nVector capacity = \d+',
                            self.stdout),
            #
            # --- check the tool output (std::):
            #     -> 'pvector domain.clist 2 4'
            #   Element type = std::_Vector_base<int, std::allocator<int> >...
            #   pgi -> Element type = int *
            sn.assert_found(pvector_type_regex, self.stdout),
            # check the tool output (quit):
            sn.assert_found(r'[Inferior 1 (process \d+) exited normally]',
                            self.stdout),
        ])
    # }}}
# }}}
