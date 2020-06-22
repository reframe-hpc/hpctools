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


@rfm.parameterized_test(*[[mpitask, steps]
                          for mpitask in [24]
                          for steps in [1]
                          ])
class SphExaNativeCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with Extrae (mpi only)

    2 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks; the size of the cube in the 3D
         square patch test is set with a dictionary depending on mpitask,
         but cubesize could also be on the list of parameters,
    :arg steps: number of simulation steps.

    Typical performance reporting:

    .. literalinclude:: ../../reframechecks/extrae/extrae.res
      :lines: 1-7, 26-41

    '''
    # }}}

    def __init__(self, mpitask, steps):
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
        tool_ver = '3.7.1'
        tc_ver = '19.10'
        self.tool_modules = {
            'PrgEnv-gnu': ['Extrae/%s-CrayGNU-%s' % (tool_ver, tc_ver)],
        }
        # ---------------------------------------------------------------- tool
        self.build_system = 'SingleSource'
        self.build_system.cxx = 'CC'
        self.sourcepath = '%s.cpp' % self.testname
        self.tool = 'tool.sh'
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
        self.name = \
            'sphexa_extrae_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'. \
            format(self.testname, mpitask, ompthread, cubesize, steps)
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
        self.executable_opts = ['-n %s' % cubesize, '-s %s' % steps]
        self.xml1 = '$EBROOTEXTRAE/share/example/MPI/extrae.xml'
        self.xml2 = 'extrae.xml'
        self.patch = 'extrae.xml.patch'
        self.version_file = 'extrae_version.h'
        self.pre_run = [
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
        self.post_run = [
            'stats-wrapper.sh %s -comms_histo' % self.prv,
        ]
        self.rpt_mpistats = '%s.comms.dat' % self.target_executable
# }}}

# {{{ sanity
        # sanity
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
        self.pre_run += ['echo starttime=`date +%s`']
        self.post_run += ['echo stoptime=`date +%s`']
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

    @rfm.run_before('compile')
    def setflags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
