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
import sphexa.sanity_mpip as sphsmpip


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {24: 100}
steps_dict = {24: 0}


@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaMpipCheck(sphsmpip.MpipBaseTest):
    # {{{
    '''
    This class runs the test code with mpiP, the light-weight MPI profiler (mpi
    only): http://llnl.github.io/mpiP

    2 parameters can be set for simulation:

    :arg mpi_task: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpi_task):
        # super().__init__()
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
        self.modules = ['mpiP']
        # unload xalt to avoid _buffer_decode error:
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        tool_ver = '57fc864'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'{self.modules[0]}/{tool_ver}-CrayGNU-{tc_ver}'],
            'PrgEnv-intel': [f'{self.modules[0]}/{tool_ver}-CrayIntel-'
                             f'{tc_ver}'],
            'PrgEnv-cray': [f'{self.modules[0]}/{tool_ver}-CrayCCE-{tc_ver}'],
            'PrgEnv-pgi': [f'{self.modules[0]}/{tool_ver}-CrayPGI-{tc_ver}'],
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
        self.executable = './%s.exe' % self.testname
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
        self.name = 'sphexa_mpiP_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps)
        self.num_tasks_per_node = 24
        self.num_tasks_per_core = 2
        self.use_multithreading = True
# {{{ ht:
        # self.num_tasks_per_node = mpitasks if mpitasks < 36 else 36   # noht
        # self.use_multithreading = False  # noht
        # self.num_tasks_per_core = 1      # noht

        # self.num_tasks_per_node = mpitasks if mpitasks < 72 else 72
        # self.use_multithreading = True # ht
        # self.num_tasks_per_core = 2    # ht
# }}}
        self.num_cpus_per_task = ompthread
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            # 'MPIP': '"-c"',
        }
        self.executable_opts = [f'-n {self.cubeside}', f'-s {self.steps}',
                                '2>&1']
        self.prerun_cmds = [
            'module rm xalt',
        ]
        # }}}

        # {{{ sanity_patterns
        # set externally (in sanity_mpip.py)
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.build_system.ldflags = self.build_system.cxxflags + \
            ['-L$EBROOTMPIP/lib', '-Wl,--whole-archive -lmpiP',
             '-Wl,--no-whole-archive -lunwind', '-lbfd -liberty -ldl -lz']
    # }}}
