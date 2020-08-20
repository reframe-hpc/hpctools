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
import sphexa.sanity_papi as sphspapi


# NOTE: jenkins restricted to 1 cnode
mpi_tasks = [12]
cubeside_dict = {1: 30, 12: 78, 24: 100}
steps_dict = {1: 0, 12: 0, 24: 0}


# {{{ class SphExaPapiWrapCheck
@rfm.parameterized_test(*[[mpi_task]
                          for mpi_task in mpi_tasks
                          ])
class SphExaPapiWrapCheck(rfm.RegressionTest):
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
                           '-DUSE_MPI', '-DNDEBUG', '-fopenmp',
                           '-I$EBROOTPAPIMINWRAP/include'],
        }
        tool_ver = '57150c8'
        tc_ver = '20.08'
        self.prebuild_cmds = ['module rm xalt', 'module list -t']
        self.tool_modules = {
            'PrgEnv-gnu': ['papi-wrap/%s-CrayGNU-%s' % (tool_ver, tc_ver)],
        }
        self.build_system = 'SingleSource'
        self.sourcepath = f'{self.testname}.cpp'
        self.executable = f'{self.testname}.exe'
        insert_include = (r"'/using namespace sphexa;/a #include \"Papi"
                          "Collectors.h\"\\n#include \"papi_wrap.h\"'")
        insert_new = (r"'/const ArgParser parser(argc, argv);/a int "
                      "pwhandle_nrj = pw_new_collector(\"computeMomentum"
                      "AndEnergyIAD\");'")
        insert_start = (r"'/sph::computeMomentumAndEnergyIAD<Real>(taskList."
                        "tasks, d);/i pw_start_collector(pwhandle_nrj);'")
        insert_stop = (r"'/sph::computeMomentumAndEnergyIAD<Real>(taskList."
                       "tasks, d);/a pw_stop_collector(pwhandle_nrj);'")
        insert_print = (r"'/constantsFile.close();/a pw_print();"
                        "\\npw_print_table();'")
        # // write the counters to file, in plain text format
        # //papiCounters.writeToFile(std::string("counters.txt"),
        #                             fileFormatPlain);
        self.prebuild_cmds = [
            'module rm xalt',
            'module list -t',
            'sed -i %s %s' % (insert_include, self.sourcepath),
            'sed -i %s %s' % (insert_new, self.sourcepath),
            'sed -i %s %s' % (insert_start, self.sourcepath),
            'sed -i %s %s' % (insert_stop, self.sourcepath),
            'sed -i %s %s' % (insert_print, self.sourcepath),
        ]
        # }}}

        # {{{ run
        ompthread = 1
        self.num_tasks = mpi_task
        self.cubeside = cubeside_dict[mpi_task]
        self.steps = steps_dict[mpi_task]
        self.name = 'sphexa_papiw_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
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
            'CSCSPERF_EVENTS': '"PAPI_REF_CYC|PAPI_L2_DCM"',
        }
        self.executable_opts = [f"-n {self.cubeside}", f"-s {self.steps}"]
        self.prerun_cmds += ['module rm xalt', 'module list -t']
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
        ])
        # }}}

        # {{{ performance
        # {{{ internal timers
        self.prerun_cmds += ['echo starttime=`date +%s`']
        self.postrun_cmds += ['echo stoptime=`date +%s`']
        # }}}

        # {{{ perf_patterns:
        basic_perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))
        tool_perf_patterns = sn.evaluate(sphspapi.pw_perf_patterns(self))
        self.perf_patterns = {**basic_perf_patterns, **tool_perf_patterns}
        # }}}

        # {{{ reference:
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))
        self.reference = sn.evaluate(sphspapi.pw_tool_reference(self))
        # }}}
        # }}}

    # {{{ hooks
    @rfm.run_before('compile')
    def set_compiler_flags(self):
        self.modules = self.tool_modules[self.current_environ.name]
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.build_system.ldflags = ['-L$EBROOTPAPIMINWRAP/lib -lpapi_wrap '
                                     '-lpapi -lstdc++']
    # }}}
# }}}
