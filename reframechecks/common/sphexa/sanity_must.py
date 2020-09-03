# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ sanity_function: must
# @property

@sn.sanity_function
def tool_version(obj):
    '''Checks tool's version:

    .. code-block::

      > mustrun --help 2>&1
      "mustrun" from MUST v1.6
      returns: True or False
    '''
    reference_tool_version = {
        'daint': 'v1.6',
        'dom': 'v1.6',
    }
    regex = (r'"mustrun" from MUST (?P<tool_version>\S+)')
    version = sn.extractsingle(regex, obj.version_rpt, 'tool_version')
    TorF = sn.assert_eq(
        version, reference_tool_version[obj.current_system.name])
    return TorF
# }}}
