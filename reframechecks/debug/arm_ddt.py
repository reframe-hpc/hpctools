# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.launchers import LauncherWrapper


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]  # [24, 480, 528, 8192]
cubeside_dict = {24: 30, 480: 78, 528: 81, 8192: 201}
steps_dict = {24: 2, 480: 2, 528: 2, 8192: 2}


# {{{ class SphExaDDTCheck
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExaDDTCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Arm Forge DDT (mpi),
    3 parameters can be set for the simulation:

    :arg mpi_task: number of mpi tasks,
    :arg cubeside: size of the simulation domain,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpi_task):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi',
                                    'PrgEnv-cray']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.tool = 'ddt'
        # need to set version to avoid module load to fail.
        self.tool_v = '20.1.1-Suse-15.0'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}', f'{self.tool}/{self.tool_v}'],
            'PrgEnv-intel': [f'CrayIntel/.{tc_ver}',
                             f'{self.tool}/{self.tool_v}'],
            'PrgEnv-cray': [f'CrayCCE/.{tc_ver}',
                            f'{self.tool}/{self.tool_v}'],
            'PrgEnv-pgi': [f'CrayPGI/.{tc_ver}', f'{self.tool}/{self.tool_v}'],
        }
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-O0',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'./{self.testname}.exe'
        # make mpi ranks > 2 crash after second iteration:
        self.step_abort = 1
        insert_abort = (r'"/sph::computeMomentumAndEnergyIAD/a if (d.rank > 2 '
                        r'&& d.iteration > %s)'
                        r' { MPI::COMM_WORLD.Abort(0); }"' % self.step_abort)
        self.prebuild_cmds = [
            'module rm xalt',
            'module list -t',
            'sed -i %s %s' % (insert_abort, self.sourcepath),
        ]
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_ddt_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
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
        self.executable_opts = [
            f'-n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.txt_rpt = 'rpt_ddt.txt'
        self.htm_rpt = 'rpt_ddt.html'
        self.postrun_cmds = [
            'echo stoptime=`date +%s`',
            # htm2txt is the same as running with --output=rpt.txt, see hook
            'w3m -dump %s > %s' % (self.htm_rpt, self.txt_rpt),
        ]
        # }}}

        # {{{ sanity
        # --- "0-23  Add tracepoint for sqpatch.cpp:75"
        regex_addtp = r' 0-\d+\s+Add tracepoint for \S+:\d+'
        # --- "* number of processes : 24"
        #                              ^^
        regex_np = r'\* number of processes\s+:\s(?P<nprocs>\d+)'
        res_np = sn.extractsingle(regex_np, self.txt_rpt, 'nprocs', int)
        # ---
        #   Time      Tracepoint    Processes            Values
        #   main(int, domain.clist[0]: Sparkline from 0 to 19286 domain.clist:
        #                                                  ^^^^^
        regex_tpoint = r'from 0 to (?P<maxi>\d+)'
        rest = sn.count(sn.extractall(regex_tpoint, self.txt_rpt, 'maxi', int))
        # ---
        #   Time      Tracepoint    Processes            Values
        #   main(int, domain.clist[0]: Sparkline from 0 to 19286 domain.clist:
        #     1 0:08.098 char**)          0-23      std::vector of length 0,
        #                                                       capacity 1786
        #                                                                ^^^^
        regex_cap = r'domain\.clist:\s*\n?.*capacity\s+(?P<cap>\d+)'
        # --- "3-23  MPI::Comm::Abort  virtual void Abort" = 21/24 core crashed
        regex_abort = r'^\s+(?P<rk0>\d+)-(?P<rkn>\d+).*MPI::Comm::Abort\s+'
        res_rk0 = sn.extractsingle(regex_abort, self.txt_rpt, 'rk0', int)
        res_rkn = sn.extractsingle(regex_abort, self.txt_rpt, 'rkn', int)
        res_rk = res_rkn - res_rk0 + 1
        # ---
        self.sanity_patterns = sn.all([
            sn.assert_found(regex_addtp, self.txt_rpt),
            sn.assert_eq(self.num_tasks, res_np),
            sn.assert_found(regex_cap, self.txt_rpt),
            sn.assert_eq(self.step_abort + 2, rest),
            sn.assert_eq(self.num_tasks - 3, res_rk),
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_after('setup')
    def set_launcher(self):
        linen = 75
        tracepoint = r'"%s:%d,domain.clist[0],domain.clist"' % \
                     (self.sourcepath, linen)
        # recommending tracepoint but this will work too:
        # --break-at %s:%d --evaluate="domain.clist;domain.clist[0]"
        self.ddt_options = ['--offline', '--output=%s' % self.htm_rpt,
                            '--trace-at', tracepoint]
        self.job.launcher = LauncherWrapper(self.job.launcher, self.tool,
                                            self.ddt_options)
    # }}}
# }}}


# {{{ class SphExaLegacyDDTCheck
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExaLegacyDDTCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Arm Forge DDT (mpi),
    3 parameters can be set for the simulation:

    :arg mpi_task: number of mpi tasks,
    :arg cubeside: size of the simulation domain,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpi_task):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi',
                                    'PrgEnv-cray']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sqpatch'
        self.tool = 'ddt'
        self.tool_v = '20.0-Suse-15.0'
        self.tool_version = self.tool_v.split('-')[0]
        self.tool_lic = '6784'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}', f'{self.tool}/{self.tool_v}'],
            'PrgEnv-intel': [f'CrayIntel/.{tc_ver}',
                             f'{self.tool}/{self.tool_v}'],
            'PrgEnv-cray': [f'CrayCCE/.{tc_ver}',
                            f'{self.tool}/{self.tool_v}'],
            'PrgEnv-pgi': [f'CrayPGI/.{tc_ver}', f'{self.tool}/{self.tool_v}'],
        }
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                           '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-intel': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                             '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-cray': ['-I.', '-I./include', '-std=c++17', '-g', '-O0',
                            '-DUSE_MPI', '-DNDEBUG'],
            'PrgEnv-pgi': ['-I.', '-I./include', '-std=c++14', '-g', '-O0',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'./{self.testname}'
        # make mpi ranks > 2 crash after second iteration:
        self.step_abort = 1
        insert_abort = (r'"/sph::computeMomentumAndEnergyIAD/a if (d.rank > 2 '
                        r'&& d.iteration > %s)'
                        r' { MPI::COMM_WORLD.Abort(0); }"' % self.step_abort)
        self.prebuild_cmds = [
            'module rm xalt',
            'module list -t',
            'sed -i %s %s' % (insert_abort, self.sourcepath),
        ]
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_ddt0_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
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
        self.executable_opts = [
            f'-- -n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.lic_rpt = 'rpt_ddt.lic'
        self.prerun_cmds = [
            'module rm xalt',
            f'{self.tool} --version &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'cat $EBROOTDDT/licences/Licence > {self.lic_rpt}',
        ]
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.txt_rpt = 'rpt_ddt.txt'
        self.htm_rpt = 'rpt_ddt.html'
        self.postrun_cmds = [
            'echo stoptime=`date +%s`',
            # htm2txt is the same as running with --output=rpt.txt, see hook
            f'w3m -dump {self.htm_rpt} > {self.txt_rpt}',
        ]
        # }}}

        # {{{ sanity
        # --- license version:
        regex_lic = r'^serial_number=(?P<vv>\S+)$'
        res_lic = sn.extractsingle(regex_lic, self.lic_rpt, 'vv')
        # --- tool version:
        regex_version = r'Version: (?P<vv>\S+)$'
        res_version = sn.extractsingle(regex_version, self.version_rpt, 'vv')
        # --- "0-23  Add tracepoint for sqpatch.cpp:75"
        regex_addtp = r' 0-\d+\s+Add tracepoint for \S+:\d+'
        # --- "* number of processes : 24"
        #                              ^^
        regex_np = r'\* number of processes\s+:\s(?P<nprocs>\d+)'
        res_np = sn.extractsingle(regex_np, self.txt_rpt, 'nprocs', int)
        # ---
        #   Time      Tracepoint    Processes            Values
        #   main(int, domain.clist[0]: Sparkline from 0 to 19286 domain.clist:
        #                                                  ^^^^^
        regex_tpoint = r'from 0 to (?P<maxi>\d+)'
        rest = sn.count(sn.extractall(regex_tpoint, self.txt_rpt, 'maxi', int))
        # ---
        #   Time      Tracepoint    Processes            Values
        #   main(int, domain.clist[0]: Sparkline from 0 to 19286 domain.clist:
        #     1 0:08.098 char**)          0-23      std::vector of length 0,
        #                                                       capacity 1786
        #                                                                ^^^^
        regex_cap = r'domain\.clist:\s*\n?.*capacity\s+(?P<cap>\d+)'
        # --- "3-23  MPI::Comm::Abort  virtual void Abort" = 21/24 core crashed
        regex_abort = r'^\s+(?P<rk0>\d+)-(?P<rkn>\d+).*MPI::Comm::Abort\s+'
        res_rk0 = sn.extractsingle(regex_abort, self.txt_rpt, 'rk0', int)
        res_rkn = sn.extractsingle(regex_abort, self.txt_rpt, 'rkn', int)
        res_rk = res_rkn - res_rk0 + 1
        # ---
        self.sanity_patterns = sn.all([
            sn.assert_eq(self.tool_lic, res_lic),
            sn.assert_eq(self.tool_version, res_version),
            sn.assert_found(regex_addtp, self.txt_rpt),
            sn.assert_eq(self.num_tasks, res_np),
            sn.assert_found(regex_cap, self.txt_rpt),
            sn.assert_eq(self.step_abort + 2, rest),
            sn.assert_eq(self.num_tasks - 3, res_rk),
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules += self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]

    @rfm.run_after('setup')
    def set_launcher(self):
        linen = 75
        tracepoint = r'"%s:%d,domain.clist[0],domain.clist"' % \
                     (self.sourcepath, linen)
        # recommending tracepoint but this will work too:
        # --break-at %s:%d --evaluate="domain.clist;domain.clist[0]"
        self.ddt_options = ['--offline', '--output=%s' % self.htm_rpt,
                            '--trace-at', tracepoint]
        self.job.launcher = LauncherWrapper(self.job.launcher, self.tool,
                                            self.ddt_options)
    # }}}
# }}}
