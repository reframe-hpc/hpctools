# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
# import numpy as np
from reframe.core.fields import ScopedDict
import sphexa.sanity as sphs


class LikwidBaseTest(rfm.RegressionTest):
    def __init__(self):
        x = 0

# {{{ sanity patterns
    # {{{ tool_version
    @rfm.run_before('sanity')
    def likwid_sanity_patterns(self):
        '''Checks tool's version and sanity_patterns:

        .. code-block::

          > likwid-perfctr --version
          likwid-perfctr -- Version 5.0.1 (commit: 233ab9...)
        '''
        reference_tool_version = {
            'daint': '5.0.1',
            'dom': '5.0.1',
        }
        ref_version = reference_tool_version[self.current_system.name]
        regex = r'likwid-perfctr -- Version (?P<toolversion>\S+) \('
        res_version = sn.extractsingle(regex, self.version_rpt, 'toolversion')
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool version:
            sn.assert_eq(res_version, ref_version),
        ])
        # TODO: self.sanity_patterns.append ?
    # }}}
# }}}

# {{{ performance patterns
    # --- 1
    @rfm.run_before('performance')
    def set_basic_perf_patterns(self):
        '''A set of basic perf_patterns shared between the tests
        '''
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))

# {{{ --- 2
    @rfm.run_before('performance')
    def set_tool_perf_patterns(self):
        '''More perf_patterns for the tool

        Typical performance reporting:

        .. literalinclude:: ../../reframechecks/perftools/patrun.res
          :lines: 141-169

        '''
        regex = r'^\|\s+Runtime \(RDTSC\) \[s\]\s+\|\s+(?P<sec>\S+)\s+\|'
        res_runtime = sn.extractsingle(regex, self.stdout, 'sec', float)
        regex = r'^\|\s+CPI\s+\|\s+(?P<cpi>\S+)\s+\|'
        res_cpi = sn.extractsingle(regex, self.stdout, 'cpi', float)
        if self.group == 'CLOCK':
            # CLOCK:
            regex = r'^\|\s+Energy \[J\]\s+\|\s+(?P<J>\S+)\s+\|'
            res_energy = sn.extractsingle(regex, self.stdout, 'J', float)
            regex = r'^\|\s+Power \[W\]\s+\|\s+(?P<W>\S+)\s+\|'
            res_power = sn.extractsingle(regex, self.stdout, 'W', float)
            perf_pattern = {
                'likwid_runtime': res_runtime,
                'likwid_cpi': res_cpi,
                # power/energy:
                'likwid_energy': res_energy,
                'likwid_power': res_power,
            }

        if self.group == 'MEM':
            # MEM:
            regex = (r'^\|\s+Memory bandwidth \[MBytes/s\]\s+\|\s+'
                     r'(?P<MBperSec>\S+)\s+\|')
            res_mem_bw = sn.extractsingle(regex, self.stdout, 'MBperSec',
                                          float)
            regex = (r'^\|\s+Memory data volume \[GBytes\]\s+\|\s+'
                     r'(?P<GB>\S+)\s+\|')
            res_mem_gb = sn.extractsingle(regex, self.stdout, 'GB', float)
            perf_pattern = {
                'likwid_runtime': res_runtime,
                'likwid_cpi': res_cpi,
                # memory:
                'likwid_memory_bw': res_mem_bw,
                'likwid_memory': res_mem_gb,
            }

        if self.group == 'TMA':
            # TMA:
            regex = r'^\|\s+Front End \[%\]\s+\|\s+(?P<pct>\S+)\s+\|'
            res_frontend = sn.extractsingle(regex, self.stdout, 'pct', float)
            regex = r'^\|\s+Speculation \[%\]\s+\|\s+(?P<pct>\S+)\s+\|'
            res_speculation = sn.extractsingle(regex, self.stdout, 'pct',
                                               float)
            regex = r'^\|\s+Retiring \[%\]\s+\|\s+(?P<pct>\S+)\s+\|'
            res_retiring = sn.extractsingle(regex, self.stdout, 'pct', float)
            regex = r'^\|\s+Back End \[%\]\s+\|\s+(?P<pct>\S+)\s+\|'
            res_backend = sn.extractsingle(regex, self.stdout, 'pct', float)
            perf_pattern = {
                'likwid_runtime': res_runtime,
                'likwid_cpi': res_cpi,
                # topdown:
                '%likwid_topdown_frontend': res_frontend,
                '%likwid_topdown_speculation': res_speculation,
                '%likwid_topdown_retiring': res_retiring,
                '%likwid_topdown_backend': res_backend,
            }

        if self.perf_patterns:
            self.perf_patterns = {**self.perf_patterns, **perf_pattern}
        else:
            self.perf_patterns = perf_pattern

# }}}
# }}}

# {{{ performance reference
    # --- 1
    @rfm.run_before('performance')
    def set_basic_reference(self):
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))

# {{{ --- 2
    @rfm.run_before('performance')
    def set_mpip_reference(self):
        ref = ScopedDict()
        # first, copy the existing self.reference (if any):
        if self.reference:
            for kk in self.reference:
                ref[kk] = self.reference['*:%s' % kk]

        # then add more:
        myzero = (0, None, None, '')
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        myzero_j = (0, None, None, 'J')
        myzero_w = (0, None, None, 'W')
        myzero_mbs = (0, None, None, 'MBytes/s')
        myzero_gb = (0, None, None, 'GBytes')
        ref['likwid_runtime'] = myzero_s
        ref['likwid_cpi'] = myzero
        if self.group == 'CLOCK':
            ref['likwid_energy'] = myzero_j
            # power/energy:
            ref['likwid_energy'] = myzero_j
            ref['likwid_power'] = myzero_w

        if self.group == 'MEM':
            # memory:
            ref['likwid_memory_bw'] = myzero_mbs
            ref['likwid_memory'] = myzero_gb

        if self.group == 'TMA':
            # topdown:
            ref['%likwid_topdown_frontend'] = myzero_p
            ref['%likwid_topdown_speculation'] = myzero_p
            ref['%likwid_topdown_retiring'] = myzero_p
            ref['%likwid_topdown_backend'] = myzero_p
        #
        self.reference = ref
# }}}
# }}}
