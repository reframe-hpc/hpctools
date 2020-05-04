# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict
import sphexa.sanity as sphs
# import sphexa.sanity_intel as sphsintel


class MpipBaseTest(rfm.RegressionTest):
    def __init__(self):
        x = 0

# {{{ others
    @rfm.run_before('sanity')
    def rpt_file_txt(self):
        # As the report output file is hardcoded ( using getpid:
        # https://github.com/LLNL/mpiP/blob/master/mpiPi.c#L935 ), i.e changing
        # at every job, it's needed to extract the filename from stdout:
        self.rpt = sn.extractsingle(
            r'^mpiP: Storing mpiP output in \[(?P<rpt>.*)\]',
            self.stdout, 'rpt', str)
# }}}

# {{{ sanity patterns
    @rfm.run_before('sanity')
    def mpip_version(self):
        '''Checks tool's version:

        .. code-block::

          > cat ./sqpatch.exe.6.31820.1.mpiP
          @ mpiP
          @ Command : sqpatch.exe -n 62 -s 1
          @ Version                  : 3.4.2  <---
          @ MPIP Build date          : Oct 15 2019, 16:52:21
        '''
        reference_tool_version = {
            'daint': '3.4.2',
            'dom': '3.4.2',
        }
        ref_version = reference_tool_version[self.current_system.name]
        regex = r'^@ Version\s+: (?P<toolversion>\S+)$'
        version = sn.extractsingle(regex, self.rpt, 'toolversion')
        self.sanity_patterns_l.append(
            sn.assert_eq(version, ref_version)
        )
# }}}

# {{{ performance patterns
    # --- 1
    @rfm.run_before('performance')
    def set_basic_perf_patterns(self):
        '''A set of basic perf_patterns shared between the tests
        '''
        self.perf_patterns = sn.evaluate(sphs.basic_perf_patterns(self))

    # --- 2
    @rfm.run_before('performance')
    def set_mpip_perf_patterns(self):
        '''More perf_patterns for the tool

    .. code-block::

      -----------------------------------
      @--- MPI Time (seconds) -----------
      -----------------------------------
      Task    AppTime    MPITime     MPI%
         0        8.6      0.121     1.40 <-- min
         1        8.6      0.157     1.82
         2        8.6       5.92    68.84 <-- max
         *       25.8        6.2    24.02 <---

      => NonMPI= AppTime - MPITime

    Typical performance reporting:

    .. code-block::

      * mpip_avg_app_time: 8.6 s  (= 25.8/3mpi)
      * mpip_avg_mpi_time: 2.07 s (=  6.2/3mpi)
      * %mpip_avg_mpi_time: 24.02 %
      * %mpip_avg_non_mpi_time: 75.98 %
        '''
        regex_star = r'^\s+\*\s+(?P<appt>\S+)\s+(?P<mpit>\S+)\s+(?P<pct>\S+)$'
        app_t = sn.extractsingle(regex_star, self.rpt, 'appt', float)
        mpi_t = sn.extractsingle(regex_star, self.rpt, 'mpit', float)
        mpi_pct = sn.extractsingle(regex_star, self.rpt, 'pct', float)
        nonmpi_pct = sn.round(100 - mpi_pct, 2)
        # min/max
        regex = (r'^\s+(?P<mpirk>\S+)\s+(?P<appt>\S+)\s+(?P<mpit>\S+)\s+'
                 r'(?P<pct>\S+)$')
        mpi_pct_max = sn.max(sn.extractall(regex, self.rpt, 'pct', float))
        mpi_pct_min = sn.min(sn.extractall(regex, self.rpt, 'pct', float))
        perf_pattern = {
            'mpip_avg_app_time': sn.round(app_t / self.num_tasks, 2),
            'mpip_avg_mpi_time': sn.round(mpi_t / self.num_tasks, 2),
            '%mpip_avg_mpi_time': mpi_pct,
            '%mpip_avg_mpi_time_max': mpi_pct_max,
            '%mpip_avg_mpi_time_min': mpi_pct_min,
            '%mpip_avg_non_mpi_time': nonmpi_pct,
        }
        if self.perf_patterns:
            self.perf_patterns = {**self.perf_patterns, **perf_pattern}
        else:
            self.perf_patterns = perf_pattern
# }}}

# {{{ performance reference
    # --- 1
    @rfm.run_before('performance')
    def set_basic_reference(self):
        self.reference = sn.evaluate(sphs.basic_reference_scoped_d(self))

    # --- 2
    @rfm.run_before('performance')
    def set_mpip_reference(self):
        ref = ScopedDict()
        # first, copy the existing self.reference (if any):
        if self.reference:
            for kk in self.reference:
                ref[kk] = self.reference['*:%s' % kk]

        # then add more:
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        ref['mpip_avg_app_time'] = myzero_s
        ref['mpip_avg_mpi_time'] = myzero_s
        ref['%mpip_avg_mpi_time'] = myzero_p
        ref['%mpip_avg_non_mpi_time'] = myzero_p
        ref['%mpip_avg_mpi_time_max'] = myzero_p
        ref['%mpip_avg_mpi_time_min'] = myzero_p
        # final reference:
        self.reference = ref
# }}}
