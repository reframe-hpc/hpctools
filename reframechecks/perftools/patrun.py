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


@rfm.parameterized_test(*[[mpitask, steps]
                          for mpitask in [48]
                          for steps in [1]
                          # for mpitask in [24, 48, 96]
                          # for steps in [4]
                          ])
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

    def __init__(self, mpitask, steps):
        super().__init__()
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi',
                                    'PrgEnv-cray', 'PrgEnv-cray_classic']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'latestpe'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
        if self.current_system.name in ['dom']:
            self.modules = ['cdt/20.03']  # will load perftools-base/20.03.0
        self.modules += ['perftools-preload']
        self.prebuild_cmds = ['module rm xalt']
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-Ofast',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray_classic': ['-I.', '-I./include', '-hstd=c++14', '-g',
                                    '-O3', '-hnoomp', '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.tool = 'pat_run'
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
        # This dictionary sets cubesize = f(mpitask), for instance:
        # if mpitask == 24:
        #     cubesize = 100
        size_dict = {24: 100, 48: 125, 96: 157, 192: 198, 384: 250, 480: 269,
                     960: 340, 1920: 428, 3840: 539, 7680: 680, 15360: 857,
                     6: 62, 3: 49, 1: 34
                     }
        cubesize = size_dict[mpitask]
        self.name = 'sphexa_patrun_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpitask, ompthread, cubesize, steps)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 24
        self.num_tasks_per_core = 2
        self.use_multithreading = True
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
        # -r: generate a report upon successful execution
        # TODO: use rpt-files/RUNTIME.rpt
        self.executable_opts = ['-r', '%s' % self.target_executable,
                                '-n %s' % cubesize, '-s %s' % steps, '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.csv_rpt = 'csv.rpt'
        self.pre_run = [
            'module rm xalt',
            'mv %s %s' % (self.executable, self.target_executable),
            '%s -V &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
            # 'rm -fr $HOME/.craypat/*',
        ]
        # use linux date as timer:
        self.pre_run += ['echo starttime=`date +%s`']
        self.post_run = ['echo stoptime=`date +%s`']
        # needed for sanity functions:
        self.rpt = 'rpt'
        csv_options = ('-v -O load_balance_group -s sort_by_pe=\'yes\' '
                       '-s show_data=\'csv\' -s pe=\'ALL\'')
        self.post_run += [
            # patrun_num_of_compute_nodes
            'ls -1 %s+*s/xf-files/' % self.target_executable,
            'cp *_job.out %s' % self.rpt,
            'pat_report %s %s+*s/index.ap2 &> %s' %
            (csv_options, self.target_executable, self.csv_rpt)
        ]
# }}}

# {{{ sanity
        self.sanity_patterns_l = [
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout)
        ]
        # will also silently call patrun_version (in sanity_perftools.py)
        self.sanity_patterns = sn.all(self.sanity_patterns_l)
# }}}

# {{{ performance: see sanity.py
# }}}

    @rfm.run_before('compile')
    def set_flags(self):
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

#     @rfm.run_before('sanity')
#     def cp_stdout(self):
#         self.post_run = ['cp *_job.out %s' % self.rpt]
