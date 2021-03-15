# Copyrigh 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.launchers import LauncherWrapper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.hooks as hooks
# import sphexa.sanity as sphs
import sphexa.sanity_perftools as sphsperft


# {{{ class SphExa_PatRun
@rfm.simple_test
# class SphExa_PatRun_Check(rfm.RegressionTest, hooks.setup_pe,
class SphExa_PatRun_Check(sphsperft.PerftoolsBaseTest, hooks.setup_pe,
                          hooks.setup_code):
    # {{{
    '''This class runs the test code with CrayPAT (Cray Performance Measurement
    and Analysis toolset):

        * https://pubs.cray.com (Cray Perftools)
        * man pat_run
        * man intro_craypat
        * ``pat_help``
    '''
    # }}}
    steps = parameter([1])
    compute_node = parameter([1])
    # compute_node = parameter([2**i for i in range(8)])  # 1:128 cn
    np_per_c = parameter([1e4])

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            'PrgEnv-aocc', 'cpeGNU', 'cpeIntel', 'cpeAMD', 'cpeCray',
        ]
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.tool = 'pat_run'
        self.modules = ['perftools-preload']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype', 'performance'}
        # }}}

        # {{{ run
        self.testname = 'sedov'
        self.time_limit = '10m'
        self.executable = self.tool
        self.target_executable = './mpi+omp'
        # }}}

        # -r: generates a report upon successful execution
        # TODO: read rpt-files/RUNTIME.rpt
        self.executable_opts = ['-r', self.target_executable]
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.csv_rpt = 'csv.rpt'
        self.rpt = 'rpt'
        self.prerun_cmds = [
            f'srun --version > {self.version_rpt}',
            f'{self.tool} -V >> {self.version_rpt} 2>&1',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        # convert report to csv for some sanity functions:
        csv_options = ('-v -O load_balance_group -s sort_by_pe=\'yes\' '
                       '-s show_data=\'csv\' -s pe=\'ALL\'')
        self.postrun_cmds += [
            # patrun_num_of_compute_nodes
            f'ls -1 {self.target_executable}+*s/xf-files/',
            f'cp *_job.out {self.rpt}',
            f'pat_report {csv_options} %s+*s/index.ap2 &> %s' %
            (self.target_executable, self.csv_rpt)
        ]

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
        ])
        # }}}
#         # {{{ sanity
#         self.sanity_patterns_l = [
#             sn.assert_found(r'Total time for iteration\(0\)', self.stdout)
#         ]
#         # will also silently call patrun_version (in sanity_perftools.py)
#         self.sanity_patterns = sn.all(self.sanity_patterns_l)
#         # }}}

        # {{{ performance
        # see common/sphexa/hooks.py and common/sphexa/sanity_perftools.py
        # }}}

    # {{{ hooks
    # @rfm.run_before('performance')
    # def set_(self):
    # }}}
# }}}
