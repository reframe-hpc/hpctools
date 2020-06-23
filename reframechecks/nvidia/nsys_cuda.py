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
import sphexa.sanity_nvidia as sphsnv


# 3 steps minimum to avoid "delay timeout" error
@rfm.parameterized_test(*[[mpitask, steps]
                          for mpitask in [2]
                          for steps in [3]
                          ])
class SphExaNsysCudaCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Nvidia nsys systems (2 mpi tasks min)
    https://docs.nvidia.com/nsight-systems/index.html

    Available analysis types are: ``nsys profile -help``

    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.

    Typical performance reporting:

    .. literalinclude:: ../../reframechecks/nvidia/nsys_cuda.res
      :emphasize-lines: 26

    # Total execution time of 2 iterations of SqPatch: 1.01668s
    The application terminated before the delay timeout. No report was generated.
    '''
    # }}}

    def __init__(self, mpitask, steps):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'gpu'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
        self.modules = ['craype-accel-nvidia60',
                        'nvidia-nsight-systems/2020.2.1.71']
                        # 'nvidia-nsight-systems/2020.1.1.65']
        self.prebuild_cmds = ['module rm xalt']

        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.build_system.nvcc = 'nvcc'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2
        self.tool = 'nsys'
        self.executable = self.tool
        self.target_executable = 'mpi+omp+cuda'
        self.build_system.options = [
            self.target_executable, 'MPICXX=CC', 'SRCDIR=.', 'BUILDDIR=.',
            'BINDIR=.', 'CUDA_PATH=$CUDATOOLKIT_HOME',
            # The makefile adds -DUSE_MPI
            # 'CXXFLAGS=',
        ]
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
                     2: 40
                     }
        cubesize = size_dict[mpitask]
        self.name = 'sphexa_nsyscuda_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpitask, ompthread, cubesize, steps)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 1  # 72
# {{{ ht:
        # self.num_tasks_per_node = mpitask if mpitask < 36 else 36   # noht
        # self.use_multithreading = False  # noht
        # self.num_tasks_per_core = 1      # noht

        # self.num_tasks_per_node = mpitask if mpitask < 72 else 72
        # self.use_multithreading = True # ht
        # self.num_tasks_per_core = 2    # ht
# }}}
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '15m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.tool = 'nsys'
        self.tool_opts = (r'profile --force-overwrite=true '
                          r'-o %h.%q{SLURM_NODEID}.%q{SLURM_PROCID}.qdstrm '
                          r'--trace=cuda,mpi,nvtx --mpi-impl=mpich '
                          r'--stats=true '
                          r'--delay=2')
        # deactivate cpu reporting:
        # tool_opts += '--sample=none '
        # tool_opts += '--trace=cublas,cuda,mpi,nvtx,osrt --mpi-impl=mpich '
        self.executable_opts = [self.tool_opts, '%s' % self.target_executable,
                                '-n %s' % cubesize, '-s %s' % steps, '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.summary_rpt = 'summary.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            'mv %s %s' % (self.target_executable + '.app',
                          self.target_executable),
            '%s --version &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
        ]
# }}}

# {{{ sanity
        # sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool's version:
            sn.assert_true(sphsnv.nsys_version(self)),
            # check the summary report:
            sn.assert_found('Exported successfully', self.stdout),
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
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphsnv.nsys_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool's reference
        myzero_k = (0, None, None, 'KiB')
        myzero_p = (0, None, None, '%')
        self.reference['*:%cudaMemcpy'] = myzero_p
        self.reference['*:%CUDA_memcpy_HtoD_time'] = myzero_p
        self.reference['*:%CUDA_memcpy_DtoH_time'] = myzero_p
        self.reference['*:CUDA_memcpy_HtoD_KiB'] = myzero_k
        self.reference['*:CUDA_memcpy_DtoH_KiB'] = myzero_k
        self.reference['*:%computeMomentumAndEnergyIAD'] = myzero_p
        self.reference['*:%computeIAD'] = myzero_p
# }}}
# }}}
