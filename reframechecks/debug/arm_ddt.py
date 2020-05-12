# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.launchers import LauncherWrapper


@rfm.parameterized_test(*[[mpitask, steps]
                          for mpitask in [24]
                          for steps in [2]
                          ])
class SphExaDDTCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Arm Forge DDT (mpi),
    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks,
    :arg cubesize: set to small value as default,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpitask, steps):
        super().__init__()
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
        self.modules = ['ddt']
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
        # self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.executable = './%s.exe' % self.testname
        # make mpi ranks > 2 crash after second iteration:
        self.step_abort = 1
        insert_abort = (r'"/sph::computeMomentumAndEnergyIAD/a if (d.rank > 2 '
                        r'&& d.iteration > %s)'
                        r' { MPI::COMM_WORLD.Abort(0); }"' % self.step_abort)
        self.prebuild_cmd = [
            'module rm xalt',
            'sed -i %s %s' % (insert_abort, self.sourcepath),
        ]
        # }}}

        # {{{ run
        ompthread = 1
        cubesize = 35
        self.name = 'sphexa_ddt_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpitask, ompthread, cubesize, steps)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 24
        self.num_tasks_per_core = 2
        self.use_multithreading = True
        self.num_cpus_per_task = ompthread
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps, '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        # self.csv_rpt = 'csv.rpt'
        self.pre_run = [
            'module rm xalt',
            'ddt --version > %s' % self.version_rpt,
            'which ddt &> %s' % self.which_rpt,
        ]
        # use linux date as timer:
        self.pre_run += ['echo starttime=`date +%s`']
        self.htm_rpt = 'rpt_ddt.html'
        self.txt_rpt = 'rpt_ddt.txt'

        self.post_run = [
            'echo stoptime=`date +%s`',
            # htm2txt is the same as running with --output=rpt.txt, see hook
            'w3m -dump %s > %s' % (self.htm_rpt, self.txt_rpt),
        ]
        # }}}

        # {{{ sanity
        # --- "0-23  Add tracepoint for sqpatch.cpp:75"
        regex_addtp = r' 0-\d+\s+Add tracepoint for \S+:\d+'
        # --- "* number of processes : 24"
        regex_np = r'\* number of processes\s+:\s(?P<nprocs>\d+)'
        res_np = sn.extractsingle(regex_np, self.txt_rpt, 'nprocs', int)
        # --- "main(int,  domain.clist: std::vector of length 0, capacity 1786"
        regex_cap = r'\s+main\S+\s+domain\.clist:.*capacity\s+(?P<cap>\d+)'
        # --- tracepoints:
        #   Time      Tracepoint    Processes    Values
        #             main(int,
        # 1 0:05.479  char**)          0-23      from 0 to 19286
        regex_tpoint = r'0-\d+\s+from 0 to (?P<maxi>\d+)'
        rest = sn.count(sn.extractall(regex_tpoint, self.txt_rpt, 'maxi', int))
        # --- "3-23  MPI::Comm::Abort  virtual void Abort" = 21/24 core crashed
        regex_abort = r'^\s+(?P<rk0>\d+)-(?P<rkn>\d+)\s+MPI::Comm::Abort\s+'
        res_rk0 = sn.extractsingle(regex_abort, self.txt_rpt, 'rk0', int)
        res_rkn = sn.extractsingle(regex_abort, self.txt_rpt, 'rkn', int)
        res_rk = res_rkn - res_rk0 + 1

        self.sanity_patterns = sn.all([
            sn.assert_found(regex_addtp, self.txt_rpt),
            sn.assert_eq(self.num_tasks, res_np),
            sn.assert_found(regex_cap, self.txt_rpt),
            sn.assert_eq(self.step_abort + 2, rest),
            sn.assert_eq(self.num_tasks - 3, res_rk),
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        if self.current_environ.name == 'PrgEnv-cray':
            # cce<9.1 fails to compile with -g
            # self.modules = ['cdt/20.03']
            self.modules += ['cce/9.1.3']
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_after('setup')
    def set_launcher(self):
        linen = 75
        tracepoint = r'"%s:%d,domain.clist[0],domain.clist"' % \
                     (self.sourcepath, linen)
        # recommending tracepoint but this will work too:
        # --break-at %s:%d --evaluate="domain.clist;domain.clist[0]"
        self.ddt_options = ['--offline', '--output=%s' % self.htm_rpt,
                            '--trace-at', tracepoint]
        self.job.launcher = LauncherWrapper(self.job.launcher, 'ddt',
                                            self.ddt_options)
    # }}}
