# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.parameterized_test(*[[mpitask, steps]
                          for mpitask in [24]
                          for steps in [1]
                          ])
class SphExaATPCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with cray-atp (mpi),
    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks,
    :arg cubesize: set to 50 as default,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpitask, steps):
        super().__init__()
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi',
                                    'PrgEnv-cray', 'PrgEnv-cray_classic']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.modules = ['atp', 'stat']
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        self.build_system = 'SingleSource'
        # self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.executable = './%s.exe' % self.testname
        insert_abort = (r'"/sph::computeMomentumAndEnergyIAD/a if (d.rank > 2)'
                        r' { MPI::COMM_WORLD.Abort(0); }"')
        self.ini = '/opt/cray/elogin/eproxy/etc/eproxy.ini'
        self.cfg = '/opt/cray/elogin/eproxy/default/bin/eproxy_config.py'
        self.rpt_cfg = 'rpt.eproxy'
        self.prebuild_cmd = [
            'module rm xalt',
            'sed -i %s %s' % (insert_abort, self.sourcepath),
            # not strictly needed for atp but keeping as reminder:
            # --- check eproxy.ini (slurm = True):
            'grep ^slurm %s > %s' % (self.ini, self.rpt_cfg),
            # --- check eproxy_config.py:
            # ['debug', 'ps', None, False],
            'grep "\'ps\'," %s >> %s' % (self.cfg, self.rpt_cfg),
            # ['eproxy', 'eproxy', None, True],
            'grep "\'eproxy\'," %s >> %s' % (self.cfg, self.rpt_cfg),
            # --- check STAT_MOM_NODE (daintgw01|domgw03)
            'grep login /etc/hosts >> %s' % self.rpt_cfg
        ]
        # }}}

        # {{{ run
        ompthread = 1
        cubesize = 50
        self.name = 'sphexa_atp_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
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
            'ATP_ENABLED': '1',
        }
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps, '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.csv_rpt = 'csv.rpt'
        self.pre_run = [
            'module rm xalt',
            'stat --version > %s' % self.version_rpt,
            'pkg-config --modversion AtpSigHandler >> %s' % self.version_rpt,
            'pkg-config --variable=atp_libdir AtpSigHandler &> %s' %
            self.which_rpt,
        ]
        # use linux date as timer:
        self.pre_run += ['echo starttime=`date +%s`']
        self.rpt_rkn = 'rpt.rkn'
        self.rpt_rk0 = 'rpt.rk0'
        gdb_command = (r'-e %s '
                       r'--eval-command="set pagination off" '
                       r'--eval-command="bt" '
                       r'--eval-command="quit"' % self.executable)
        regex_not_rk0 = r'grep -m1 -v "\.0\."'
        self.post_run = [
            'echo stoptime=`date +%s`',
            # --- rank 0: MPI_Allreduce
            'gdb -c core.atp.*.%s.* %s &> %s' % (0, gdb_command, self.rpt_rk0),
            # --- rank>2: MPI::Comm::Abort
            'ln -s `ls -1 core.atp.* |%s` mycore' % regex_not_rk0,
            'gdb -c mycore %s &> %s' % (gdb_command, self.rpt_rkn),
            # can't do this because core filename is unknown at runtime:
            # 'gdb -c core.atp.*.%s.* -e %s' % (self.core, self.executable),
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            sn.assert_found(r'^slurm = True', self.rpt_cfg),
            sn.assert_found(r'\[.debug., .ps., None, False\],', self.rpt_cfg),
            sn.assert_found(r'\[.eproxy., .eproxy., None, True', self.rpt_cfg),
            sn.assert_found(r'login', self.rpt_cfg),
            # Forcing core dumps of ranks 1743, 0
            sn.assert_found(r'^Forcing core dumps of ranks \d+', self.stdout),
            sn.assert_found(r'with: stat-view atpMergedBT\.dot', self.stdout),
            sn.assert_found(r'MPI_Allreduce', self.rpt_rk0),
            sn.assert_found(r'MPI_Abort', self.rpt_rkn),
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_before('sanity')
    def get_core_filename(self):
        '''
        Retrieving core filenames for postprocessing with gdb:

        .. code-block:: none

           Forcing core dumps of ranks 21, 0
           core.atp.1010894.0.8826
           core.atp.1010894.21.8847
        '''
        self.core = sn.extractsingle(
            r'^Forcing core dumps of ranks (?P<corefile>\d+),', self.stdout,
            'corefile', str)
    # }}}
