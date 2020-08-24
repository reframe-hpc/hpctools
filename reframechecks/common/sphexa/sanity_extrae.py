# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ sanity_function: extrae
# @property

@sn.sanity_function
def extrae_version(obj):
    '''Checks tool's version. As there is no ``--version`` flag available,
    we read the version from extrae_version.h and compare it to our reference

    .. code-block::

      > cat $EBROOTEXTRAE/include/extrae_version.h
      #define EXTRAE_MAJOR 3
      #define EXTRAE_MINOR 7
      #define EXTRAE_MICRO 1
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '371',
        'dom': '381',
    }
    ref_file = obj.version_file
    regex = (r'#define EXTRAE_MAJOR (?P<v1>\d)\n'
             r'#define EXTRAE_MINOR (?P<v2>\d)\n'
             r'#define EXTRAE_MICRO (?P<v3>\d)')
    v1 = sn.extractsingle(regex, ref_file, 'v1')
    v2 = sn.extractsingle(regex, ref_file, 'v2')
    v3 = sn.extractsingle(regex, ref_file, 'v3')
    version = v1 + v2 + v3
    TorF = sn.assert_eq(
        version, reference_tool_version[obj.current_system.name])
    return TorF


@sn.sanity_function
def create_sh(obj):
    '''Create a wrapper script to insert Extrae libs (with ``LD_PRELOAD``) into
    the executable at runtime
    '''
    multistr = ("#!/bin/bash\n"
                "export EXTRAE_HOME=$EBROOTEXTRAE\n"
                "source $EXTRAE_HOME/etc/extrae.sh\n"
                "export EXTRAE_CONFIG_FILE=./extrae.xml\n"
                "export LD_PRELOAD=$EXTRAE_HOME/lib/libmpitrace.so\n"
                "%s \"$@\"" % obj.target_executable)
    return multistr


@sn.sanity_function
def rpt_mpistats(obj):
    '''Reports statistics (histogram of MPI communications) from the comms.dat
    file

    .. code-block::

      #_of_comms %_of_bytes_sent # histogram bin
      466        0.00            # 10 B
      3543       0.25            # 100 B
      11554     11.69            # 1 KB
      29425     88.05            # 10 KB
      0          0.00            # 100 KB
      0          0.00            # 1 MB
      0          0.00            # 10 MB
      0          0.00            # >10 MB
    '''
    regex = r'^(?P<tenB_n>\d+)\s+(?P<tenB_b>\d+\D\d+)\n'
    regex += r'(?P<hundB_n>\d+)\s+(?P<hundB_b>\d+\D\d+)\n'
    regex += r'(?P<oneKB_n>\d+)\s+(?P<oneKB_b>\d+\D\d+)\n'
    regex += r'(?P<tenKB_n>\d+)\s+(?P<tenKB_b>\d+\D\d+)\n'
    regex += r'(?P<hundKB_n>\d+)\s+(?P<hundKB_b>\d+\D\d+)\n'
    regex += r'(?P<oneMB_n>\d+)\s+(?P<oneMB_b>\d+\D\d+)\n'
    regex += r'(?P<tenMB_n>\d+)\s+(?P<tenMB_b>\d+\D\d+)\n'
    regex += r'(?P<hundMB_n>\d+)\s+(?P<hundMB_b>\d+\D\d+)'
    #
    tenB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'tenB_n', int)
    tenB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'tenB_b', float)
    hundB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'hundB_n', int)
    hundB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'hundB_b', float)
    oneKB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'oneKB_n', int)
    oneKB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'oneKB_b', float)
    tenKB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'tenKB_n', int)
    tenKB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'tenKB_b', float)
    hundKB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'hundKB_n', int)
    hundKB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'hundKB_b', float)
    oneMB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'oneMB_n', int)
    oneMB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'oneMB_b', float)
    tenMB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'tenMB_n', int)
    tenMB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'tenMB_b', float)
    hundMB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'hundMB_n', int)
    hundMB_b = sn.extractsingle(regex, obj.rpt_mpistats, 'hundMB_b', float)
    #
    res_d = {
        'num_comms_0-10B': tenB_n,
        'num_comms_10B-100B': hundB_n,
        'num_comms_100B-1KB': oneKB_n,
        'num_comms_1KB-10KB': tenKB_n,
        'num_comms_10KB-100KB': hundKB_n,
        'num_comms_100KB-1MB': oneMB_n,
        'num_comms_1MB-10MB': tenMB_n,
        'num_comms_10MB': hundMB_n,
        #
        '%_of_bytes_sent_0-10B': tenB_b,
        '%_of_bytes_sent_10B-100B': hundB_b,
        '%_of_bytes_sent_100B-1KB': oneKB_b,
        '%_of_bytes_sent_1KB-10KB': tenKB_b,
        '%_of_bytes_sent_10KB-100KB': hundKB_b,
        '%_of_bytes_sent_100KB-1MB': oneMB_b,
        '%_of_bytes_sent_1MB-10MB': tenMB_b,
        '%_of_bytes_sent_10MB': hundMB_b,
    }
    # works too:
    # res_d = {}
    # res_d['tenB_n'] = tenB_n
    # res_d['tenB_b'] = tenB_b
    return res_d


@sn.sanity_function
def tool_reference_scoped_d(self):
    '''Sets a set of tool perf_reference to be shared between the tests.
    '''
    myzero = (0, None, None, '')
    myzero_p = (0, None, None, '%')
    myreference = ScopedDict({
        '*': {
            'num_comms_0-10B': myzero,
            'num_comms_10B-100B': myzero,
            'num_comms_100B-1KB': myzero,
            'num_comms_1KB-10KB': myzero,
            'num_comms_10KB-100KB': myzero,
            'num_comms_100KB-1MB': myzero,
            'num_comms_1MB-10MB': myzero,
            'num_comms_10MB': myzero,
            #
            '%_of_bytes_sent_0-10B': myzero_p,
            '%_of_bytes_sent_10B-100B': myzero_p,
            '%_of_bytes_sent_100B-1KB': myzero_p,
            '%_of_bytes_sent_1KB-10KB': myzero_p,
            '%_of_bytes_sent_10KB-100KB': myzero_p,
            '%_of_bytes_sent_100KB-1MB': myzero_p,
            '%_of_bytes_sent_1MB-10MB': myzero_p,
            '%_of_bytes_sent_10MB': myzero_p,
        }
    })
    return myreference


# {{{
# @sn.sanity_function
# def rpt_mpistats_mini(obj):
#     '''Reports statistics (histogram of MPI communications) from comms.dat
#     file
#
#     '''
#     regex = '^(?P<tenB_n>\d+)\s+(?P<tenB_b>\d+\D\d+)\n'
#     regex += '(?P<hundB_n>\d+)\s+(?P<hundB_b>\d+\D\d+)\n'
#     regex += '(?P<oneKB_n>\d+)\s+(?P<oneKB_b>\d+\D\d+)\n'
#     regex += '(?P<tenKB_n>\d+)\s+(?P<tenKB_b>\d+\D\d+)\n'
#     regex += '(?P<hundKB_n>\d+)\s+(?P<hundKB_b>\d+\D\d+)\n'
#     regex += '(?P<oneMB_n>\d+)\s+(?P<oneMB_b>\d+\D\d+)\n'
#     regex += '(?P<tenMB_n>\d+)\s+(?P<tenMB_b>\d+\D\d+)\n'
#     regex += '(?P<hundMB_n>\d+)\s+(?P<hundMB_b>\d+\D\d+)'
#     tenB_n = sn.extractsingle(regex, obj.rpt_mpistats, 'tenB_n', int)
#     # works too:
#     res_d = {}
#     res_d['num_comms_0-10B'] = tenB_n
#     # res_d = {
#     #     'num_comms_0-10B': tenB_n,
#     #         }
#
#     return res_d
#
#
# @sn.sanity_function
# def tool_reference_scoped_d_mini(self):
#     '''Sets a set of tool perf_reference to be shared between the tests.
#     '''
#     myzero = (0, None, None, '')
#     myzero_p = (0, None, None, '%')
#     myreference = ScopedDict({
#         '*': {
#             'num_comms_0-10B': myzero,
#             }
#         })
#     return myreference
# }}}
# }}}
