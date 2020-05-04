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


@rfm.parameterized_test(*[[mpitask, cubesize, steps]
                          for mpitask in [24]
                          for cubesize in [100]
                          for steps in [0]
                          ])
class SphExaNativeCheck(rfm.RegressionTest):
# {{{
    '''
    This class runs the test code without any tool (mpi only), and reports
    elapsed time from internal timers. 3 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks,
    :arg cubesize: size of the cube in the 3D square patch test,
    :arg steps: number of simulation steps.

    .. code-block:: none

       A weak scaling study (normal partition <= 2400cn)
       --------------------------------------------------
      weak cn    p/c    c       np            cubesize
      weak 1     41000  24      984000         99      1million
      weak 2     41000  48      1968000       125
      weak 4     41000  96      3936000       157
      weak 8     41000  192     7872000       198
      weak 16    41000  384     15744000      250     10millions
      weak 20    41000  480     19680000      269
      weak 40    41000  960     39360000      340
      weak 80    41000  1920    78720000      428
      weak 160   41000  3840    157440000     539     100millions
      weak 320   41000  7680    314880000     680
      weak 640   41000  15360   629760000     857
      weak 1280  41000  30720   1259520000   1079     1billion
      ------------------------------------------------------------
      weak 2560  41000  61440   2519040000   1360
      weak 5120  41000  122880  5038080000   1714
      weak 10240 41000  245760  10076160000  2159    10billions

    Typical output:

    .. code-block:: none

      starttime=1579725956
      # domain::distribute: 0.0983208s
      # mpi::synchronizeHalos: 0.0341479s
      # domain::buildTree: 0.084004s
      # updateTasks: 0.000900428s
      # FindNeighbors: 0.354712s
      # Density: 0.296224s
      # EquationOfState: 0.00244751s
      # mpi::synchronizeHalos: 0.0770191s
      # IAD: 0.626564s
      # mpi::synchronizeHalos: 0.344856s
      # MomentumEnergyIAD: 1.05951s
      # Timestep: 0.621583s
      # UpdateQuantities: 0.00498222s
      # EnergyConservation: 0.00137127s
      # UpdateSmoothingLength: 0.00321161s
      ### Check ### Global Tree Nodes: 1097, Particles: 40947, Halos: 109194
      ### Check ### Computational domain: -49.5 49.5 -49.5 49.5 -50 50
      ### Check ### Total Neighbors: 244628400, Avg neighbor count per particle: 244
      ### Check ### Total time: 1.1e-06, current time-step: 1.1e-06
      ### Check ### Total energy: 2.08323e+10, (internal: 1e+06, cinetic: 2.08313e+10)
      === Total time for iteration(0) 3.61153s
      stoptime=1579725961

    Typical performance reporting:

    .. code-block:: none

      PERFORMANCE REPORT
      -----------------------------------------------
      sphexa_timers_sqpatch_024mpi_001omp_100n_0steps
      - daint:gpu
         - PrgEnv-gnu
            * num_tasks: 24
            * Elapsed: 3.6201 s
            * _Elapsed: 5 s
            * domain_build: 0.0956 s
            * mpi_synchronizeHalos: 0.4567 s
            * BuildTree: 0 s
            * FindNeighbors: 0.3547 s
            * Density: 0.296 s
            * EquationOfState: 0.0024 s
            * IAD: 0.6284 s
            * MomentumEnergyIAD: 1.0914 s
            * Timestep: 0.6009 s
            * UpdateQuantities: 0.0051 s
            * EnergyConservation: 0.0012 s
            * SmoothingLength: 0.0033 s
            *
            * %MomentumEnergyIAD: 30.15 %
            * %Timestep: 16.6 %
            * %mpi_synchronizeHalos: 12.62 %
            * %FindNeighbors: 9.8 %
            * %IAD: 17.36 %
    '''
# }}}
    def __init__(self, mpitask, cubesize, steps):
        # {{{ pe
        self.descr = 'Strong scaling study'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel',
                                    'PrgEnv-cray', 'PrgEnv-cray_classic',
                                    'PrgEnv-pgi']
        #self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
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
        # self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.executable = '%s.exe' % self.testname

# }}}

# {{{ run
        ompthread = 1
        # This dictionary sets cubesize = f(mpitask), for instance:
        # if mpitask == 24:
        #     cubesize = 100
        size_dict = {24: 100, 48: 125, 96: 157, 192: 198, 384: 250, 480: 269,
                     960: 340, 1920: 428, 3840: 539, 7680: 680, 15360: 857
                     }
        cubesize = size_dict[mpitask]
        self.name = 'sphexa_timers_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpitask, ompthread, cubesize, steps)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 24  # 72
# {{{ ht:
        # self.num_tasks_per_node = mpitask if mpitask < 36 else 36   # noht
        # self.use_multithreading = False  # noht
        # self.num_tasks_per_core = 1      # noht

        # self.num_tasks_per_node = mpitask if mpitask < 72 else 72
        # self.use_multithreading = True # ht
        # self.num_tasks_per_core = 2    # ht
# }}}
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 2
        self.use_multithreading = True
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps]
# }}}

# {{{ sanity
        # sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found('Total time for iteration\(0\)', self.stdout),
        ])
# }}}

# {{{ performance
        # {{{ internal timers
        # use linux date as timer:
        self.pre_run = ['echo starttime=`date +%s`']
        self.post_run = ['echo stoptime=`date +%s`']
        #self.rpt = '%s.rpt' % self.testname
        # }}}

        # {{{ perf_patterns:
        self.perf_patterns = {
            'Elapsed':              sphs.seconds_elaps(self),
            '_Elapsed':             sphs.elapsed_time_from_date(self),
            #
            'domain_distribute':    sphs.seconds_domaindistrib(self),
            'mpi_synchronizeHalos': sphs.seconds_halos(self),
            'BuildTree':            sphs.seconds_tree(self),
            'FindNeighbors':        sphs.seconds_neigh(self),
            'Density':              sphs.seconds_denst(self),
            'EquationOfState':      sphs.seconds_state(self),
            'IAD':                  sphs.seconds_iad(self),
            'MomentumEnergyIAD':    sphs.seconds_energ(self),
            'Timestep':             sphs.seconds_step(self),
            'UpdateQuantities':     sphs.seconds_updat(self),
            'EnergyConservation':   sphs.seconds_consv(self),
            'SmoothingLength':      sphs.seconds_smoothinglength(self),
        }
        # top%
        self.perf_patterns.update({
            '%MomentumEnergyIAD':       sphs.pctg_MomentumEnergyIAD(self),
            '%Timestep':                sphs.pctg_Timestep(self),
            '%mpi_synchronizeHalos':    sphs.pctg_mpi_synchronizeHalos(self),
            '%FindNeighbors':           sphs.pctg_FindNeighbors(self),
            '%IAD':                     sphs.pctg_IAD(self),
        })
        # }}}

        # {{{ reference:
        self.reference = {
            '*': {
                'Elapsed': (0, None, None, 's'),
                '_Elapsed': (0, None, None, 's'),
                #
                'domain_distribute': (0, None, None, 's'),
                'mpi_synchronizeHalos': (0, None, None, 's'),
                'BuildTree': (0, None, None, 's'),
                'FindNeighbors': (0, None, None, 's'),
                'Density': (0, None, None, 's'),
                'EquationOfState': (0, None, None, 's'),
                'IAD': (0, None, None, 's'),
                'MomentumEnergyIAD': (0, None, None, 's'),
                'Timestep': (0, None, None, 's'),
                'UpdateQuantities': (0, None, None, 's'),
                'EnergyConservation': (0, None, None, 's'),
                'SmoothingLength': (0, None, None, 's'),
                # top%
                '%MomentumEnergyIAD': (0, None, None, '%'),
                '%Timestep': (0, None, None, '%'),
                '%mpi_synchronizeHalos': (0, None, None, '%'),
                '%FindNeighbors': (0, None, None, '%'),
                '%IAD': (0, None, None, '%'),
            }
        }
# }}}
# }}}

    @rfm.run_before('compile')
    def setflags(self):
        self.build_system.cxxflags = self.prgenv_flags[self.current_environ.name]

# {{{
# ok     def setup(self, partition, environ, **job_opts):
# ok         super().setup(partition, environ, **job_opts)
# ok         environ_name = self.current_environ.name
# ok         prgenv_flags = self.prgenv_flags[environ_name]
# ok         self.build_system.cxxflags = prgenv_flags
# ---
# ok     exec(open("../common/sphexa/performance.py").read())
# }}}
