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
import sphexa.sanity_extrae as sphsextrae


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [24]
cubeside_dict = {24: 100}
steps_dict = {24: 1}


@rfm.parameterized_test(*[[mpi_task] for mpi_task in mpi_tasks])
class SphExaExtraeCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Extrae (mpi only)
    3 parameters can be set for simulation:

    :arg mpi_task: number of mpi tasks,
    :arg cubeside: size of the simulation domain,
    :arg steps: number of simulation steps.

    Typical performance reporting:

    .. literalinclude:: ../../reframechecks/extrae/extrae.res
      :lines: 1-7, 26-41

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
        self.prebuild_cmds = ['module rm xalt']
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-I.', '-I./include', '-std=c++14', '-g', '-O3',
                           '-DUSE_MPI', '-DNDEBUG'],
        }
        # ---------------------------------------------------------------- tool
        self.tool = 'tool.sh'
        tool_ver = '3.8.1'
        tc_ver = '20.08'
        self.tool_modules = {
            'PrgEnv-gnu': [f'Extrae/{tool_ver}-CrayGNU-{tc_ver}'],
        }
        # ---------------------------------------------------------------- tool
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
        self.name = \
            'sphexa_extrae_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
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
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.rpt = 'rpt'
        self.tool = './tool.sh'
        self.executable = self.tool
        self.executable_opts = [
            f'-- -n {self.cubeside}', f'-s {self.steps}', '2>&1']
        self.xml1 = '$EBROOTEXTRAE/share/example/MPI/extrae.xml'
        self.xml2 = 'extrae.xml'
        self.patch = 'extrae.xml.patch'
        self.version_file = 'extrae_version.h'
        self.prerun_cmds = [
            'module rm xalt',
            # tool version
            'cp $EBROOTEXTRAE/include/extrae_version.h %s' % self.version_file,
            # will launch ./tool.sh myexe myexe_args:
            'mv %s %s' % (self.executable, self.target_executable),
            # .xml
            'echo %s &> %s' % (self.xml1, self.which_rpt),
            'patch -i %s %s -o %s' % (self.patch, self.xml1, self.xml2),
            # .sh
            'echo -e \'%s\' >> %s' % (sphsextrae.create_sh(self), self.tool),
            'chmod u+x %s' % (self.tool),
        ]
        self.prv = '%s.prv' % self.target_executable[2:]  # stripping './'
        self.postrun_cmds = [
            'stats-wrapper.sh %s -comms_histo' % self.prv,
        ]
        self.rpt_mpistats = '%s.comms.dat' % self.target_executable
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool version:
            sn.assert_true(sphsextrae.extrae_version(self)),
            # check the summary report:
            sn.assert_found(r'Congratulations! %s has been generated.' %
                            self.prv, self.stdout),
        ])
        # }}}

        # {{{  performance
        # {{{ internal timers
        # use linux date as timer:
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphsextrae.rpt_mpistats(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        basic_reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        self.reference = basic_reference
        # tool's reference
        myzero = (0, None, None, '')
        myzero_p = (0, None, None, '%')
        self.reference['*:num_comms_0-10B'] = myzero
        self.reference['*:num_comms_10B-100B'] = myzero
        self.reference['*:num_comms_100B-1KB'] = myzero
        self.reference['*:num_comms_1KB-10KB'] = myzero
        self.reference['*:num_comms_10KB-100KB'] = myzero
        self.reference['*:num_comms_100KB-1MB'] = myzero
        self.reference['*:num_comms_1MB-10MB'] = myzero
        self.reference['*:num_comms_10MB'] = myzero
        #
        self.reference['*:%_of_bytes_sent_0-10B'] = myzero_p
        self.reference['*:%_of_bytes_sent_10B-100B'] = myzero_p
        self.reference['*:%_of_bytes_sent_100B-1KB'] = myzero_p
        self.reference['*:%_of_bytes_sent_1KB-10KB'] = myzero_p
        self.reference['*:%_of_bytes_sent_10KB-100KB'] = myzero_p
        self.reference['*:%_of_bytes_sent_100KB-1MB'] = myzero_p
        self.reference['*:%_of_bytes_sent_1MB-10MB'] = myzero_p
        self.reference['*:%_of_bytes_sent_10MB'] = myzero_p
        # TODO:
        # tool_reference =
        # sn.evaluate(sphsextrae.tool_reference_scoped_d(self))
        # self.reference = {**basic_reference, **tool_reference}
# }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('run')
    def set_prg_environment(self):
        self.modules = self.tool_modules[self.current_environ.name]

    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
    # }}}
