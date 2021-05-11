# Copyright 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.hooks as hooks
import sphexa.sanity as sphs
import sphexa.sanity_extrae as sphsextrae

from reframe.core.launchers import LauncherWrapper


# {{{ class SphExa_Extrae_Check
@rfm.simple_test
class SphExa_Extrae_Check(rfm.RegressionTest, hooks.setup_pe,
                          hooks.setup_code):
    # {{{
    '''
    This class runs the test code with Extrae (mpi+openmp):
    https://tools.bsc.es/extrae
    '''
    # }}}
    steps = parameter([2])
    compute_node = parameter([2])
    # compute_node = parameter([100, 200, 300, 400, 500])
    np_per_c = parameter([1e4])
    # extrae_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['Extrae']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.which_rpt = 'which.rpt'
        self.version_rpt = 'version.rpt'
        version_file = '$EBROOTEXTRAE/include/extrae_version.h'
        prepost_tool = 'papi_best_set'
        postproc_tool = 'stats-wrapper.sh'
        self.prebuild_cmds = [
            f'which {prepost_tool} &> {self.which_rpt}',
            f'ls {version_file} >> {self.which_rpt}',
            f'egrep "EXTRAE_MAJOR |EXTRAE_MINOR |EXTRAE_MICRO " {version_file}'
            f'&> {self.version_rpt}',
        ]
        # }}}

        # {{{ run
        self.postrun_cmds += [
            f'# -------------------------------------------------------------',
            f'{postproc_tool} *.prv -comms_histo',
            f'# use {prepost_tool} for unavailable PAPI hardware counters',
            f'# -------------------------------------------------------------',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool report:
            sn.assert_found(r'Congratulations! \S+ has been generated.',
                            self.stdout),
        ])
        # }}}

    # {{{ hooks
    # {{{ run
    @rfm.run_before('run')
    def set_tool_options(self):
        tool_scriptname = './extrae.sh'
        self.prerun_cmds += [
            f'# -------------------------------------------------------------',
            f'echo -e \'{sphsextrae.create_sh(self)}\' > {tool_scriptname}',
            f'chmod u+x {tool_scriptname}',
            f'cat {tool_scriptname}',
            f'# -------------------------------------------------------------',
        ]
        # run with: srun ... ./extrae.sh myexe ...
        self.job.launcher.options += [tool_scriptname]
    # }}}

    # {{{ performance
    @rfm.run_before('performance')
    def add_tool_perf_patterns(self):
        self.rpt_mpistats = f'{self.executable}.comms.dat'
        self.perf_patterns.update(sn.evaluate(sphsextrae.rpt_mpistats(self)))
    # }}}
# }}}
