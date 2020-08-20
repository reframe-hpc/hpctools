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
import sphexa.sanity_gperftools as sphsgperf


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [12]
cubeside_dict = {1: 30, 12: 78, 24: 100}
steps_dict = {1: 0, 12: 1, 24: 0}


# {{{ class SphExaGperftoolsCheck
@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaGperftoolsCheck(rfm.RegressionTest):
    # {{{
    '''This class runs the test code with gperftools:
       https://gperftools.github.io/gperftools/cpuprofile.html

    '''
    # }}}

    def __init__(self, mpi_task):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
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
                           '-DUSE_MPI', '-DNDEBUG', '-fopenmp']
        }
        tool_ver = '2.8'
        tc_ver = '20.08'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.tool_modules = {
            'PrgEnv-gnu': [f'CrayGNU/.{tc_ver}', f'gperftools/{tool_ver}'],
        }
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = './gperftools.sh'
        self.tool_executable = f'gperftools_script.sh'
        self.target_executable = f'./{self.testname}.exe'
        self.prebuild_cmds = [
            'module rm xalt',
            'module list -t',
        ]
        # }}}

        # {{{  run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_gperf_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpi_task, ompthread, self.cubeside, self.steps)
        self.num_tasks_per_node = 12
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '10m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
            'OMP_PROC_BIND': 'true',
        }
        self.executable_opts = [
            self.target_executable,
            f"-n {self.cubeside}", f"-s {self.steps}"]
        self.prerun_cmds += [
            'module rm xalt', 'module list -t',
            f'mv {self.executable} {self.target_executable}',
            f'mv {self.tool_executable} {self.executable}']
        self.rpt_file = 'gperftools.rpt'
        self.rpt_file_txt = f'{self.rpt_file}.txt'
        self.rpt_file_pdf = f'{self.rpt_file}.pdf'
        self.rpt_file_doc = f'{self.rpt_file}.doc'
        self.postrun_tool = '$EBROOTPPROF/bin/pprof'
        self.postrun_cmds += [
            # txt rpt (quotation mark will make it fail):
            f'{self.postrun_tool} --unit=ms --text --lines '
            f'{self.target_executable} *.0 &> {self.rpt_file_txt}',
            # pdf rpt:
            f'{self.postrun_tool} --pdf {self.target_executable} *.0 '
            f'&> {self.rpt_file_pdf}',
            # pdf rpt type:
            f'file {self.rpt_file_pdf} &> {self.rpt_file_doc}',
            # '$EBROOTPPROF/bin/pprof --unit=ms --text --lines %s %s &> %s' %
            # (self.exe, '*.0', self.rpt_file_txt),
            # '$EBROOTPPROF/bin/pprof --pdf %s %s &> %s' %
            # (self.exe, '*.0', self.rpt_file_pdf),
            # 'file %s &> %s' % (self.rpt_file_pdf, self.rpt_file_doc)
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            sn.assert_found('PDF document', self.rpt_file_doc),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphsgperf.gp_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        self.reference = sn.evaluate(sphsgperf.gp_tool_reference(self))
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.build_system.ldflags = ['`pkg-config --libs libprofiler`']
    # }}}
# }}}
