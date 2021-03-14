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


# {{{ class SphExa_timers
@rfm.simple_test
class SphExa_Timers_Check(rfm.RegressionTest, hooks.setup_pe,
                          hooks.setup_code):
    steps = parameter([0])
    compute_node = parameter([1])
    np_per_c = parameter([1e4])

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            'PrgEnv-aocc', 'cpeAMD', 'cpeCray', 'cpeGNU', 'cpeIntel']
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype'}
        # }}}

        # {{{ run
        self.testname = 'sedov'
        self.time_limit = '10m'
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
        ])
        # }}}

        # {{{ performance
        # see common/sphexa/hooks.py
        # }}}
