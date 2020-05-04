# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import cxxfilt
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


@sn.sanity_function
def rpt_trace_stats_d(obj):
    '''Reports MPI statistics (mpi_latesender, mpi_latesender_wo,
    mpi_latereceiver, mpi_wait_nxn, mpi_nxn_completion) by reading the stat_rpt
    (``trace.stat``) file reported by the tool. Columns are (for each
    PatternName): Count Mean Median Minimum Maximum Sum Variance Quartil25 and
    Quartil75. Count (=second column) is used here.

    Typical performance reporting:

    .. literalinclude::
      ../../reframechecks/scalasca/res/scalasca_sampling_tracing.res
      :lines: 33-36, 40, 43, 48, 55
    '''
    regex_latesender = r'^mpi_latesender\s+(?P<cnt>\d+)\s'
    regex_latesender_wo = r'^mpi_latesender_wo\s+(?P<cnt>\d+)\s'
    regex_latereceiver = r'^mpi_latereceiver\s+(?P<cnt>\d+)\s'
    regex_wait_nxn = r'^mpi_nxn_completion\s+(?P<cnt>\d+)\s'
    #
    latesender = sn.extractsingle(regex_latesender, obj.stat_rpt, 'cnt', int)
    latesender_wo = sn.extractsingle(regex_latesender_wo, obj.stat_rpt,
                                     'cnt', int)
    latereceiver = sn.extractsingle(regex_latereceiver, obj.stat_rpt,
                                    'cnt', int)
    wait_nxn = sn.extractsingle(regex_wait_nxn, obj.stat_rpt, 'cnt', int)
    #
    res_d = {
        'mpi_latesender': latesender,
        'mpi_latesender_wo': latesender_wo,
        'mpi_latereceiver': latereceiver,
        'mpi_wait_nxn': wait_nxn,
    }
    return res_d
