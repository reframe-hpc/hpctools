# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.launchers import LauncherWrapper


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [1]
cubeside_dict = {1: 30}
steps_dict = {1: 0}


# {{{ class SphExaCudaDDTCheck
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaCudaDDTCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Arm Forge DDT (cuda+mpi),
    3 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks,
    :arg cubeside: set to small value as default,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpi_task):
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
        self.tool = 'ddt'
        # self.tool_v = '20.1.1-Suse-15.0'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}'],
        }
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.sourcesdir = 'src_cuda'
        self.build_system.nvcc = 'nvcc'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2

        self.executable = 'mpi+omp+cuda'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.postbuild_cmds = [f'mv {self.executable}.app {self.executable}']
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_cudaddt_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
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
        self.executable_opts = [
            f'-n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            # use linux date as timer:
            'echo starttime=`date +%s`',
        ]
        self.htm_rpt = 'rpt_tool.html'
        self.txt_rpt = 'rpt_tool.txt'
        self.postrun_cmds = [
            'echo stoptime=`date +%s`',
            # htm2txt is the same as running with --output=rpt.txt, see hook
            'w3m -dump %s > %s' % (self.htm_rpt, self.txt_rpt),
        ]
        # }}}

        # {{{ sanity
        # --- Looking for: 'Add tracepoint for cudaDensity.cu:26'
        regex_addtp = r' Add tracepoint for \S+:\d+'
        # --- Looking for tracepoints:
        # 5 0:26.423 const*, int const*, int const*,     0  ...
        #   ... clist[27000-1]@3: {[0] = 26999, [1] = 0, [2] = 0}
        regex_tpoint = (r'clist\[(?P<np>\d+)-1]@3: {\[0\] = (?P<last>\d+), '
                        r'\[1\] = (?P<out>\d+),')
        res_tp_np = sn.extractsingle(regex_tpoint, self.txt_rpt, 'np', int)
        res_tp_last = sn.extractsingle(regex_tpoint, self.txt_rpt, 'last', int)
        res_tp_out = sn.extractsingle(regex_tpoint, self.txt_rpt, 'out', int)
        self.sanity_patterns = sn.all([
            sn.assert_found(regex_addtp, self.txt_rpt),
            sn.assert_eq(res_tp_np, self.cubeside**3),
            sn.assert_eq(res_tp_last, self.cubeside**3 - 1),
            sn.assert_eq(res_tp_out, 0),
        ])
        # }}}

    # {{{ compile hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        '''
        Sets compilation flags for debugging (cpu and gpu)
        '''
        self.prgenv_cpuflags = {
            'PrgEnv-gnu': ['-std=c++14', '-g', '-O0', '-DNDEBUG'],
            # Makefile adds: '-DUSE_MPI', '-DUSE_CUDA'],
        }
        self.build_system.cxxflags = \
            self.prgenv_cpuflags[self.current_environ.name]
        if self.current_system.name in ['dom', 'daint']:
            cap = 'sm_60',  # P100
            self.modules += ['craype-accel-nvidia60', 'ddt']
            self.variables['ALLINEA_FORCE_CUDA_VERSION'] = '10.1'
            prgenv_gpuflags = {
                'PrgEnv-gnu': ['-std=c++14', '-rdc=true', '-arch=%s' % cap,
                               '-g', '-G', '--expt-relaxed-constexpr']
            }
        else:
            cap = 'sm_70'  # V100
            self.modules = ['craype-accel-nvidia70', 'allinea-forge']
            prgenv_gpuflags = {
                'PrgEnv-gnu': ['-std=c++14', '-rdc=true', '-arch=%s' % cap,
                               '-g', '-G', '--expt-relaxed-constexpr']
            }

        self.prgenv_gpuflags = prgenv_gpuflags[self.current_environ.name]
        self.build_system.options = [
            self.executable, 'SRCDIR=.', 'BUILDDIR=.',
            'BINDIR=.', 'NVCCFLAGS="%s"' % " ".join(self.prgenv_gpuflags),
            'NVCCARCH=%s' % cap, 'CUDA_PATH=$CUDA_PATH',
            'MPICXX=%s' % self.build_system.cxx]
    # }}}

    # {{{ launcher hooks
    @rfm.run_after('setup')
    def set_launcher(self):
        '''
        Sets tracepoint for offline debugging
        '''
        srcfile = 'include/sph/cuda/cudaDensity.cu'
        linen = 26
        # by default, cuda kernels are logged (slow), tracepoints are optionals
        tracepoint = r'"%s:%d,clist[%d-1]@3,clist"' % \
                     (srcfile, linen, self.cubeside**3)
        # recommending tracepoint but this will work too:
        # --break-at %s:%d --evaluate="domain.clist;domain.clist[0]"
        self.tool_options = ['--offline', '--output=%s' % self.htm_rpt,
                             '--trace-at', tracepoint, '--cuda',
                             '--openmp-threads=%s' % self.num_cpus_per_task]
        self.job.launcher = LauncherWrapper(self.job.launcher, self.tool,
                                            self.tool_options)
    # }}}

    # {{{ performance hook
    @rfm.run_before('performance')
    def elapsed_time_from_date(self):
        '''Reports elapsed time in seconds using the linux date command:

        .. code-block::

         starttime=1579725956
         stoptime=1579725961
         reports: elapsed: 5 s
        '''
        regex_start_sec = r'^starttime=(?P<sec>\d+)'
        regex_stop_sec = r'^stoptime=(?P<sec>\d+)'
        start_sec = sn.extractsingle(regex_start_sec, self.stdout, 'sec', int)
        stop_sec = sn.extractsingle(regex_stop_sec, self.stdout, 'sec', int)
        res = stop_sec - start_sec
        self.perf_patterns = {
            'elapsed': res,
        }
        self.reference = {
            '*': {
                'elapsed': (0, None, None, 's'),
            }
        }
    # }}}
