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
