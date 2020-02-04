import os
import reframe as rfm
import reframe.utility.sanity as sn
# from reframe.core.fields import ScopedDict


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


@sn.sanity_function
def vtune_elapsed_max(self):
    '''Reports the maximum elapsed time (in seconds) between nodes measured by
    the tool

    .. code-block::

      > stdout:
       vtune: Executing actions 50 % Creating top-level rows Elapsed \
               Time: 29.974s
       Elapsed Time: 30.413s
       Elapsed Time: 29.528s
      returns: * vtune_elapsed_max: 30.413 s
    '''
    regex = r'.*Elapsed Time: (?P<sec>\S+)s'
    # rpt = os.path.join(obj.stagedir, obj.summary_rpt)
    return sn.round(sn.max(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def vtune_elapsed_min(self):
    '''Reports the minimum elapsed time (in seconds) between nodes measured by
    the tool

    .. code-block::

      > stdout:
       vtune: Executing actions 50 % Creating top-level rows Elapsed \
               Time: 29.974s
       Elapsed Time: 30.413s
       Elapsed Time: 29.528s
      returns: * vtune_elapsed_min: 29.528 s
    '''
    regex = r'.*Elapsed Time: (?P<sec>\S+)s'
    return sn.round(sn.min(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def vtune_cpu_time_max(self):
    '''Reports the maximum ``CPU Time`` (in seconds) measured by the tool
    divided by num_tasks for the slowest node

    .. code-block::

      CPU Time: 53.739s   <---
          Effective Time: 53.739s
          Spin Time: 0s
            MPI Busy Wait Time: 12.457s
    '''
    regex = r'^\s+CPU Time: (?P<sec>\S+)s'
    return sn.round(sn.max(sn.extractall(regex, self.stdout, 'sec', float)) /
                    self.num_tasks, 4)


@sn.sanity_function
def vtune_cpu_effective_time_max(self):
    '''Reports the maximum ``CPU Effective Time`` (in seconds) measured by the
    tool

    .. code-block::

      CPU Time: 53.739s
          Effective Time: 53.739s <---
          Spin Time: 0s
            MPI Busy Wait Time: 12.457s
    '''
    regex = r'^\s+Effective Time: (?P<sec>\S+)s'
    return sn.round(sn.max(sn.extractall(regex, self.stdout, 'sec', float)) /
                    self.num_tasks, 4)


@sn.sanity_function
def vtune_cpu_spin_time_max(self):
    '''Reports the maximum ``CPU Spin Time`` (in seconds) measured by the
    tool

    .. code-block::

      CPU Time: 53.739s
          Effective Time: 53.739s
          Spin Time: 0s <---
            MPI Busy Wait Time: 12.457s
    '''
    regex = r'^\s+Spin Time: (?P<sec>\S+)s'
    return sn.round(sn.max(sn.extractall(regex, self.stdout, 'sec', float)) /
                    self.num_tasks, 4)


@sn.sanity_function
def vtune_cpu_spin_mpiwait_time_max(self):
    '''Reports the maximum ``CPU MPI Wait Time`` (in seconds) measured by the
    tool

    .. code-block::

      CPU Time: 53.739s
          Effective Time: 53.739s
          Spin Time: 0s
            MPI Busy Wait Time: 12.457s <---
    '''
    regex = r'\s+MPI Busy Wait Time: (?P<sec>\S+)s'
    # print("self.num_tasks=", self.num_tasks)
    return sn.round(sn.max(sn.extractall(regex, self.stdout, 'sec', float)) /
                    self.num_tasks, 4)


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


@sn.sanity_function
def vtune_momentumAndEnergyIAD(self):
    '''
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   40.919s
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   38.994s
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   40.245s
    sphexa::sph::computeMomentumAndEnergyIADImpl<...>  sqpatch.exe   39.487s
    '''
    regex1 = r'^\s+CPU Time: (?P<sec>\S+)s'
    result1 = sn.max(sn.extractall(regex1, self.stdout, 'sec', float))
    regex2 = r'^sphexa::sph::computeMomentumAndEnergyIADImpl.*\s+(?P<x>\S+)s$'
    result2 = sn.max(sn.extractall(regex2, self.stdout, 'x', float))
    print("vtune_cput=", result1)
    print("vtune_energ=", result2)
    print("vtune_cput/24=", result1/24)
    print("vtune_energ/24=", result2/24)
    #print("t=", result1/result2)
    #print("c=", self.num_tasks)
    #print("t=", (result1/result2) / self.num_tasks)
    # t= 5.208910219363269 / 24 = 0.2170379258068029
    # vtune_momentumAndEnergyIAD: 5.2089 %
    return 0
    # return sn.round(result1/result2, 4)
    # return sn.round((100 * sec / self.vtune_cpu_time), 2)

# sphexa::sph::computeMomentumAndEnergyIADImpl<double, sphexa::ParticlesData<double>>  sqpatch.exe   40.919s / 24 = 1.7 s = 32% of 5.3 s
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
