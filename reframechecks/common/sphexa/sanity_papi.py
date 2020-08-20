# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


@sn.sanity_function
def pw_perf_patterns(obj):
    '''Reports hardware counter values from the tool

    .. code-block::

     collector                       time time (%)   PAPI_REF_CYC   PAPI_L2_DCM
     --------------------------------------------------------------------------
     computeMomentumAndEnergyIAD   0.6816   100.00     1770550470       2438527
                                                                        ^^^^^^^

    '''
    regex = r'^computeMomentumAndEnergyIAD\s+\S+\s+\S+\s+\S+\s+(?P<hwc>\d+)$'
    hwc_min = sn.min(sn.extractall(regex, obj.stderr, 'hwc', int))
    hwc_avg = sn.round(sn.avg(sn.extractall(regex, obj.stderr, 'hwc', int)), 1)
    hwc_max = sn.max(sn.extractall(regex, obj.stderr, 'hwc', int))
    res_d = {
        'papiwrap_hwc_min': hwc_min,
        'papiwrap_hwc_avg': hwc_avg,
        'papiwrap_hwc_max': hwc_max,
    }
    return res_d


@sn.sanity_function
def pw_tool_reference(obj):
    '''Dictionary of default ``reference`` for the tool
    '''
    ref = ScopedDict()
    # first, copy the existing self.reference (if any):
    if obj.reference:
        for kk in obj.reference:
            ref[kk] = obj.reference['*:%s' % kk]

    # then add more:
    myzero = (0, None, None, '')
    ref['*:papiwrap_hwc_min'] = myzero
    ref['*:papiwrap_hwc_avg'] = myzero
    ref['*:papiwrap_hwc_max'] = myzero
    return ref
