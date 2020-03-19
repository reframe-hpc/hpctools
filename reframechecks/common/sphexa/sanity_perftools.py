# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict
import sphexa.sanity as sphs


class PerftoolsBaseTest(rfm.RegressionTest):
    def __init__(self):
        x = 0

# {{{ sanity patterns
# {{{ patrun_version
    @rfm.run_before('sanity')
    def patrun_version(self):
        '''Checks tool's version:

        .. code-block::

          > pat_run -V
          CrayPat/X:  Version 20.03.0 Revision b18264180
        '''
        reference_tool_version = {
            'daint': '7.1.1',
            'dom': '20.03.0',
        }
        ref_version = reference_tool_version[self.current_system.name]
        regex = r'^CrayPat/X:\s+Version (?P<toolversion>\S+) Revision'
        res_version = sn.extractsingle(regex, self.version_rpt, 'toolversion')
        self.sanity_patterns_l.append(sn.assert_eq(res_version, ref_version))
# }}}
# }}}

# {{{ regex functions
# {{{ patrun: number of compute nodes
    @rfm.run_before('performance')
    def patrun_num_of_compute_nodes(self):
        '''Extract the number of compute nodes to compute averages

        .. code-block::

          > ls 96mpi/sqpatch.exe+8709-4s/xf-files/:
            000004.xf
            000005.xf
            000006.xf
            000007.xf

        Typical output:
            * patrun_cn: 4
        '''
        regex = r'^(?P<cn>\d+.xf)$'
        self.num_cn = sn.count(sn.extractall(regex, self.stdout, 'cn'))
# }}}

# {{{ patrun: table Wall Clock Time, Memory
    @rfm.run_before('performance')
    def patrun_walltime_and_memory(self):
        '''This table shows total wall clock time for the ranks with the
        maximum, mean, and minimum time, as well as the average across ranks.

        .. code-block::

          Table 10:  Wall Clock Time, Memory High Water Mark

             Process |   Process | PE=[mmm]
                Time |     HiMem |
                     | (MiBytes) |

           11.389914 |      76.3 | Total    <-- avgt
          |--------------------------------
          | 11.398188 |      57.7 | pe.24   <-- maxt
          | 11.389955 |      98.9 | pe.34
          | 11.365630 |      54.0 | pe.93   <-- mint
          |================================

        Typical output:
          * patrun_wallt_max: 11.3982 s
          * patrun_wallt_avg: 11.3899 s
          * patrun_wallt_min: 11.3656 s
          * patrun_mem_max: 57.7 MiBytes
          * patrun_mem_min: 54.0 MiBytes
        '''
        # TODO: bug avg mem?
        res = {}
        # --- avg
        regex = (r'^Table \d+:  Wall Clock Time, Memory High Water Mark\n'
                 r'(.*\n){4}\s+(.*\n)\s+(?P<proct>\S+)\s+\|\s+(?P<mem>\S+)'
                 r' \| Total$')
        res['patrun_wallt_avg'] = sn.extractsingle(regex, self.stdout,
                                                   'proct', float)
        res['patrun_mem_avg'] = sn.extractsingle(regex, self.stdout,
                                                 'mem', float)
        # --- max
        regex = (r'^Table \d+:  Wall Clock Time, Memory High Water Mark\n'
                 r'(.*\n){4}\s+(.*\n){2}\|\s+(?P<proct>\S+) \|\s+(?P<mem>\S+)'
                 r'\s+\|\s(?P<pe>\S+)$')
        res['patrun_wallt_max'] = sn.extractsingle(regex, self.stdout, 'proct',
                                                   float)
        res['patrun_mem_max'] = sn.extractsingle(regex, self.stdout, 'mem',
                                                 float)
        res['patrun_mem_max_pe'] = sn.extractsingle(regex, self.stdout, 'pe',
                                                    float)
        # --- min
        regex = (r'^Table \d+:  Wall Clock Time, Memory High Water Mark\n'
                 r'(.*\n){4}\s+(.*\n){4}\|\s+(?P<proct>\S+) \|\s+(?P<mem>\S+)'
                 r'\s+\|\s(?P<pe>\S+)$')
        res['patrun_wallt_min'] = sn.extractsingle(regex, self.stdout, 'proct',
                                                   float)
        res['patrun_mem_min'] = sn.extractsingle(regex, self.stdout, 'mem',
                                                 float)
        res['patrun_mem_min_pe'] = sn.extractsingle(regex, self.stdout, 'pe',
                                                    float)
        for kk, vv in res.items():
            if not isinstance(vv, str):
                res[kk] = sn.round(vv, 4)
        self.patrun_perf_d = res
# }}}

# {{{ patrun: table Memory Bandwidth by Numanode
    @rfm.run_before('performance')
    def patrun_memory_bw(self):
        '''This table shows memory traffic to local and remote memory for numa
        nodes, taking for each numa node the maximum value across nodes.

        .. code-block::

          Table 9:  Memory Bandwidth by Numanode

            Memory |   Local |    Thread |  Memory |  Memory | Numanode
           Traffic |  Memory |      Time | Traffic | Traffic |  Node Id
            GBytes | Traffic |           |  GBytes |       / |   PE=HIDE
                   |  GBytes |           |   / Sec | Nominal |
                   |         |           |         |    Peak |
          |--------------------------------------------------------------
          |   33.64 |   33.64 | 11.360701 |    2.96 |    4.3% | numanode.0
          ||-------------------------------------------------------------
          ||   33.64 |   33.64 | 11.359413 |    2.96 |    4.3% | nid.4
          ||   33.59 |   33.59 | 11.359451 |    2.96 |    4.3% | nid.6
          ||   33.24 |   33.24 | 11.360701 |    2.93 |    4.3% | nid.5
          ||   28.24 |   28.24 | 11.355006 |    2.49 |    3.6% | nid.7
          |==============================================================

        Typical output:
            * patrun_memory_traffic_global: 33.64 GB
            * patrun_memory_traffic_local: 33.64 GB
            * %patrun_memory_traffic_peak: 4.3 %
        '''
        res = {}
        regex = (r'^Table \d+:\s+Memory Bandwidth by Numanode\n(.*\n){7}\|\s+'
                 r'(?P<GBytes>\S+)\s+\|\s+(?P<GBytes_local>\S+)\s+\|\s+\S+\s+'
                 r'\|\s+\S+\s+\|\s+(?P<peak_pct>\S+)%')
        res['memory_traffic_global'] = sn.extractsingle(regex, self.stdout,
                                                        'GBytes', float)
        res['memory_traffic_local'] = sn.extractsingle(regex, self.stdout,
                                                       'GBytes_local', float)
        res['memory_traffic_peak'] = sn.extractsingle(regex, self.stdout,
                                                      'peak_pct', float)
        #
        if self.patrun_perf_d:
            self.patrun_perf_d = {**self.patrun_perf_d, **res}
        else:
            self.patrun_perf_d = res
# }}}

# {{{ patrun: table HW Performance Counter
    @rfm.run_before('performance')
    def patrun_hwpc(self):
        '''This table shows HW performance counter data for the whole program,
        averaged across ranks or threads, as applicable.

        .. code-block::

          Table 4:  Program HW Performance Counter Data
            ...
            Thread Time                                          11.352817 secs
            UNHALTED_REFERENCE_CYCLES                        28,659,167,096
            CPU_CLK_THREAD_UNHALTED:THREAD_P                 34,170,540,119
            DTLB_LOAD_MISSES:WALK_DURATION                       61,307,848
            INST_RETIRED:ANY_P                               22,152,242,298
            RESOURCE_STALLS:ANY                              19,793,119,676
            OFFCORE_RESPONSE_0:ANY_REQUEST:L3_MISS_LOCAL         20,949,344
            CPU CLK Boost                                              1.19 X
            Resource stall cycles / Cycles  -->                       57.9%
            Memory traffic GBytes           -->       0.118G/sec       1.34 GB
            Local Memory traffic GBytes               0.118G/sec       1.34 GB
            Memory Traffic / Nominal Peak                              0.2%
            DTLB Miss Ovhd                       61,307,848 cycles  0.2% cycles
            Retired Inst per Clock          -->                        0.65
          ==============================================================================

        Typical output:
            * patrun_memory_traffic: 1.34 GB
            * patrun_ipc: 0.65
            * %patrun_stallcycles: 57.9 %
        '''
        res = {}
        regex = (r'^Table \d+:\s+Program HW Performance Counter Data\n'
                 r'(.*\n){15}.*Resource stall cycles \/ Cycles\s+(?P<pp>\S+)%')
        res['stallcycles'] = sn.extractsingle(regex, self.stdout, 'pp', float)
        #
        regex = (r'^Table \d+:\s+Program HW Performance Counter Data\n'
                 r'(.*\n){16}.*Memory traffic GBytes.*\s+(?P<GB>\S+) GB')
        res['memory_traffic'] = sn.extractsingle(regex, self.stdout, 'GB',
                                                 float)
        #
        regex = (r'^Table \d+:\s+Program HW Performance Counter Data\n'
                 r'(.*\n){20}.*Retired Inst per Clock\s+(?P<ipc>\S+)')
        res['ipc'] = sn.extractsingle(regex, self.stdout, 'ipc', float)
        #
        self.patrun_hwc_d = res
        # if self.patrun_perf_d:
        #     self.patrun_perf_d = {**self.patrun_perf_d, **res}
        # else:
        #     self.patrun_perf_d = res
# }}}

# {{{ patrun: table energy and power usage
    @rfm.run_before('performance')
    def patrun_energy_power(self):
        '''This table shows HW performance counter data for the whole program,
        averaged across ranks or threads, as applicable.

        .. code-block::

          Table 8:  Program energy and power usage (from Cray PM)

             Node |     Node |   Process | Node Id
           Energy |    Power |      Time |  PE=HIDE
              (J) |      (W) |           |

            7,891 |  692.806 | 11.389914 | Total    <---
          |-- --------------------------------------
          |  2,076 |  182.356 | 11.384319 | nid.7
          |  1,977 |  173.548 | 11.391657 | nid.4
          |  1,934 |  169.765 | 11.392220 | nid.6
          |  1,904 |  167.143 | 11.391461 | nid.5
          |========================================

        Typical output:
            * patrun_avg_power: 692.806 W
        '''
        res = {}
        regex = (r'^Table \d+:\s+Program energy and power usage \(from Cray '
                 r'PM\)\n(.*\n){5}\s+(?P<nrgy>\S+)\s+\|\s+(?P<power>\S+).*'
                 r'Total$')
        # res_str = sn.extractsingle(regex, self.stdout, 'nrgy')
        # mystr = sn.evaluate(res_str)
        # print('XXXX', type(res_str))
        # res['energy_avg'] = int(mystr.replace(',', ''))
        res['power_avg'] = sn.extractsingle(regex, self.stdout, 'power',
                                            float) / self.num_cn
        # res['ipc'] = sn.extractsingle(regex, self.stdout, 'ipc', float)
        #
        # self.patrun_xxx_d = res
        if self.patrun_perf_d:
            self.patrun_perf_d = {**self.patrun_perf_d, **res}
        else:
            self.patrun_perf_d = res
# }}}

# {{{ patrun: table Profile by Function
    @rfm.run_before('performance')
    def patrun_samples(self):
        '''Elapsed time (in samples) reported by the tool:

        .. code-block::

          Table 1:  Profile by Function

            Samp% |  Samp |  Imb. |  Imb. | Group
                  |       |  Samp | Samp% |  Function
                  |       |       |       |   PE=HIDE

           100.0% | 382.8 |    -- |    -- | Total
           TODO:
            Experiment:  samp_cs_time
            Sampling interval:  10000 microsecs
        '''
        regex = (r'^Table 1:  Profile by Function\n(.*\n){4}\s+100.0%\s+\|\s+'
                 r'(?P<sam>\S+)\s+')
        self.patrun_sample = sn.extractsingle(regex, self.stdout, 'sam', float)
# }}}

# {{{ patrun: hotspot1
    @rfm.run_after('sanity')
    def patrun_hotspot1(self):
        regex = (r'^Table \d+:  Profile by Group, Function, and Line\n'
                 r'(.*\n){7}\s+.*Total\n(.*\n){3}(\|)+\s+(?P<pct>\S+)%.*\|\s+'
                 r'.*(?P<fname>sphexa.*)$')
        # --- ok:
        rpt = os.path.join(self.stagedir, self.rpt)
        self.patrun_hotspot1_pct = sn.extractsingle(regex, rpt, 'pct', float)
        self.patrun_hotspot1_name = sn.extractsingle(regex, rpt, 'fname')
# {{{        # --- ko:
        # self.patrun_hotspot1_pct = \
        #     sn.extractsingle(regex, self.stdout, 'pct', float)
        # self.patrun_hotspot1_name = \
        #     sn.extractsingle(regex, self.stdout, 'fname')
        # --- ko:
        # self.patrun_hotspot1_pct = \
        #     sn.extractsingle(regex, self.rpt, 'pct', float)
        # self.patrun_hotspot1_name = \
        #     sn.extractsingle(regex, self.rpt, 'fname')
# }}}
# }}}

# {{{ patrun: hotspot1 MPI
    @rfm.run_after('sanity')
    def patrun_hotspot1_mpi(self):
        '''

        .. code-block::

          Table 1:  Profile by Function

            Samp% |    Samp |  Imb. |  Imb. | Group
                  |         |  Samp | Samp% |  Function
                  |         |       |       |   PE=HIDE

           100.0% | 1,126.4 |    -- |    -- | Total
          ...
          ||=================================================
          |   9.9% |   111.4 |    -- |    -- | MPI
          ||-------------------------------------------------
          ||   5.2% |    58.2 | 993.8 | 95.5% | MPI_Allreduce <--
          ||   3.6% |    40.9 | 399.1 | 91.7% | MPI_Recv


        '''
        rpt = os.path.join(self.stagedir, self.rpt)
        regex = (r'^Table \d+:  Profile by Function\n(.*\n){19}\|+\s+'
                 r'(?P<sam_pct>\S+)%(\s+\|\s+\S+){2}\s\|\s+'
                 r'(?P<imb_pct>\S+)%\s\|\s+(?P<fname>\S+)')
        res = {}
        res['mpi_h1'] = sn.extractsingle(regex, rpt, 'sam_pct', float)
        res['mpi_h1_imb'] = sn.extractsingle(regex, rpt, 'imb_pct', float)
        res['mpi_h1_name'] = sn.extractsingle(regex, rpt, 'fname')
        #
        self.mpi_h1 = res['mpi_h1']
        self.mpi_h1_imb = res['mpi_h1_imb']
        self.mpi_h1_name = res['mpi_h1_name']
        # if self.patrun_perf_d:
        #     self.patrun_perf_d = {**self.patrun_perf_d, **res}
        # else:
        #     self.patrun_perf_d = res
        # TODO: when MPI is not #2 as in:
        # |  14.8% |  57.0 |    -- |    -- | ETC
        # ||----------------------------------------------------
        # ||  10.9% |  42.1 |   7.9 | 16.4% | __sin_avx
        # ||   2.8% |  10.7 |   5.3 | 34.5% | __memset_avx2_erms
        # ||====================================================
        # |   6.9% |  26.5 |    -- |    -- | MPI
        # ||----------------------------------------------------
        # ||   3.2% |  12.2 | 124.8 | 95.0% | MPI_Recv
# }}}

# {{{ rpt_path_stdout
#     @rfm.run_before('sanity')
#     def rpt_path_stdout(self):
#         '''Get path to the report dir from stdout:
#
#         .. code-block::
#
#           Experiment data directory written:
#           .../sqpatch.exe+19625-2s
#         '''
#         regex = r'^Experiment data directory written:\n(?P<rpt_path>.*)$'
#         self.rpt_path = sn.extractsingle(regex, self.stdout, 'rpt_path')
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
          :lines: 97-137
          :emphasize-lines: 24-28, 35-37

        '''
        regex = r'^\|\s+(?P<pct>\S+)%\s+\|\s+(?P<sam>\S+).*USER$'
        usr_pct = sn.extractsingle(regex, self.stdout, 'pct', float)
        regex = r'^\|\s+(?P<pct>\S+)%\s+\|\s+(?P<sam>\S+).*MPI$'
        mpi_pct = sn.extractsingle(regex, self.stdout, 'pct', float)
        etc_pct = sn.round(100 - usr_pct - mpi_pct, 1)
        perf_pattern = {
            'patrun_cn': self.num_cn,
            'patrun_wallt_max': self.patrun_perf_d['patrun_wallt_max'],
            'patrun_wallt_avg': self.patrun_perf_d['patrun_wallt_avg'],
            'patrun_wallt_min': self.patrun_perf_d['patrun_wallt_min'],
            #
            'patrun_mem_max': self.patrun_perf_d['patrun_mem_max'],
            # 'patrun_mem_avg': self.patrun_perf_d['patrun_mem_avg'],
            'patrun_mem_min': self.patrun_perf_d['patrun_mem_min'],
            #
            'patrun_memory_traffic_global':
                self.patrun_perf_d['memory_traffic_global'],
            'patrun_memory_traffic_local':
                self.patrun_perf_d['memory_traffic_local'],
            '%patrun_memory_traffic_peak':
                self.patrun_perf_d['memory_traffic_peak'],
            #
            'patrun_memory_traffic': self.patrun_hwc_d['memory_traffic'],
            'patrun_ipc': self.patrun_hwc_d['ipc'],
            '%patrun_stallcycles': self.patrun_hwc_d['stallcycles'],
            #
            '%patrun_avg_usr': usr_pct,
            '%patrun_avg_mpi': mpi_pct,
            '%patrun_avg_etc': etc_pct,
            '%patrun_hotspot1': self.patrun_hotspot1_pct,
            #
            '%patrun_mpi_h1': self.mpi_h1,
            '%patrun_mpi_h1_imb': self.mpi_h1_imb,
            # ko:
            # '%patrun_mpi_h1': self.patrun_perf_d['mpi_h1'],
            # '%patrun_mpi_h1_imb': self.patrun_perf_d['mpi_h1_imb'],
            #
            'patrun_avg_power': self.patrun_perf_d['power_avg'],
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
        myzero_j = (0, None, None, 'J')
        myzero_w = (0, None, None, 'W')
        myzero_p = (0, None, None, '%')
        myzero_mb = (0, None, None, 'MiBytes')
        myzero_gb = (0, None, None, 'GB')
        h1_name = '%% (%s)' % self.patrun_hotspot1_name
        myzero_h1 = (0, None, None, h1_name)
        # mpi_h1_name = '%% (%s)' % self.patrun_perf_d['mpi_h1_name']
        mpi_h1_name = '%% (%s)' % self.mpi_h1_name
        myzero_mpi_h1 = (0, None, None, mpi_h1_name)
        ref['patrun_cn'] = myzero
        ref['patrun_wallt_max'] = myzero_s
        ref['patrun_wallt_avg'] = myzero_s
        ref['patrun_wallt_min'] = myzero_s
        #
        ref['patrun_mem_max'] = myzero_mb
        # ref['patrun_mem_avg'] = myzero_mb
        ref['patrun_mem_min'] = myzero_mb
        #
        ref['patrun_memory_traffic_global'] = myzero_gb
        ref['patrun_memory_traffic_local'] = myzero_gb
        ref['%patrun_memory_traffic_peak'] = myzero_p
        #
        ref['patrun_memory_traffic'] = myzero_gb
        ref['patrun_ipc'] = myzero
        ref['%patrun_stallcycles'] = myzero_p
        #
        ref['%patrun_avg_usr'] = myzero_p
        ref['%patrun_avg_mpi'] = myzero_p
        ref['%patrun_avg_etc'] = myzero_p
        ref['%patrun_hotspot1'] = myzero_h1
        #
        ref['%patrun_mpi_h1'] = myzero_mpi_h1
        ref['%patrun_mpi_h1_imb'] = myzero_mpi_h1
        #
        ref['patrun_avg_power'] = myzero_w
        # TODO: ref['patrun_avg_energy'] = myzero_j
        # final reference:
        self.reference = ref
# }}}
# }}}

# {{{ TODO: perftools-lite
# }}}
