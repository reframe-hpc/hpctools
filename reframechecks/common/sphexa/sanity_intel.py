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
