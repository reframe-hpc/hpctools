import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.sanity as sphs
import sphexa.sanity_intel as sphsintel


@rfm.parameterized_test(*[[mpitask, steps]
                          for mpitask in [24]
                          for steps in [0]
                          # for cubesize in [100]
                          ])
class SphExaNativeCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Intel Advisor (mpi only):
    https://software.intel.com/en-us/advisor

    Available analysis types are: ``advixe-cl -h collect``

    .. code-block:: none

      survey       - Discover efficient vectorization and/or threading
      dependencies - Identify and explore loop-carried dependencies for loops
      map          - Identify and explore complex memory accesses
      roofline     - Run the Survey analysis + Trip Counts & FLOP analysis
      suitability  - Check predicted parallel performance
      tripcounts   - Identify the number of loop iterations.

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
            * Elapsed: 3.6147 s
            ...
            * advisor_elapsed: 2.13 s
            * advisor_loop1_line: 94 (momentumAndEnergyIAD.hpp)
    '''
    # }}}

    def __init__(self, mpitask, steps):
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
        self.modules = ['advisor/2020']
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
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.tool = 'advixe-cl'
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
                     6: 30,
                     }
        cubesize = size_dict[mpitask]
        self.name = 'sphexa_advisor_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
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
        self.time_limit = (0, 10, 0)
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.dir_rpt = 'rpt'
        self.tool_opts = '--collect=survey --search-dir src:rp=. ' \
                         '--data-limit=0 --no-auto-finalize --trace-mpi ' \
                         '--project-dir=%s -- ' % self.dir_rpt
        self.executable_opts = [self.tool_opts, '%s' % self.target_executable,
                                '-n %s' % cubesize, '-s %s' % steps, '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.summary_rpt = 'summary.rpt'
        self.pre_run = [
            'module rm xalt',
            'mv %s %s' % (self.executable, self.target_executable),
            '%s --version &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
        ]
        self.post_run = [
            'cd %s ;ln -s nid?????.000 e000 ;cd -' % self.dir_rpt,
            '%s --report=survey --project-dir=%s &> %s' %
            (self.tool, self.dir_rpt, self.summary_rpt),
        ]
# }}}

# {{{ sanity
        # sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version:
            sn.assert_true(sphsintel.advisor_version(self)),
            # check the summary report:
            sn.assert_found(r'advixe: This data has been saved',
                            self.summary_rpt),
        ])
# }}}

# {{{ performance
        # {{{ internal timers
        # use linux date as timer:
        self.pre_run += ['echo starttime=`date +%s`']
        self.post_run += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # tool
        self.perf_patterns.update({
            'advisor_elapsed': sphsintel.advisor_elapsed(self),
            'advisor_loop1_line': sphsintel.advisor_loop1_line(self),
        })
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool
        self.reference['*:advisor_elapsed'] = (0, None, None, 's')
        loop1_fname = sphsintel.advisor_loop1_filename(self)
        self.reference['*:advisor_loop1_line'] = (0, None, None, loop1_fname)
        # NOTE: this also works:
        # 'advisor_loop1_line': (0, None, None,
        #   sphsintel.advisor_loop1_filename(self)),
#         self.reference = {
#             '*': {
#                 'Elapsed': (0, None, None, 's'),
#                 '_Elapsed': (0, None, None, 's'),
#                 #
#                 'domain_distribute': (0, None, None, 's'),
#                 'mpi_synchronizeHalos': (0, None, None, 's'),
#                 'BuildTree': (0, None, None, 's'),
#                 'FindNeighbors': (0, None, None, 's'),
#                 'Density': (0, None, None, 's'),
#                 'EquationOfState': (0, None, None, 's'),
#                 'IAD': (0, None, None, 's'),
#                 'MomentumEnergyIAD': (0, None, None, 's'),
#                 'Timestep': (0, None, None, 's'),
#                 'UpdateQuantities': (0, None, None, 's'),
#                 'EnergyConservation': (0, None, None, 's'),
#                 'SmoothingLength': (0, None, None, 's'),
#                 # top%
#                 '%MomentumEnergyIAD': (0, None, None, '%'),
#                 '%Timestep': (0, None, None, '%'),
#                 '%mpi_synchronizeHalos': (0, None, None, '%'),
#                 '%FindNeighbors': (0, None, None, '%'),
#                 '%IAD': (0, None, None, '%'),
#                 # tool
#                 'advisor_elapsed': (0, None, None, 's'),
#                 'advisor_loop1_line': (0, None, None, loop1_fname),
#             }
#         }
# }}}
# }}}

    @rfm.run_before('compile')
    def setflags(self):
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]