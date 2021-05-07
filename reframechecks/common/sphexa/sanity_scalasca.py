# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import cxxfilt
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ --- scorep.score: scalasca_mpi_pct / scalasca_omp_pct
@sn.sanity_function
def scalasca_mpi_pct(obj):
    '''MPI % reported by Scalasca (scorep.score, notice no hits column)

    .. code-block::

         type max_buf[B]  visits time[s] time[%] time/visit[us]  region
         ALL  6,529,686 193,188   28.13   100.0         145.63  ALL
         OMP  6,525,184 141,056   27.33    97.1         193.74  OMP
         MPI      4,502      73    0.02     0.1         268.42  MPI
                                          *****
    '''
    regex = r'^\s+MPI.* (?P<pct>\S+)\s+\S+\s+MPI'
    return sn.extractsingle(regex, obj.rpt_score, 'pct', float)


@sn.sanity_function
def scalasca_omp_pct(obj):
    '''OpenMP % reported by Scalasca (scorep.score, notice no hits column)

    .. code-block::

         type max_buf[B]  visits time[s] time[%] time/visit[us]  region
         ALL  6,529,686 193,188   28.13   100.0         145.63  ALL
         OMP  6,525,184 141,056   27.33    97.1         193.74  OMP
                                          *****
         MPI      4,502      73    0.02     0.1         268.42  MPI
    '''
    regex = r'^\s+OMP.* (?P<pct>\S+)\s+\S+\s+OMP'
    return sn.extractsingle(regex, obj.rpt_score, 'pct', float)
# }}}


# {{{ trace.stat: rpt_trace_stats_mpi
@sn.sanity_function
def rpt_tracestats_mpi(obj):
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
# }}}


# {{{ trace.stat: rpt_trace_stats_omp
@sn.sanity_function
def rpt_tracestats_omp(obj):
    '''Reports OpenMP statistics by reading the trace.stat file:
    - omp_ibarrier_wait: OMP Wait at Implicit Barrier (sec) in Cube GUI
    - omp_lock_contention_critical: OMP Critical Contention (sec) in Cube GUI
    Each column (Count Mean Median Minimum Maximum Sum Variance Quartil25 and
    Quartil75) is read, only Sum is reported here.
    '''
    regex_omp_ibarrier = r'^omp_ibarrier_wait\s+(\S+\s+){5}(?P<Sum>\S+)'
    regex_omp_lock = r'^omp_lock_contention_critical\s+(\S+\s+){5}(?P<Sum>\S+)'
    #
    omp_ibarrier = sn.extractsingle(regex_omp_ibarrier, obj.stat_rpt, 'Sum',
                                    float)
    omp_lock = sn.extractsingle(regex_omp_lock, obj.stat_rpt, 'Sum', float)
    #
    n_procs = obj.compute_node * obj.num_tasks_per_node * obj.omp_threads
    res_d = {
        'omp_ibarrier': sn.round(omp_ibarrier / n_procs, 4),
        'omp_lock': sn.round(omp_lock / n_procs, 4),
    }
    return res_d
# }}}
