# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict
import sphexa.sanity as sphs
import sphexa.sanity_intel as sphsintel


class VtuneBaseTest(rfm.RegressionTest):
    def __init__(self):
        x = 0

# {{{ others
    @rfm.run_before('performance')
    def get_vtune_num_result_path(self):
        regex = r'^vtune: Using result path .(?P<paths>\S+).$'
        rpt = os.path.join(self.stagedir, self.dir_rpt)
        self.vtune_paths = sn.evaluate(sn.count(sn.findall(regex, rpt)))
# }}}

# {{{ patterns
    # --- 1
    @rfm.run_before('performance')
    def set_basic_perf_patterns(self):
        '''A set of basic perf_patterns shared between the tests
        '''
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))

    # --- 2
    @rfm.run_before('performance')
    def set_vtune_perf_patterns_stdout(self):
        res = sn.evaluate(sphsintel.vtune_perf_patterns(self))
        if self.perf_patterns:
            self.perf_patterns = {**self.perf_patterns, **res}
        else:
            self.perf_patterns = res

    # --- 3
    @rfm.run_before('performance')
    def set_vtune_perf_patterns_rpt(self):
        '''More perf_patterns for the tool

        Typical performance reporting:

        .. literalinclude::
          ../../reframechecks/intel/intel_vtune.res
          :lines: 117-127

        '''
        regex_l = r'^vtune: Using result path .(?P<paths>\S+).$'
        paths_l = sn.extractall(regex_l, self.dir_rpt, 'paths')
        regex = (r'(?P<funcname>.*);(?P<cput>\d+.\d+);(?P<cput_efft>\S+);'
                 r'(?P<cput_spint>\S+);(?P<cput_overhead>\S+)')
        res = {}
        res2 = {}
        for ii in range(self.vtune_paths):
            rpt = paths_l[ii] + '.csv'  # rpt.nid00034.csv
            kk = 'vtune_cput_cn%s' % ii
            res[kk] = sn.round(sn.sum(sn.extractall(regex, rpt, 'cput',
                                                    float)), 2)
            kk = 'vtune_cput_cn%s_efft' % ii
            res2[kk] = sn.round(sn.sum(sn.extractall(regex, rpt, 'cput_efft',
                                                     float)), 2)
            kk = 'vtune_cput_cn%s_spint' % ii
            res2[kk] = sn.round(sn.sum(sn.extractall(regex, rpt, 'cput_spint',
                                                     float)), 2)
            kk = '%svtune_cput_cn%s_efft' % ('%', ii)
            res[kk] = sn.round(res2['vtune_cput_cn%s_efft' % ii] /
                               res['vtune_cput_cn%s' % ii] * 100, 1)
            kk = '%svtune_cput_cn%s_spint' % ('%', ii)
            res[kk] = sn.round(res2['vtune_cput_cn%s_spint' % ii] /
                               res['vtune_cput_cn%s' % ii] * 100, 1)
        if self.perf_patterns:
            self.perf_patterns = {**self.perf_patterns, **res}
        else:
            self.perf_patterns = res
# }}}

# {{{ reference
    # --- 1
    @rfm.run_before('performance')
    def set_basic_reference(self):
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))

    # --- 2
    @rfm.run_before('performance')
    def set_tool_reference_stdout(self):
        self.reference = sn.evaluate(sphsintel.vtune_tool_reference(self))

    # --- 3
    @rfm.run_before('performance')
    def set_tool_reference_rpt(self):
        ref = ScopedDict()
        # first, copy the existing self.reference (if any):
        if self.reference:
            for kk in self.reference:
                ref[kk] = self.reference['*:%s' % kk]

        # then add more:
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        for ii in range(self.vtune_paths):
            kk = '*:vtune_cput_cn%s' % ii
            ref[kk] = myzero_s
        # ok for ii in range(self.vtune_paths):
        # ok     kk = '*:vtune_cput_cn%s_efft' % ii
        # ok     ref[kk] = myzero_s
        # ok for ii in range(self.vtune_paths):
        # ok     kk = '*:vtune_cput_cn%s_spint' % ii
        # ok     ref[kk] = myzero_s
        for ii in range(self.vtune_paths):
            kk = '*:%svtune_cput_cn%s_efft' % ('%', ii)
            ref[kk] = myzero_p
            # ref['%vtune_cput_cn0_efft'] = myzero_p
        for ii in range(self.vtune_paths):
            kk = '*:%svtune_cput_cn%s_spint' % ('%', ii)
            ref[kk] = myzero_p
        # final reference:
        self.reference = ref
# }}}
