# Copyright 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
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
    # steps = parameter([0])
    # compute_node = parameter([1])
    # np_per_c = parameter([1e4])
    # memory usage:
    # steps = parameter([1])
    # compute_node = parameter([1])
    # np_per_c = parameter([1e4, 2e4, 4e4, 6e4, 8e4,
    #                       1e5, 2e5, 4e5, 6e5, 8e5, 1e6, 2e6])
    # weak scaling:
    steps = parameter([25])
    compute_node = parameter([1, 2, 4, 8, 16, 32])
    np_per_c = parameter([2e5])

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            'PrgEnv-nvidia',
            'PrgEnv-aocc', 'cpeAMD', 'cpeCray', 'cpeGNU', 'cpeIntel']
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc', 'archer2:compute',
        ]
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype'}
        # }}}

        # {{{ run
        self.testname = 'sedov'
        self.time_limit = '20m'
        # self.executable = 'mpi+omp'
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
