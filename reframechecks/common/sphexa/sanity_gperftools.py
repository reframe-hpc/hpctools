# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


@sn.sanity_function
def gp_perf_patterns(obj, reg):
    '''Reports top1 function from the tool

    .. code-block::

      Type: cpu
      Showing nodes accounting for 3690ms, 92.48% of 3990ms total
      Dropped 79 nodes (cum <= 19.95ms)
      flat  flat%   sum%        cum   cum%
      530ms 13.28% 13.28%      530ms 13.28%  sphexa::.../lookupTables.hpp:123
            ^^^^^                                        ^^^^^^^^^^^^^^^^ ^^^
    '''
    rpt = os.path.join(obj.stagedir, obj.rpt_file_txt)
    regex = (r'^\s+flat\s+flat%\s+sum%\s+cum\s+cum%\n\s+\d+ms\s+(?P<pct>\S+)'
             r'%.*/(?P<filename>\S+):(?P<linen>\S+)')
    if reg == 1:
        result = sn.extractsingle(regex, rpt, 'pct', float)
    elif reg == 2:
        result = sn.extractsingle(regex, rpt, 'filename')
    elif reg == 3:
        result = sn.extractsingle(regex, rpt, 'linen', int)
    elif reg == 4:
        res1 = sn.extractsingle(regex, rpt, 'filename')
        res2 = sn.extractsingle(regex, rpt, 'linen', int)
        result = f'({res1}:{res2})'
    else:
        raise ValueError('unknown region id in gp_perf_patterns')

    # res_d = {
    #     'gperftools_top_function1': result,
    # }
    # return res_d
    return result


# @sn.sanity_function
# def gp_tool_reference(obj):
#     '''Dictionary of default ``reference`` for the tool
#     '''
#     ref = ScopedDict()
#     # first, copy the existing self.reference (if any):
#     if obj.reference:
#         for kk in obj.reference:
#             ref[kk] = obj.reference['*:%s' % kk]
#
#     # then add more:
#     myzero_p = (0, None, None, '%')
#     ref['*:gperftools_top_function1'] = myzero_p
#     return ref
