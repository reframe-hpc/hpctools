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


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {1: 30, 12: 78, 24: 100}
steps_dict = {1: 0, 12: 0, 24: 0}


# {{{ class SphExa_MPI
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExa_MPI_Check(rfm.RegressionTest):
    def __init__(self, mpi_task):
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
        self.sourcesdir = 'src_cpu'
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
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'{self.testname}.exe'
        # }}}

        # {{{ run
        ompthread = 1
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_timers_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
        self.num_tasks = mpi_task
        self.num_tasks_per_node = 24
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 2
        self.use_multithreading = True
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.executable_opts = [f"-n {self.cubeside}", f"-s {self.steps}"]
        self.prerun_cmds += ['module rm xalt', 'module list -t']
        # }}}

        # {{{ sanity
        # sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds = ['echo stoptime=`date +%s`']
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
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

# {{{
# ok     def setup(self, partition, environ, **job_opts):
# ok         super().setup(partition, environ, **job_opts)
# ok         environ_name = self.current_environ.name
# ok         prgenv_flags = self.prgenv_flags[environ_name]
# ok         self.build_system.cxxflags = prgenv_flags
# ---
# ok     exec(open("../common/sphexa/performance.py").read())
# }}}
