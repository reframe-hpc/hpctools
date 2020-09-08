# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ perftools-lite-gpu
# {{{ tool version
@sn.sanity_function
def tool_version(obj):
    '''Checks tool's version:

    .. code-block::

      > pat_report -V
      CrayPat/X:  Version 20.08.0 Revision 28ef35c9f  07/08/20 20:40:20
                          ^^^^^^^
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '20.08.0',
        'dom': '20.08.0',
    }
    regex = r'CrayPat\/X:\s+Version\s+(?P<toolversion>\S+)\s+'
    res_version = sn.extractsingle(regex, obj.version_rpt, 'toolversion')
    TorF = sn.assert_eq(res_version,
                        reference_tool_version[obj.current_system.name])
    return TorF
# }}}


# {{{ H2D, D2H
regex_gpu = (
    r'Table \d+:\s+Time and Bytes Transferred for Accelerator Regions'
    r'(.*\n){6}\s+(?P<host_p>\S+)%\s+\|\s+\S+\s+\|\s+(?P<acc_p>\S+)%'
    r'\s+\|\s+\S+\s+\|\s+(?P<mb_in>\S+)\s+\|\s+(?P<mb_out>\S+).*Total')


@sn.sanity_function
def ptlgpu_report_host_pct(self):
    '''Reports gpu metrics measured by the tool (Host Time%)

    .. code-block::

      > job.stdout
      # Table 2:  Time and Bytes Transferred for Accelerator Regions
      #  Host | Host |    Acc |  Acc |  Acc Copy |  Acc Copy | Events |Function
      # Time% | Time |  Time% | Time |        In |       Out |        |PE=HIDE
              |      |        |      | (MiBytes) | (MiBytes) |        |
      #100.0% | 0.68 | 100.0% | 0.68 |     3,840 |    118.16 |    216 | Total
      #^^^^^           ^^^^^               ^^^^^      ^^^^^^
      # |----------------------------------------------------------------------
      # |  61.5% | 0.42 |  61.5% | 0.42 |3,840 | 118.16 |    204 | cudaMemcpy
      # |  38.5% | 0.26 |  38.5% | 0.26 |   -- |     -- |     12 | cudaLaunch
      #                                                            Kernel
      # |======================================================================
    '''
    rpt = os.path.join(self.stagedir, self.rpt)
    result = sn.extractsingle(regex_gpu, rpt, 'host_p', float)
    return result


@sn.sanity_function
def ptlgpu_report_device_pct(self):
    '''Reports gpu metrics measured by the tool (Acc Time%)
    '''
    rpt = os.path.join(self.stagedir, self.rpt)
    result = sn.extractsingle(regex_gpu, rpt, 'acc_p', float)
    return result


@sn.sanity_function
def ptlgpu_report_device_copyin(self):
    '''Reports gpu metrics measured by the tool (Acc CopyIn MiBytes)
    '''
    rpt = os.path.join(self.stagedir, self.rpt)
    result = sn.extractsingle(regex_gpu, rpt, 'mb_in',
                              conv=lambda x: float(x.replace(',', '')))
    # result = sn.extractsingle(regex_gpu, rpt, 'mb_in', float)
    return result


@sn.sanity_function
def ptlgpu_report_device_copyout(self):
    '''Reports gpu metrics measured by the tool (Acc CopyOut MiBytes)
    '''
    rpt = os.path.join(self.stagedir, self.rpt)
    result = sn.extractsingle(regex_gpu, rpt, 'mb_out',
                              conv=lambda x: float(x.replace(',', '')))
    return result
# }}}


# {{{ tool perf_patterns
@sn.sanity_function
def tool_perf_patterns(obj):
    '''Dictionary of default perf_patterns for the tool
    '''
    res_d = {
        'host_time%': ptlgpu_report_host_pct(obj),
        'device_time%': ptlgpu_report_device_pct(obj),
        'acc_copyin': ptlgpu_report_device_copyin(obj),
        'acc_copyout': ptlgpu_report_device_copyout(obj),
    }
    return res_d

# }}}
# }}}
