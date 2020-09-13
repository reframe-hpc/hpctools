# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
tools = ['memcheck', 'racecheck', 'initcheck', 'synccheck']


@rfm.parameterized_test(*[[mpitask, cubesize, steps, memtool]
                          for mpitask in [1]
                          for cubesize in [30]
                          for steps in [0]
                          for memtool in tools
                          ])
class SphExaCudaMemCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with cuda-memcheck tools:
    https://docs.nvidia.com/cuda/cuda-memcheck/index.html#cuda-memcheck-tools
    '''
    # }}}

    def __init__(self, mpitask, cubesize, steps, memtool):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'debug', 'gpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.prebuild_cmds = ['module rm xalt']
        self.modules = ['craype-accel-nvidia60']
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-std=c++14', '-g', '-O0', '-DNDEBUG'],
            # Makefile adds: '-DUSE_MPI', '-DUSE_CUDA'],
        }
        self.prgenv_gpuflags = {
            # P100 = sm_60
            'PrgEnv-gnu': ['-std=c++14', '-rdc=true', '-arch=sm_60', '-g',
                           '-G', '--expt-relaxed-constexpr']
        }
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.sourcesdir = 'src_cuda'
        self.build_system.nvcc = 'nvcc -g -G'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2
        self.tool = 'cuda-memcheck'
        self.executable = self.tool
        self.target_executable = 'mpi+omp+cuda'
        self.postbuild_cmds = [f'mv {self.target_executable}.app '
                               f'{self.target_executable}']
        # }}}

        # {{{ run
        ompthread = 1
        self.cubesize = cubesize
        self.memtool = memtool
        self.name = \
            'sphexa_cudamem_{}_{:03d}mpi_{:03d}omp_{}n_{}steps_{}'.format(
                self.testname, mpitask, ompthread, cubesize, steps, memtool)
        self.num_tasks = mpitask
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
        self.executable_opts = [
            f'--tool {memtool}', self.target_executable, f'-n {cubesize}',
            f'-s {steps}'
        ]
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            '%s -V &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
        ]
        # }}}

    # {{{ self.sanity_patterns:
    @rfm.run_before('sanity')
    def set_sanity_gpu(self):
        # {{{ --- sanity_patterns:
        if self.memtool not in 'racecheck':
            regex = r'========= ERROR SUMMARY: 0 errors'
        else:
            regex = r'RACECHECK SUMMARY: 0 hazards displayed'
        self.sanity_patterns = sn.all([
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_found(regex, self.stdout),
        ])
        # }}}
    # }}}

    # {{{ set_sanity hook: compiler flags
    @rfm.run_before('compile')
    def set_flags(self):
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.nvccflags = \
            self.prgenv_gpuflags[self.current_environ.name]
        if self.current_system.name in ['dom', 'daint']:
            cap = 'sm_60'
        self.build_system.options = [
            self.target_executable, 'SRCDIR=.', 'BUILDDIR=.',
            'BINDIR=.', 'NVCCFLAGS="%s"' % " ".join(self.nvccflags),
            'NVCCARCH=%s' % cap, 'CUDA_PATH=$CUDA_PATH',
            'MPICXX=%s' % self.build_system.cxx]
    # }}}
