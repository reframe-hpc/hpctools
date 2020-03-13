# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
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


@rfm.parameterized_test(*[[mpitask, steps]
                          # for mpitask in [24, 48, 96]
                          for mpitask in [24]
                          for steps in [0]
                          ])
class SphExaMpipCheck(sphsmpip.MpipBaseTest):
    # {{{
    '''
    This class runs the test code with mpiP, the light-weight MPI profiler (mpi
    only): http://llnl.github.io/mpiP

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
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel',
                                    'PrgEnv-cray', 'PrgEnv-cray_classic',
                                    'PrgEnv-pgi']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
        self.modules = ['mpiP']
        # unload xalt to avoid _buffer_decode error:
        self.prebuild_cmd = ['module rm xalt']
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
        # ---------------------------------------------------------------- tool
        tool_ver = '57fc864'
        tc_ver = '19.10'
        self.tool_modules = {
            'PrgEnv-gnu': ['mpiP/%s-CrayGNU-%s' % (tool_ver, tc_ver)],
            'PrgEnv-intel': ['mpiP/%s-CrayIntel-%s' % (tool_ver, tc_ver)],
            'PrgEnv-cray': ['mpiP/%s-CrayCCE-%s' % (tool_ver, tc_ver)],
            'PrgEnv-cray_classic': ['mpiP/%s-CrayCCE-%s-classic' %
                                    (tool_ver, tc_ver)],
            'PrgEnv-pgi': ['mpiP/%s-CrayPGI-%s' % (tool_ver, tc_ver)]
        }
        # ---------------------------------------------------------------- tool
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
        # This dictionary sets cubesize = f(mpitask), for instance:
        # if mpitask == 24:
        #     cubesize = 100
        size_dict = {24: 100, 48: 125, 96: 157, 192: 198, 384: 250, 480: 269,
                     960: 340, 1920: 428, 3840: 539, 7680: 680, 15360: 857,
                     6: 62, 3: 49, 1: 34
                     }
        cubesize = size_dict[mpitask]
        self.name = 'sphexa_mpiP_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
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
            # 'MPIP': '"-c"',
        }
        # self.mpi_isendline = '140'
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps, '2>&1']
        self.pre_run = [
            'module rm xalt',
        ]
# }}}

# {{{ sanity
        self.sanity_patterns_l = [
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout)
        ]
        self.sanity_patterns = sn.all(self.sanity_patterns_l)
# }}}

# {{{ performance
        # {{{ internal timers
        # use linux date as timer:
        self.pre_run += ['echo starttime=`date +%s`']
        self.post_run += ['echo stoptime=`date +%s`']
        # }}}

#        # {{{ perf_patterns:
#        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
#        tool_perf_patterns = sn.evaluate(sphsintel.vtune_perf_patterns(self))
#        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
#        # }}}
#
#        # {{{ reference:
#        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
#        self.reference = sn.evaluate(sphsintel.vtune_tool_reference(self))
# }}}
# }}}

    @rfm.run_before('compile')
    def setflags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.build_system.ldflags = self.build_system.cxxflags + \
            ['-L$(EBROOTMPIP)/lib', '-Wl,--whole-archive -lmpiP',
             '-Wl,--no-whole-archive -lunwind', '-lbfd -liberty -ldl -lz']
