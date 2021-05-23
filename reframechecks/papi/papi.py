# Copyrigh 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn


# {{{ class Papi_Check
@rfm.simple_test
class Papi_Check(rfm.RegressionTest):
    # compute_node = parameter([1])

    def __init__(self):
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
        self.sourcepath = 'papi_hw_info.c'
        self.modules = ['papi']
        self.tool = 'papi_version'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prebuild_cmds = [
            'module list', 'srun --version',
            f'{self.tool} &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]

    @rfm.run_before('sanity')
    def set_sanity(self):
        reference_hwinfo = {
            # bwl: Intel(R) Xeon(R) CPU E5-2695 v4 @ 2.10GHz (vendor 1)
            'dom:mc': 36,
            'daint:mc': 36,
            # hwl: Intel(R) Xeon(R) CPU E5-2690 v3 @ 2.60GHz (vendor 1)
            'dom:gpu': 12,
            'daint:gpu': 12,
            # AMD EPYC 7742 64-Core Processor (vendor 2)
            'eiger:mc': 128,
            'pilatus:mc': 128,
        }
        cp = self.current_partition.fullname
        regex = r'^physical_cores\s+\|(?P<cores>\d+)'
        phy_cores = sn.extractsingle(regex, self.stdout, 'cores', int)
        self.sanity_patterns = sn.all([
            # check the tool output:
            sn.assert_found(r'PAPI Version: \S+', self.version_rpt),
            # check the code output:
            sn.assert_eq(phy_cores, reference_hwinfo[cp]),
        ])
