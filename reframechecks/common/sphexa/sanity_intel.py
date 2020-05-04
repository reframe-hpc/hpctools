# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ sanity_function: intel_inspector
# @property

@sn.sanity_function
def inspector_version(obj):
    '''Checks tool's version:

    .. code-block::

      > inspxe-cl --version
      Intel(R) Inspector 2020 (build 603904) Command Line tool
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '603904',  # 2020
        'dom': '603904',    # 2020
    }
    regex = (r'^Intel\(R\) Inspector \d+\s+\(build (?P<toolsversion>\d+)')
    version = sn.extractsingle(regex, obj.version_rpt, 'toolsversion')
    TorF = sn.assert_eq(
        version, reference_tool_version[obj.current_system.name])
    # print('version=%s' % version)
    # print('ref_version=%s' % reference_tool_version[obj.current_system.name])
    return TorF


@sn.sanity_function
def inspector_not_deallocated(obj):
    '''Reports number of Memory not deallocated problem(s)

    .. code-block::

      > summary.rpt
      2 new problem(s) found
      1 Memory leak problem(s) detected
      1 Memory not deallocated problem(s) detected
      returns: * Memory not deallocated: 1
    '''
    regex = r'(?P<ndealloc>\d+) Memory not deallocated problem'
    result = sn.extractsingle(regex, obj.summary_rpt, 'ndealloc', int)
    return result


# TODO:
# @sn.sanity_function
# def inspector_leak(self):
#     print('rpt=%s' % obj.summary_rpt)
#     regex = r'(?P<nleak>\d+) Memory leak problem'
#     result = sn.extractsingle(regex, self.summary_rpt, 'nleak', int)
#     return result
# }}}

# {{{ sanity_function: intel_vtune
# {{{ vtune_version
@sn.sanity_function
def vtune_version(obj):
    '''Checks tool's version:

    .. code-block::

      > vtune --version
      Intel(R) VTune(TM) Profiler 2020 (build 605129) Command Line Tool
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '605129',  # 2020
        'dom': '605129',    # 2020
    }
    regex = (r'^Intel\(R\) VTune\(TM\) Profiler \d+\s+\(build'
             r'\s(?P<toolsversion>\d+)')
    version = sn.extractsingle(regex, obj.version_rpt, 'toolsversion')
    TorF = sn.assert_eq(
        version, reference_tool_version[obj.current_system.name])
    return TorF
# }}}

# {{{ vtune_time
@sn.sanity_function
def vtune_time(self):
    '''Vtune creates 1 report per compute node. For example, a 48 mpi tasks job
    (= 2 compute nodes when running with 24 c/cn) will create 2 directories:
    * rpt.nid00001/rpt.nid00001.vtune
    * rpt.nid00002/rpt.nid00002.vtune

    Typical output (for each compute node) is:

    .. code-block::

      Elapsed Time:	14.866s
          CPU Time:	319.177s            /24 = 13.3
              Effective Time:	308.218s    /24 = 12.8
                  Idle:	0s
                  Poor:	19.725s
                  Ok:	119.570s
                  Ideal:	168.922s
                  Over:	0s
              Spin Time:	10.959s             /24 =  0.4
                  MPI Busy Wait Time:	10.795s
                  Other:	0.164s
              Overhead Time:	0s
      Total Thread Count:	25
      Paused Time:	0s
    '''
    result_d = {}
    # --- ranks per node
    if self.num_tasks < self.num_tasks_per_node:
        vtune_tasks_per_node = self.num_tasks
    else:
        vtune_tasks_per_node = self.num_tasks_per_node
    # --- Elapsed Time (min, max)
    regex = r'.*Elapsed Time: (?P<sec>\S+)s'
    result = sn.extractall(regex, self.stdout, 'sec', float)
    result_d['elapsed_min'] = sn.round(sn.min(result), 4)
    result_d['elapsed_max'] = sn.round(sn.max(result), 4)
    # --- CPU Time (max)
    regex = r'^\s+CPU Time: (?P<sec>\S+)s'
    result = sn.extractall(regex, self.stdout, 'sec', float)
    result_d['elapsed_cput'] = sn.round(sn.max(result) / vtune_tasks_per_node,
                                        4)
    # --- CPU Time: Effective Time (max)
    regex = r'^\s+Effective Time: (?P<sec>\S+)s'
    result = sn.extractall(regex, self.stdout, 'sec', float)
    result_d['elapsed_cput_efft'] = sn.round(sn.max(result) /
                                             vtune_tasks_per_node, 4)
    # --- CPU Time: Spin Time (max)
    regex = r'^\s+Spin Time: (?P<sec>\S+)s'
    result = sn.extractall(regex, self.stdout, 'sec', float)
    result_d['elapsed_cput_spint'] = sn.round(sn.max(result) /
                                              vtune_tasks_per_node, 4)
    # --- CPU Time: Spin Time: MPI Busy Wait (max)
    if self.num_tasks > 1:
        regex = r'\s+MPI Busy Wait Time: (?P<sec>\S+)s'
        result = sn.extractall(regex, self.stdout, 'sec', float)
        result_d['elapsed_cput_spint_mpit'] = sn.round(sn.max(result) /
                                                       vtune_tasks_per_node, 4)
    else:
        result_d['elapsed_cput_spint_mpit'] = 0

# TODO:
# 'vtune_momentumAndEnergyIAD':
# sphsintel.vtune_momentumAndEnergyIAD(self),
# '%vtune_srcf_lookupTables': self.vtune_pct_lookupTables,
# '%vtune_srcf_Octree': self.vtune_pct_Octree,
# '%vtune_srcf_momentumAndEnergyIAD':
# self.vtune_pct_momentumAndEnergyIAD,
# '%vtune_srcf_IAD': self.vtune_pct_IAD,
    return result_d
# }}}

# {{{ vtune_physical_core_utilization
@sn.sanity_function
def vtune_physical_core_utilization(self):
    '''Reports the minimum ``Physical Core Utilization`` (%) measured by the
    tool

    .. code-block::

      Effective Physical Core Utilization: 96.3% (11.554 out of 12)
      Effective Physical Core Utilization: 96.1% (11.534 out of 12)
      Effective Physical Core Utilization: 95.9% (11.512 out of 12)
    '''
    regex = r'^Effective Physical Core Utilization: (?P<pct>\S+)%'
    return sn.round(sn.min(sn.extractall(regex, self.stdout, 'pct', float)), 4)
# }}}

# {{{ vtune_logical_core_utilization
@sn.sanity_function
def vtune_logical_core_utilization(self):
    '''Reports the minimum ``Physical Core Utilization`` (%) measured by the
    tool

    .. code-block::

      Effective Logical Core Utilization: 96.0% (23.028 out of 24)
      Effective Logical Core Utilization: 95.9% (23.007 out of 24)
      Effective Logical Core Utilization: 95.5% (22.911 out of 24)
    '''
    regex = r'^\s+Effective Logical Core Utilization: (?P<pct>\S+)%'
    return sn.round(sn.min(sn.extractall(regex, self.stdout, 'pct', float)), 4)
# }}}

# {{{ vtune_momentumAndEnergyIAD
@sn.sanity_function
def vtune_momentumAndEnergyIAD(self):
    '''
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   40.919s
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   38.994s
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   40.245s
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   39.487s
    '''
    # ^[sphexa::|MPI|[Others].*\s+(?P<sec>\S+)s$'
    regex1 = r'^\s+CPU Time: (?P<sec>\S+)s'
    result1 = sn.max(sn.extractall(regex1, self.stdout, 'sec', float))
    regex2 = r'^sphexa::sph::computeMomentumAndEnergyIADImpl.*\s+(?P<x>\S+)s$'
    result2 = sn.max(sn.extractall(regex2, self.stdout, 'x', float))
    print("vtune_cput=", result1)
    print("vtune_energ=", result2)
    print("vtune_cput/24=", result1/24)
    print("vtune_energ/24=", result2/24)
    # print("t=", result1/result2)
    # print("c=", self.num_tasks)
    # print("t=", (result1/result2) / self.num_tasks)
    # t= 5.208910219363269 / 24 = 0.2170379258068029
    # vtune_momentumAndEnergyIAD: 5.2089 %
    return 0
    # return sn.round(result1/result2, 4)
    # return sn.round((100 * sec / self.vtune_cpu_time), 2)

# sphexa::sph::computeMomentumAndEnergyIADImpl
# <double, sphexa::ParticlesData<double>>  sqpatch.exe
# 40.919s / 24 = 1.7 s = 32% of 5.3 s
# }}}

# {{{ vtune_perf_patterns
@sn.sanity_function
def vtune_perf_patterns(obj):
    '''Dictionary of default ``perf_patterns`` for the tool
    '''
    stdout_d = vtune_time(obj)
    res_d = {
        'vtune_elapsed_min': stdout_d['elapsed_min'],
        'vtune_elapsed_max': stdout_d['elapsed_max'],
        'vtune_elapsed_cput': stdout_d['elapsed_cput'],
        'vtune_elapsed_cput_efft': stdout_d['elapsed_cput_efft'],
        'vtune_elapsed_cput_spint': stdout_d['elapsed_cput_spint'],
        'vtune_elapsed_cput_spint_mpit': stdout_d['elapsed_cput_spint_mpit'],
        #
        '%vtune_effective_physical_core_utilization':
        vtune_physical_core_utilization(obj),
        '%vtune_effective_logical_core_utilization':
        vtune_logical_core_utilization(obj),
    }
    return res_d
# }}}

# {{{ vtune_tool_reference
@sn.sanity_function
def vtune_tool_reference(obj):
    '''Dictionary of default ``reference`` for the tool
    '''
    reference = ScopedDict()
    # first, copy the existing self.reference (if any):
    if obj.reference:
        for kk in obj.reference:
            reference[kk] = obj.reference['*:%s' % kk]

    # then add more:
    myzero_s = (0, None, None, 's')
    myzero_p = (0, None, None, '%')
    reference['*:vtune_elapsed_min'] = myzero_s
    reference['*:vtune_elapsed_max'] = myzero_s
    reference['*:vtune_elapsed_cput'] = myzero_s
    reference['*:vtune_elapsed_cput_efft'] = myzero_s
    reference['*:vtune_elapsed_cput_spint'] = myzero_s
    reference['*:vtune_elapsed_cput_spint_mpit'] = myzero_s
    reference['*:%vtune_effective_physical_core_utilization'] = myzero_p
    reference['*:%vtune_effective_logical_core_utilization'] = myzero_p
    # inside check, use this instead:
    # self.reference['*:vtune_elapsed_min'] = myzero_s
    # self.reference['*:vtune_momentumAndEnergyIAD'] = (0, None, None, 's')

    return reference
# }}}
# }}}

# {{{ sanity_function: intel_advisor
@sn.sanity_function
def advisor_version(obj):
    '''Checks tool's version:

    .. code-block::

      > advixe-cl --version
      Intel(R) Advisor 2020 (build 604394) Command Line Tool
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '604394',  # 2020
        'dom': '604394',    # 2020
    }
    regex = (r'^Intel\(R\) Advisor \d+\s+\(build (?P<toolsversion>\d+)')
    version = sn.extractsingle(regex, obj.version_rpt, 'toolsversion')
    TorF = sn.assert_eq(
        version, reference_tool_version[obj.current_system.name])
    # print('version=%s' % version)
    # print('ref_version=%s' % reference_tool_version[obj.current_system.name])
    return TorF


@sn.sanity_function
def advisor_loop1_line(obj):
    ''' Reports the line (fline) of the most time consuming loop

    .. code-block::

      > summary.rpt
      ID / Function Call Sites and Loops / Total Time / Self Time /  Type
      71 [loop in sphexa::sph::computeMomentumAndEnergyIADImpl<double,
        ... sphexa::ParticlesData<double>> at momentumAndEnergyIAD.hpp:94]
        ... 1.092s      0.736s              Scalar  momentumAndEnergyIAD.hpp:94
      34 [loop in MPIDI_Cray_shared_mem_coll_bcast]
        ... 0.596s      0.472s              Scalar  libmpich_gnu_82.so.3
      etc.
      returns: * advisor_loop1_line: 94 (momentumAndEnergyIAD.hpp)
    '''
    regex = (r'\d+\s+\[loop in sphexa::(?P<funcname>.*) at (?P<filename>\S+):'
             r'(?P<fline>\d+)\]')
    rpt = os.path.join(obj.stagedir, obj.summary_rpt)
    # print('RPT=', rpt)
    fline = sn.extractsingle(regex, rpt, 'fline', int)
    # NOTE: This will fail with 'No such file or directory':
    # fline = sn.extractsingle(regex, obj.summary_rpt, 'fline', int)
    return fline


@sn.sanity_function
def advisor_loop1_filename(obj):
    ''' Reports the name of the source file (filename) of the most time
    consuming loop

    .. code-block::

      > summary.rpt
      ID / Function Call Sites and Loops / Total Time / Self Time /  Type
      71 [loop in sphexa::sph::computeMomentumAndEnergyIADImpl<double,
        ... sphexa::ParticlesData<double>> at momentumAndEnergyIAD.hpp:94]
        ... 1.092s      0.736s              Scalar  momentumAndEnergyIAD.hpp:94
      34 [loop in MPIDI_Cray_shared_mem_coll_bcast]
        ... 0.596s      0.472s              Scalar  libmpich_gnu_82.so.3
      etc.
      returns: * advisor_loop1_line: 94 (momentumAndEnergyIAD.hpp)
    '''
    # debug with: import pdb; pdb.set_trace()
    # also in rpt/e000/hs000/advisor-survey.txt
    regex = (r'\d+\s+\[loop in sphexa::(?P<funcname>.*) at (?P<filename>\S+):'
             r'(?P<fline>\d+)\]')
    rpt = os.path.join(obj.stagedir, obj.summary_rpt)
    fname = sn.extractsingle(regex, rpt, 'filename')
    return ('(' + fname + ')')


@sn.sanity_function
def advisor_elapsed(obj):
    ''' Reports the elapsed time (sum of ``Self Time`` in seconds) measured by
    the tool

    .. code-block::

      > summary.rpt
      ID / Function Call Sites and Loops / Total Time / Self Time /  Type
      71 [loop in sphexa::sph::computeMomentumAndEnergyIADImpl<double,
        ... sphexa::ParticlesData<double>> at momentumAndEnergyIAD.hpp:94]
        ... 1.092s      0.736s              Scalar  momentumAndEnergyIAD.hpp:94
      34 [loop in MPIDI_Cray_shared_mem_coll_bcast]
        ... 0.596s      0.472s              Scalar  libmpich_gnu_82.so.3
      etc.
      returns: * advisor_elapsed: 2.13 s
    '''
    regex = r'\s+\d+\s+\[.*\]\s+(?P<inclusive>\S+)s\s+(?P<exclusive>\S+)s'
    rpt = os.path.join(obj.stagedir, obj.summary_rpt)
    return sn.round(sn.sum(sn.extractall(regex, rpt, 'exclusive', float)), 4)

# @property
# @sn.sanity_function
# def advisor_loop1_name(self):
#     # Intel Advisor identifies the loops that will benefit the most from
#     # refined vectorization
#     regex =  (r'\d+\s+\[loop in sphexa::(?P<loop>\S+) at '
#               r'(?P<fname>\S+):(?P<fline>\d+)\]')
#     loop = sn.extractsingle(regex, self.rpt, 'loop')
#     fname = sn.extractsingle(regex, self.rpt, 'fname')
#     return (loop + '/' + fname)

# }}}
