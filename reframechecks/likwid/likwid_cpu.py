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
import sphexa.sanity_likwid as sphslikwid


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [1]
cubeside_dict = {1: 35}
steps_dict = {1: 5}


@rfm.parameterized_test(*[[mpi_task, group]
                          for mpi_task in mpi_tasks
                          for group in ['TMA', 'MEM', 'CLOCK']
                          # for group in ['MEM']
                          ])
class SphExaLikwidCpuCheck(sphslikwid.LikwidBaseTest):
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

    def __init__(self, mpi_task, group):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel',
                                    'PrgEnv-cray', 'PrgEnv-pgi']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.modules = ['likwid']
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.tool = 'likwid-perfctr'
        self.tool_v = '1d6636c'
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
        self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.executable = self.tool
        self.target_executable = './%s.exe' % self.testname
# {{{ openmp:
# 'PrgEnv-intel': ['-qopenmp'],
# 'PrgEnv-gnu': ['-fopenmp'],
# 'PrgEnv-pgi': ['-mp'],
# 'PrgEnv-cray_classic': ['-homp'],
# 'PrgEnv-cray': ['-fopenmp'],
# # '-homp' if lang == 'F90' else '-fopenmp',
# }}}
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.group = group
        self.name = 'sphexa_likwid_{}_{:03d}mpi_{:03d}omp_{}n_{}steps_{}'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps, group)
        self.num_tasks_per_node = 1
        self.num_tasks_per_core = 1
        self.use_multithreading = False
# {{{ ht:
        # self.num_tasks_per_node = mpitask if mpitask < 36 else 36   # noht
        # self.use_multithreading = False  # noht
        # self.num_tasks_per_core = 1      # noht

        # self.num_tasks_per_node = mpitask if mpitask < 72 else 72
        # self.use_multithreading = True # ht
        # self.num_tasks_per_core = 2    # ht
# }}}
        self.num_cpus_per_task = ompthread
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        # -Cgpu,perf -n1 -t1 likwid-perfctr -C 0 -g MEM (-m) ./streamGCC
        # -r: generate a report upon successful execution
        # TODO: use rpt-files/RUNTIME.rpt
        # self.executable_opts = ['-C 0', '-g MEM', '-g CLOCK', '-g TMA',
        self.executable_opts = ['-C 0', '-g %s' % group,
                                self.target_executable, f'-n {self.cubeside}',
                                f'-s {self.steps}', '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        # TODO: likwid-perfctr -g $g -H
        self.prerun_cmds = [
            'module rm xalt',
            f'mv {self.executable} {self.target_executable}',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        # }}}

        # {{{ sanity
        # sanity_patterns is set externally (in sanity_likwid.py)
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # tool perf_patterns is set externally (in sanity_likwid.py)
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool reference is set externally (in sanity_likwid.py)
# }}}
    # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_before('run')
    def set_constraint(self):
        partitiontype = self.current_partition.fullname.split(':')[1]
        self.job.options = [f'--constraint="{partitiontype}&perf"']
    # }}}
