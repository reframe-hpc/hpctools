# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import json
import cxxfilt
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ sanity_function: scorep_version / scorep_assert_version
@sn.sanity_function
def scorep_version(obj):
    '''Checks tool's version:

    .. code-block::

      > scorep --version
      Score-P 7.0
      returns: version string
    '''
    regex = r'^Score-P\s(?P<toolsversion>\d.\d)'
    version = sn.extractsingle(regex, obj.version_rpt, 'toolsversion')
    return version


@sn.sanity_function
def scorep_assert_version(obj):
    '''Checks tool's version:

    .. code-block::

      > scorep --version
      Score-P 6.0
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '6.0',
        'dom': '6.0',
        'tave': '6.0',
    }
    regex = r'^Score-P\s(?P<toolsversion>\d.\d)'
    version = sn.extractsingle(regex, obj.version_rpt, 'toolsversion')
    TorF = sn.assert_eq(
        version, reference_tool_version[obj.current_system.name])
    # print('version=%s' % version)
    # print('ref_version=%s' % reference_tool_version[obj.current_system.name])
    return TorF
# }}}


# {{{ --- scorep-info:
def scorep_assert_eq(obj, title, regex):
    tool_version = scorep_version(obj)
    if tool_version == '6.0':
        nm_ref = 3
    else:
        nm_ref = 1

    nm = sn.count(sn.extractall(regex, obj.info_rpt, 'yn'))
    failure_msg = f'{title} failed: (nm={nm}) != (nm_ref={nm_ref})'
    TorF = sn.assert_eq(nm, nm_ref, msg=failure_msg)
    return TorF


@sn.sanity_function
def scorep_info_papi_support(obj):
    '''Checks tool's configuration (papi support)

    .. code-block::

      > scorep-info config-summary
      PAPI support: yes
    '''
    regex = r'^\s+PAPI support:\s+(?P<yn>yes)'
    return scorep_assert_eq(obj, 'scorep_info_papi_support', regex)


@sn.sanity_function
def scorep_info_perf_support(obj):
    '''Checks tool's configuration (perf support)

    .. code-block::

      > scorep-info config-summary
      metric perf support: yes
    '''
    regex = r'^\s+metric perf support:\s+(?P<yn>yes)'
    return scorep_assert_eq(obj, 'scorep_info_perf_support', regex)


@sn.sanity_function
def scorep_info_unwinding_support(obj):
    '''Checks tool's configuration (libunwind support)

    .. code-block::

      > scorep-info config-summary
      Unwinding support: yes
    '''
    regex = r'^\s+Unwinding support:\s+(?P<yn>\w+)'
    return scorep_assert_eq(obj, 'scorep_info_unwinding_support', regex)


@sn.sanity_function
def scorep_info_cuda_support(obj):
    '''Checks tool's configuration (Cuda support)

    .. code-block::

      > scorep-info config-summary
      CUDA support:  yes
    '''
    regex = r'^\s+CUDA support:\s+(?P<yn>\w+)'
    return scorep_assert_eq(obj, 'scorep_info_cuda_support', regex)
# }}}


# {{{ --- profiling:
@sn.sanity_function
def scorep_elapsed(obj):
    '''Typical performance report from the tool (profile.cubex)

    .. code-block::

         type max_buf[B]   visits    hits time[s] time[%] time/visit[us] region
         ALL  1,019,921 2,249,107 934,957  325.00   100.0   144.50  ALL
                                           ******
         USR    724,140 1,125,393 667,740  226.14    69.6   200.94  USR
         MPI    428,794    59,185 215,094   74.72    23.0  1262.56  MPI
         COM     43,920 1,061,276  48,832   21.96     6.8    20.69  COM
      MEMORY      9,143     3,229   3,267    2.16     0.7   669.59  MEMORY
      SCOREP         94        24      24    0.01     0.0   492.90  SCOREP
         USR    317,100   283,366 283,366   94.43    29.1         333.24 ...
      _ZN6sphexa3sph31computeMomentumAndEnergyIADImplIdNS_13ParticlesData ...
      IdEEEEvRKNS_4TaskERT0_
    '''
    regex = r'^\s+ALL\s+.* (?P<seconds>\d+\.\d+)\s+100.0'
    result = sn.extractsingle(regex, obj.rpt_score, 'seconds', float)
    n_procs = obj.compute_node * obj.num_tasks_per_node * obj.omp_threads
    return sn.round(result / n_procs, 4)


@sn.sanity_function
def scorep_mpi_pct(obj):
    '''Reports MPI % measured by the tool

    .. code-block::

         type max_buf[B]   visits    hits time[s] time[%] time/visit[us] region
         MPI    428,794    59,185 215,094   74.72    23.0  1262.56  MPI
                                                     ****
    '''
    regex = r'^\s+MPI(\s+\S+){4}\s+(?P<pct>\d+\D\d+)\s+\d+(\D\d+)?\s+MPI'
    return sn.extractsingle(regex, obj.rpt_score, 'pct', float)


@sn.sanity_function
def scorep_usr_pct(obj):
    '''Reports USR % measured by the tool

    .. code-block::

         type max_buf[B]   visits    hits time[s] time[%] time/visit[us] region
         USR    724,140 1,125,393 667,740  226.14    69.6   200.94  USR
                                                     ****
    '''
    regex = r'^\s+USR(\s+\S+){4}\s+(?P<pct>\d+\D\d+)\s+\d+(\D\d+)?\s+USR'
    return sn.extractsingle(regex, obj.rpt_score, 'pct', float)


@sn.sanity_function
def scorep_com_pct(obj):
    '''Reports COM % measured by the tool

    .. code-block::

         type max_buf[B]   visits    hits time[s] time[%] time/visit[us] region
         COM      4,680 1,019,424     891  303.17    12.0         297.39  COM
                                                     ****
    '''
    regex = r'^\s+COM(\s+\S+){4}\s+(?P<pct>\d+\D\d+)\s+\d+(\D\d+)?\s+COM'
    return sn.extractsingle(regex, obj.rpt_score, 'pct', float)


@sn.sanity_function
def scorep_omp_pct(obj):
    '''Reports OMP % measured by the tool

    .. code-block::

         type max_buf[B]   visits    hits time[s] time[%] time/visit[us] region
         OMP 40,739,286 3,017,524 111,304 2203.92    85.4         730.37  OMP
                                                     ****
    '''
    regex = r'^\s+OMP(\s+\S+){4}\s+(?P<pct>\d+\D\d+)\s+\d+(\D\d+)?\s+OMP'
    return sn.extractsingle(regex, obj.rpt_score, 'pct', float)


@sn.sanity_function
def scorep_top1_name(obj):
    '''Reports demangled name of top1 function name, for instance:

    .. code-block::

      > c++filt ...
      _ZN6sphexa3sph31computeMomentumAndEnergyIADImplIdNS_13 ...
      ParticlesDataIdEEEEvRKNS_4TaskERT0_

      void sphexa::sph::computeMomentumAndEnergyIADImpl  ...
            <double, sphexa::ParticlesData<double> > ...
            (sphexa::Task const&, sphexa::ParticlesData<double>&)
    '''
    regex = r'^\s{9}(USR|COM).*\s+(?P<pct>\S+)\s+\S+\s+(?P<fn>_\w+)'
    rpt = os.path.join(obj.stagedir, obj.rpt_score)
    result = cxxfilt.demangle(sn.evaluate(sn.extractsingle(regex, rpt, 'fn')))
    # print("fn=", result)
    return ('% (' + result.split('<')[0] + ')')


@sn.sanity_function
def scorep_top1_tracebuffersize(obj):
    '''Reports max_buf[B] for top1 function

    .. code-block::

         type max_buf[B]   visits    hits time[s] time[%] time/visit[us] region
         ...
         USR    317,100   283,366 283,366   94.43    29.1         333.24 ...
      _ZN6sphexa3sph31computeMomentumAndEnergyIADImplIdNS_13ParticlesData ...

         USR    430,500    81,902  81,902   38.00     1.5         463.99  ...
      gomp_team_barrier_wait_end
    '''
    # regex = r'^\s{9}(USR|COM).*\s+(?P<pct>\S+)\s+\S+\s+(?P<fn>_\w+)'
    # regex = r'SCOREP\n\n\s+\S+\s+(?P<buf_B>\S+).*(?P<fn> \S+)\n'
    regex = r'^\n\s{9}\S+\s+(?P<buf_B>\S+).*(?P<fn> \S+)\n'
    rpt = os.path.join(obj.stagedir, obj.rpt_score)
    try:
        result = sn.extractsingle(
            regex, rpt, 'buf_B',
            conv=lambda x: int(x.replace(',', '').split('.')[0]))
    except Exception as e:
        printer.error(f'scorep_top1_tracebuffersize failed: {e}')
        result = 0

    return result


@sn.sanity_function
def scorep_top1_tracebuffersize_name(obj):
    '''Reports function name for top1 (max_buf[B]) function
    '''
    regex = r'^\n\s{9}\S+\s+(?P<buf_B>\S+).*(?P<fn> \S+)\n'
    rpt = os.path.join(obj.stagedir, obj.rpt_score)
    try:
        result = sn.extractsingle(regex, rpt, 'fn')
    except Exception as e:
        printer.error(f'scorep_top1_tracebuffersize_name failed: {e}')
        result = ''

    return result


@sn.sanity_function
def scorep_exclusivepct_energy(obj):
    '''Reports % of elapsed time (exclusive) for MomentumAndEnergy function
    (small scale job)

    .. code-block::

      > sqpatch_048mpi_001omp_125n_10steps_1000000cycles/rpt.exclusive
      0.0193958 (0.0009252%) sqpatch.exe
      1.39647 (0.06661%)       + main
      ...
      714.135 (34.063%)   |   + ...
               *******
        _ZN6sphexa3sph31computeMomentumAndEnergyIADImplIdNS_13 ...
        ParticlesDataIdEEEEvRKNS_4TaskERT0_
      0.205453 (0.0098%)  |   +
        _ZN6sphexa3sph15computeTimestepIdNS0_21TimestepPress2ndOrderIdNS_13 ...
        ParticlesDataIdEEEES4_EEvRKSt6vectorINS_4TaskESaIS7_EERT1_
      201.685 (9.62%)     |   |   + MPI_Allreduce


       type max_buf[B]    visits    hits time[s] time[%] time/visit[us]  region
       OMP  1,925,120    81,920       0   63.84     2.5         779.29
        !$omp parallel @momentumAndEnergyIAD.hpp:87 ***
       OMP    920,500    81,920  48,000  125.41     5.0        1530.93
        !$omp for @momentumAndEnergyIAD.hpp:87      ***
       OMP    675,860    81,920       1   30.95     1.2         377.85
        !$omp implicit barrier @momentumAndEnergyIAD.hpp:93
                                                    ***
    '''
    # regex = r'^\s+\S+(\s+\S+){4}\s+(?P<pct>\S+).*@momentumAndEnergyIAD'
    regex = r'^\d+.\d+\s+\((?P<pct>\d+.\d+).*momentumAndEnergyIAD'
    try:
        result = sn.round(sn.sum(sn.extractall(
            regex, obj.rpt_exclusive, 'pct', float)), 2)
    except Exception as e:
        printer.error(f'scorep_exclusivepct_energy failed: {e}')
        result = 0

    return result


@sn.sanity_function
def scorep_inclusivepct_energy(obj):
    '''Reports % of elapsed time (inclusive) for MomentumAndEnergy function
    (small scale job)

    .. code-block::

      > sqpatch_048mpi_001omp_125n_10steps_1000000cycles/rpt.exclusive
      0.0193958 (0.0009252%) sqpatch.exe
      1.39647 (0.06661%)       + main
      ...
      714.135 (34.063%)   |   + ...
               *******
        _ZN6sphexa3sph31computeMomentumAndEnergyIADImplIdNS_13 ...
        ParticlesDataIdEEEEvRKNS_4TaskERT0_
      0.205453 (0.0098%)  |   +
        _ZN6sphexa3sph15computeTimestepIdNS0_21TimestepPress2ndOrderIdNS_13 ...
        ParticlesDataIdEEEES4_EEvRKSt6vectorINS_4TaskESaIS7_EERT1_
      201.685 (9.62%)     |   |   + MPI_Allreduce
    '''
    # regex = r'^\d+.\d+ \((?P<pct>\d+.\d+).*computeMomentumAndEnergy'
    # return sn.extractsingle(regex, obj.rpt_inclusive, 'pct', float)
    regex = r'^\d+.\d+\s+\((?P<pct>\d+.\d+).*momentumAndEnergyIAD'
    try:
        result = sn.round(sn.sum(sn.extractall(
            regex, obj.rpt_inclusive, 'pct', float)), 2)
    except Exception as e:
        printer.error(f'scorep_inclusivepct_energy failed: {e}')
        result = 0

    return result
# }}}


# {{{ --- tracing:
@sn.sanity_function
def program_begin_count(obj):
    '''Reports the number of ``PROGRAM_BEGIN`` in the otf2 trace file
    '''
    pg_begin_count = sn.count(sn.findall(r'^(?P<wl>PROGRAM_BEGIN)\s+',
                                         obj.rpt_otf2))
    return pg_begin_count


@sn.sanity_function
def program_end_count(obj):
    '''Reports the number of ``PROGRAM_END`` in the otf2 trace file
    '''
    pg_end_count = sn.count(sn.findall(r'^(?P<wl>PROGRAM_END)\s+',
                                       obj.rpt_otf2))
    return pg_end_count


@sn.sanity_function
def ru_maxrss_rk0(obj):
    '''Reports the ``maximum resident set size``
    '''
    maxrss_rk0 = sn.max(sn.extractall(
        r'^METRIC\s+0\s+.*ru_maxrss\" <2>; UINT64; (?P<rss>\d+)\)',
        obj.rpt_otf2, 'rss', int))
    return maxrss_rk0


@sn.sanity_function
def ipc_rk0(obj):
    '''Reports the ``IPC`` (instructions per cycle) for rank 0
    '''
    regex1 = (r'^METRIC\s+0\s+.*Values: \(\"PAPI_TOT_INS\" <0>; UINT64;'
              r'\s+(?P<ins>\d+)\)')
    tot_ins_rk0 = sn.extractall(regex1, obj.rpt_otf2, 'ins', float)
    regex2 = (r'^METRIC\s+0\s+.*Values:.*\(\"PAPI_TOT_CYC\" <1>; UINT64;'
              r'\s+(?P<cyc>\d+)\)')
    tot_cyc_rk0 = sn.extractall(regex2, obj.rpt_otf2, 'cyc', float)
    ipc = [a/b for a, b in zip(tot_ins_rk0, tot_cyc_rk0)]
    return sn.round(max(ipc), 6)
# }}}
