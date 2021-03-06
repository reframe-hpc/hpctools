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


# NOTE: jenkins restricted to 1 cnode
# NOTE: 3 steps minimum to avoid "delay timeout" error + cubeside >= 40
mpi_tasks = [2]
cubeside_dict = {2: 40}
steps_dict = {2: 3}


# {{{ class SphExaNsysCudaCheck
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
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

    Versions:
        - cudatoolkit/10.2.89 has nsys/2019.5.2.16-b54ef97
        - nvhpc/2020_207-cuda-10.2 has nsys/2020.3.1.54-2bd2a65
        - nvidia-nsight-systems/2020.3.1.72 has nsys/2020.3.1.72-e5b8014 <--
    '''
    # }}}

    def __init__(self, mpi_task):
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
        self.tool = 'nsys'
        self.tool_mf = 'nvidia-nsight-systems'
        tc_ver = '20.08'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}', 'craype-accel-nvidia60',
                           self.tool_mf],
        }
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.build_system.nvcc = 'nvcc'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2
        self.executable = self.tool
        self.target_executable = 'mpi+omp+cuda'
        self.build_system.options = [
            self.target_executable, 'MPICXX=CC', 'SRCDIR=.', 'BUILDDIR=.',
            'BINDIR=.', 'CUDA_PATH=$CUDATOOLKIT_HOME',
            # The makefile adds -DUSE_MPI
            # 'CXXFLAGS=',
        ]
        self.postbuild_cmds = [f'mv {self.target_executable}.app '
                               f'{self.target_executable}']
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_nsyscuda_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps)
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '15m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.tool_opts = (r'profile --force-overwrite=true '
                          r'-o %h.%q{SLURM_NODEID}.%q{SLURM_PROCID}.qdstrm '
                          r'--trace=cuda,mpi,nvtx --mpi-impl=mpich '
                          r'--stats=true '
                          r'--delay=2')
        # deactivate cpu reporting:
        # tool_opts += '--sample=none '
        # tool_opts += '--trace=cublas,cuda,mpi,nvtx,osrt --mpi-impl=mpich '
        self.executable_opts = [
            self.tool_opts, self.target_executable,
            f'-- -n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.summary_rpt = 'summary.rpt'
        # Reminder: NVreg_RestrictProfilingToAdminUsers=0 (RFC-16) needed since
        # cuda/10.1
        self.postrun_cmds = ['cat /etc/modprobe.d/nvidia.conf']
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        # }}}

        # {{{ sanity
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
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
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

    # {{{ hooks
    @rfm.run_before('compile')
    def set_prg_environment(self):
        self.modules += self.tool_modules[self.current_environ.name]
    # }}}
# }}}
