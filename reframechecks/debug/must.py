# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.sanity as sphs
import sphexa.sanity_must as sphsmust


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {1: 30, 24: 100}
steps_dict = {1: 1, 24: 1}  # use same step


# {{{ class SphExa_Must_Base_Check
class SphExa_Must_Base_Check(rfm.RegressionTest):
    # {{{
    '''
    2 parameters can be set for simulation:

    :arg mpi_task: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpi_task,
         but cubesize could also be on the list of parameters,
    :arg step: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpi_task):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
        # self.sourcesdir = None
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'debug'}
        # }}}

        # {{{ compile
        # self.testname = 'sqpatch'
        self.tool = 'mustrun'
        tool_ver = 'v1.6'
        tc_ver = '20.08'
        # need to set version to avoid module load to fail.
        self.tool_modules = {
            'PrgEnv-gnu': [f'MUST/{tool_ver}-CrayGNU-{tc_ver}'],
        }
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O2',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = self.tool
        self.target_executable = f'./{self.testname}.exe'
        # unload xalt to avoid _buffer_decode error
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        if self.insert_bug is not '':
            self.prebuild_cmds += [
                'sed -i %s %s' % (self.insert_bug, self.sourcepath)]

        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.postbuild_cmds = [
            # --help return code is 1 (instead of 0), using a trick here:
            f'$({self.tool} --help &> {self.version_rpt} ;echo echo)',
            f'which {self.tool} &> {self.which_rpt}',
            f"mv {self.executable} {self.target_executable}"]
        # }}}

        # {{{ run
        # MUST requires 1 additional core:
        self.num_tasks = mpi_task
        cubeside = cubeside_dict[mpi_task]
        step = steps_dict[mpi_task]
        self.num_tasks_per_node = 24
        self.num_cpus_per_task = self.ompthread
        self.num_tasks_per_core = 2
        self.use_multithreading = True
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        # self.variables['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)
        self.html = 'MUST_Output.html'
        self.rpt = 'MUST_Output.rpt'
        self.prerun_cmds += ['module rm xalt', 'module list -t']
        # MUST requires 1 additional core:
        self.executable_opts += [
            '--must:mpiexec srun',
            '--must:np -n', f'-n {self.num_tasks - 1}', self.target_executable,
            f'-n {cubeside}', f'-s {step}', '2>&1']
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_found(r'\[MUST\] Executing application:', self.stdout),
            sn.assert_found(r'\[MUST\] Execution finished, inspect',
                            self.stdout),
            # sn.assert_found(r'MUST has completed successfully,', self.rpt),
            # check the tool's version:
            sn.assert_true(sphsmust.tool_version(self)),
            # custom check:
            sn.assert_found(self.regex_rpt, self.rpt),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += [
            'echo stoptime=`date +%s`',
            f'w3m -dump {self.html} &> {self.rpt}',
        ]
        # }}}

        # {{{ perf_patterns:
        # self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        # }}}

        # {{{ reference:
        # self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.build_system.ldflags = ['-L$EBROOTMUST/lib -lpnmpi']

    @rfm.run_before('run')
    def set_launcher(self):
        # The job launcher has to be changed because
        # the tool can be called without srun
        self.job.launcher = getlauncher('local')()
    # }}}
# }}}


# {{{ class MPI_Must_NoCrash_Test:
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class MPI_Must_NoCrash_Test(SphExa_Must_Base_Check):
    # {{{
    '''
    This class runs an executable that does not crash
    '''
    # }}}

    def __init__(self, mpi_task):
        # share args with TestBase class
        self.testname = 'sqpatch'
        self.ompthread = 1
        step = steps_dict[mpi_task]
        cubeside = cubeside_dict[mpi_task]
        self.name = 'sphexa_must1_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, self.ompthread, cubeside, step)
        self.executable_opts = ['--must:nocrash']
        self.insert_bug = ''
        self.regex_rpt = r'MUST detected no MPI usage errors'
        super().__init__(mpi_task)
        # self.postrun_cmds.extend(postrun_cmds)
# }}}


# {{{ class MPI_Must_Crash_Test:
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class MPI_Must_Crash_Test(SphExa_Must_Base_Check):
    # {{{
    '''
    This class runs an executable that does crash
    '''
    # }}}

    def __init__(self, mpi_task):
        # share args with TestBase class
        self.testname = 'sqpatch'
        self.ompthread = 1
        step = steps_dict[mpi_task]
        cubeside = cubeside_dict[mpi_task]
        self.name = 'sphexa_must2_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, self.ompthread, cubeside, step)
        self.executable_opts = []
        # make mpi ranks > 2 crash (taken from MUST-v1.6/tests):
        self.step_abort = 0
        self.insert_bug = (
            r'"/sph::computeMomentumAndEnergyIAD/a if (d.rank > 2 '
            r'&& d.iteration > %s) {MPI_Op op; op=MPI_SUM; MPI_Op_free(&op);}"'
            % self.step_abort)
        self.regex_rpt = r'Error\s+Argument \d+ \(op\) is a predefined op'
        super().__init__(mpi_task)
# }}}
