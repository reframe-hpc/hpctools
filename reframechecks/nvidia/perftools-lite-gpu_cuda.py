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
import sphexa.sanity_perftools_lite_gpu as sphsptlgpu

# NOTE: jenkins restricted to 1 cnode
# NOTE: 3 steps minimum to avoid "delay timeout" error + cubeside >= 40
mpi_tasks = [2]
cubeside_dict = {2: 40}
steps_dict = {2: 3}
# cycles_dict = {2: 5000000}


# {{{ SphExaPtlCudaCheck
@rfm.parameterized_test(*[[mpi_task, cubeside]
                          for mpi_task in mpi_tasks
                          # for cubeside in [40]
                          for cubeside in [40, 80, 100]
                          ])
class SphExaPtlCudaCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with mpi+cuda:

    3 parameters can be set for simulation:

    :arg mpi_task: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.

    # P100-PCIE-16GB / MemTotal: 65'842'332 kB
    cuda_sqpatch_002mpi_001omp_40n_3steps  Elapsed: 3.8689 s 32'000 p/gpu
    cuda_sqpatch_002mpi_001omp_80n_3steps  Elapsed: 31.8801 s 256'000 p/gpu
    cuda_sqpatch_002mpi_001omp_100n_3steps Elapsed: 64.5344 s 500'000 p/gpu
    '''
    # }}}

    def __init__(self, mpi_task, cubeside):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        tc_ver = '20.08'
        self.modules = ['craype-accel-nvidia60', 'perftools-base']
        self.tool = 'pat_report'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}', 'perftools-lite-gpu'],
        }
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.build_system.nvcc = 'nvcc'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'./{self.testname}.exe'
        self.target_executable = 'mpi+omp+cuda'
        self.build_system.options = [
            self.target_executable, f'MPICXX="{self.build_system.cxx}"',
            'SRCDIR=.', 'BUILDDIR=.', 'BINDIR=.', 'CXXFLAGS=-std=c++14',
            'CUDA_PATH=$CUDATOOLKIT_HOME',
            # The makefile adds -DUSE_MPI
        ]
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.rpt = 'RUNTIME.rpt'
        self.postbuild_cmds = [
            f'mv {self.target_executable}.app ' f'{self.executable}',
            f'{self.tool} -V &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside
        self.steps = steps_dict[mpi_task]
        self.name = \
            'sphexa_perftools-gpu-cuda_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpi_task, ompthread, self.cubeside,
                   self.steps)
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.executable_opts = [
            f'-n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.prerun_cmds = ['module rm xalt']
        self.postrun_cmds = [
            f'cp {self.executable}+*/rpt-files/RUNTIME.rpt {self.rpt}']
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_true(sphsptlgpu.tool_version(self)),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphsptlgpu.tool_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # tool's reference
        myzero_p = (0, None, None, '%')
        myzero_mb = (0, None, None, 'MiBytes')
        self.reference['*:host_time%'] = myzero_p
        self.reference['*:device_time%'] = myzero_p
        self.reference['*:acc_copyin'] = myzero_mb
        self.reference['*:acc_copyout'] = myzero_mb
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
    # }}}
