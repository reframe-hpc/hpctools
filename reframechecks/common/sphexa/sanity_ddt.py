# Copyright 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict
import sphexa.sanity as sphs


class DDT_Base_Test(rfm.RegressionTest):
    def __init__(self):
        x = 0

    # {{{ set_sanity
    @run_before('sanity')
    def set_sanity(self):
        rpt = os.path.join(self.stagedir, self.htm_rpt)
        # {{{ sanity1
        # htm_rpt: >cubeSide: <img src="data:..." alt="Sparkline"/> 50 </td>
        regex1 = rf'{self.trace_var}: <img.*/> (\d+) </td>'
        res1 = sn.extractsingle(regex1, rpt, 1, int)
        self.cube_rpt = res1
        failure_msg1 = f'sanity1 failed: res={res1} ref={self.cubeside}'
        # }}}
        # {{{ sanity2
        # htm_rpt: <div>Add tracepoint for sedov.cpp:51 <br/>Vars: cubeSide
        regex2 = (
            r'Add tracepoint for (?P<res_fname>\S+):(?P<res_line>\d+).*Vars: '
            r'(?P<res_var>\S+)<'
        )
        res2 = sn.extractsingle(regex2, rpt, 3)
        failure_msg2 = f'sanity2 failed: res={res2} ref={self.trace_var}'
        # }}}
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool output:
            sn.assert_eq(res1, self.cubeside, msg=failure_msg1),
            sn.assert_eq(res2, self.trace_var, msg=failure_msg2),
        ])
    # }}}

    # {{{ set_txt_rpt
    @run_before('run')
    def set_txt_rpt(self):
        self.postrun_cmds += [
            f'# The html report can be converted to text with: '
            f'w3m -dump {self.htm_rpt} > {self.txt_rpt}',
            f'# It is also the same as running with: --output={self.txt_rpt}'
        ]
    # }}}

# {{{ performance patterns
    @run_before('performance')
    def set_tool_perf_patterns(self):
        '''
        More perf_patterns for the tool
        '''
        perf_pattern = {
            'ddt_cubeside': self.cube_rpt,
        }
        if self.perf_patterns:
            self.perf_patterns = {**self.perf_patterns, **perf_pattern}
        else:
            self.perf_patterns = perf_pattern

# }}}

# {{{ performance reference
    @run_before('performance')
    def set_tool_reference(self):
        ref = ScopedDict()
        # first, copy the existing self.reference (if any):
        if self.reference:
            for kk in self.reference:
                ref[kk] = self.reference['*:%s' % kk]

        # then add more for the tool:
        myzero = (0, None, None, '')
        # -----------------------------------------------------------
        ref['ddt_cubeside'] = myzero
        # final reference:
        self.reference = ref
# }}}
