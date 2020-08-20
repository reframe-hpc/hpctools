# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ valgrind_version
@sn.sanity_function
def valgrind_version(obj):
    '''Checks tool's version:

    .. code-block::

      > echo $VALGRIND4HPC_VERSION
      2.6.4
      returns: True or False if versions match
    '''
    regex_v0 = r'^#define PACKAGE_VERSION \"(?P<valgrind_version>\S+)\"$'
    version0 = sn.extractsingle(regex_v0, obj.version_rpt, 'valgrind_version')
    ref_version0 = {'daint': '3.13.0', 'dom': '3.13.0'}
    #
    regex_v1 = r'^(?P<v4hpc_version>\S+)$'
    version1 = sn.extractsingle(regex_v1, obj.version_rpt, 'v4hpc_version')
    ref_version1 = {'daint': '2.6.4', 'dom': '2.6.4'}
    #
    TorF = sn.all([
        sn.assert_eq(version0, ref_version0[obj.current_system.name]),
        sn.assert_eq(version1, ref_version1[obj.current_system.name])
    ])
    return TorF
# }}}


# {{{ perf_patterns
@sn.sanity_function
def vhpc_perf_patterns(obj):
    '''Reports values from the tool

    .. code-block::

      ERROR SUMMARY: 1 errors from 8 contexts (suppressed 21)
                     ^
      HEAP SUMMARY:
        in use at exit: 0 bytes in 0 blocks
                        ^          ^

    '''
    regex = r'ERROR SUMMARY: (?P<nerror>\d+) errors from \d+ contexts'
    error_summary = sn.extractsingle(regex, obj.stdout, 'nerror', int)
    #
    regex = r'\s+in use at exit: (?P<bytes>\d+) bytes in (?P<blocks>\d+) block'
    heap_bytes = sn.extractsingle(regex, obj.stdout, 'bytes', int)
    heap_blocks = sn.extractsingle(regex, obj.stdout, 'blocks', int)
    res_d = {
        'v4hpc_errors_found': error_summary,
        'v4hpc_heap': heap_bytes,
        'v4hpc_blocks': heap_blocks,
    }
    return res_d
# }}}


# {{{ perf_reference
@sn.sanity_function
def vhpc_tool_reference(obj):
    '''Dictionary of default ``reference`` for the tool
    '''
    ref = ScopedDict()
    # first, copy the existing self.reference (if any):
    if obj.reference:
        for kk in obj.reference:
            ref[kk] = obj.reference['*:%s' % kk]

    # then add more:
    myzero = (0, None, None, '')
    mybytes = (0, None, None, 'bytes')
    ref['*:v4hpc_errors_found'] = myzero
    ref['*:v4hpc_heap'] = mybytes
    ref['*:v4hpc_blocks'] = myzero
    return ref
# }}}
