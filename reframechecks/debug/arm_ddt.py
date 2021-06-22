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
import sphexa.sanity_ddt as sphsddt


# {{{ class SphExa_DDT_Check
@rfm.simple_test
class SphExa_DDT_Check(sphsddt.DDT_Base_Test, hooks.setup_pe,
                       hooks.setup_code):
    # {{{
    '''
    This class runs the test code with ARM DDT:
    https://developer.arm.com/tools-and-software/server-and-hpc
    '''
    # }}}
    steps = parameter([0])
    compute_node = parameter([1])
    np_per_c = parameter([1e3])
    debug_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'cpeGNU'
            # 'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            # 'PrgEnv-aocc', 'cpeGNU', 'cpeIntel', 'cpeCray', 'cpeAMD',
        ]
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.tool = 'ddt'
        self.modules = [self.tool]
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype', 'debugging'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.sourcepath = f'{self.testname}.cpp'
        # }}}

        # {{{ run
        self.time_limit = '10m'
        self.lic_rpt = 'license.rpt'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.htm_rpt = 'rpt_ddt.html'
        self.txt_rpt = 'rpt_ddt.txt'
        self.prerun_cmds = [
            f'cat $EBROOTDDT/licences/Licence > {self.lic_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            f'srun --version > {self.version_rpt}',
            f'{self.tool} --version >> {self.version_rpt}',
        ]
        # }}}

        # {{{ sanity: see hook
        # }}}
        # {{{ performance
        # see common/sphexa/hooks.py and sanity_ddt.py
        # }}}

    # {{{ hooks
    # {{{ set_launcher
    @run_before('run')
    def set_tracepoint_and_launcher(self):
        # break in main at line 51:
        #   auto d = SedovDataGenerator<Real, CodeType>::generate(cubeSide);
        linen = 51
        self.trace_var = 'cubeSide'
        tracepoint = rf'"{self.sourcepath}:{linen},{self.trace_var}"'
        # recommending tracepoint but this will work too:
        # --break-at %s:%d --evaluate="cubeSide"
        # The debugger must be launch with: ddt --offline srun ... exe ...
        self.ddt_options = ['--offline', f'--output={self.htm_rpt}',
                            '--trace-at', tracepoint]
        self.job.launcher = LauncherWrapper(self.job.launcher, self.tool,
                                            self.ddt_options)
    # }}}
    # }}}
# }}}
