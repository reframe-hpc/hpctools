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
import sphexa.sanity_intel as sphsintel


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {24: 100}
steps_dict = {24: 0}


@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaIntelInspectorCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Intel Inspector (mpi only):
    https://software.intel.com/en-us/inspector

    Available analysis types are: ``inspxe-cl -h collect``

    .. code-block:: none

      mi1   Detect Leaks
      mi2   Detect Memory Problems
      mi3   Locate Memory Problems
      ti1   Detect Deadlocks
      ti2   Detect Deadlocks and Data Races
      ti3   Locate Deadlocks and Data Races

    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.

    Typical performance reporting:

    .. code-block:: none

      PERFORMANCE REPORT
      --------------------------------------------------
      sphexa_inspector_sqpatch_024mpi_001omp_100n_0steps
      - dom:gpu
         - PrgEnv-gnu
            * num_tasks: 24
            * Elapsed: 8.899 s
            ...
            * Memory not deallocated: 1
    '''
    # }}}

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
        self.modules = ['inspector']
        self.prebuild_cmds = ['module rm xalt', 'module list -l']
        self.tool = 'inspxe-cl'
        self.tool_v = '2020_update2'
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
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_inspector_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps)
        self.num_tasks = mpi_task
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
        self.dir_rpt = 'rpt'
        self.tool_opts = '-collect mi1 -trace-mpi -no-auto-finalize -r %s' \
            % self.dir_rpt
        self.executable_opts = [self.tool_opts, self.target_executable,
                                f'-n {self.cubeside}', f'-s {self.steps}',
                                '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.summary_rpt = 'summary.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            'mv %s %s' % (self.executable, self.target_executable),
            '%s --version &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
        ]
        self.postrun_cmds = [
            '%s -r %s.* -report=summary &> %s' %
            (self.tool, self.dir_rpt, self.summary_rpt),
            # '%s -report=problems &> %s' % (self.tool, self.problems_rpt),
            # '%s -report=observations &> %s' %
            # (self.tool, self.observations_rpt),
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version:
            sn.assert_true(sphsintel.inspector_version(self)),
            # check the summary report:
            sn.assert_found(r'\d new problem\(s\) found', self.summary_rpt),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        # use linux date as timer:
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # self.rpt = '%s.rpt' % self.testname
        # }}}

        # {{{ perf_patterns:
#         self.perf_patterns = {
#             'Elapsed':              sphs.seconds_elaps(self),
#             '_Elapsed':             sphs.elapsed_time_from_date(self),
#             #
#             'domain_distribute':    sphs.seconds_domaindistrib(self),
#             'mpi_synchronizeHalos': sphs.seconds_halos(self),
#             'BuildTree':            sphs.seconds_tree(self),
#             'FindNeighbors':        sphs.seconds_neigh(self),
#             'Density':              sphs.seconds_denst(self),
#             'EquationOfState':      sphs.seconds_state(self),
#             'IAD':                  sphs.seconds_iad(self),
#             'MomentumEnergyIAD':    sphs.seconds_energ(self),
#             'Timestep':             sphs.seconds_step(self),
#             'UpdateQuantities':     sphs.seconds_updat(self),
#             'EnergyConservation':   sphs.seconds_consv(self),
#             'SmoothingLength':      sphs.seconds_smoothinglength(self),
#         }
#         # top%
#         self.perf_patterns.update({
#             '%MomentumEnergyIAD':     sphs.pctg_MomentumEnergyIAD(self),
#             '%Timestep':              sphs.pctg_Timestep(self),
#             '%mpi_synchronizeHalos':  sphs.pctg_mpi_synchronizeHalos(self),
#             '%FindNeighbors':         sphs.pctg_FindNeighbors(self),
#             '%IAD':                   sphs.pctg_IAD(self),
#         })
        # self.perf_patterns = sn.evaluate(self.basic_perf_patterns)
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # tool
        self.perf_patterns.update({
            'Memory not deallocated':
            sphsintel.inspector_not_deallocated(self),
            # 'Memory leak': sphsintel.inspector_leak(self),
        })
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # intel inspector
        self.reference['*:Memory not deallocated'] = (0, None, None, '')
        # self.reference['*:Memory leak'] = (0, None, None, '')
# }}}
    # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
    # }}}
