# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import json
import cxxfilt
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ sanity_function: otf2cli
@sn.sanity_function
def otf2cli_read_json_rpt(obj):
    '''Reads the json file reported by ``otf_profiler``,
    needed for perf_patterns.
    '''
    rpt_f = os.path.join(obj.stagedir, obj.rpt_jsn)
    with open(rpt_f) as f:
        j_d = json.load(f)
    f.close()
    j_d['HWCounters'] = {}
    if j_d['HardwareCounters'] == []:
        obj.rusage_metric = 'none'
        j_d['HWCounters']['rusage_name'] = 'none'
        j_d['HWCounters']['rusage'] = 0
        # j_d['HWCounters'][obj.rusage_metric] = 0
    else:
        obj.rusage_metric = j_d['HardwareCounters'][0]
        j_d['HWCounters']['rusage_name'] = j_d['HardwareCounters'][0]
        j_d['HWCounters']['rusage'] = j_d['HardwareCounters'][1]

    if j_d['Functions']['COMPILER'] == {}:
        j_d['Functions']['COMPILER']['Count'] = 0
        j_d['Functions']['COMPILER']['Time'] = 0

    if j_d['Functions']['MPI'] == {}:
        j_d['Functions']['MPI']['Count'] = 0
        j_d['Functions']['MPI']['Time'] = 0

    if j_d['Functions']['OpenACC'] == {}:
        j_d['Functions']['OpenACC']['Count'] = 0
        j_d['Functions']['OpenACC']['Time'] = 0

    if j_d['Messages']['MPI'] == {}:
        j_d['Messages']['MPI']['Count'] = 0
        j_d['Messages']['MPI']['Bytes'] = 0

    if j_d['CollectiveOperations']['MPI'] == {}:
        j_d['CollectiveOperations']['MPI']['Count'] = 0
        j_d['CollectiveOperations']['MPI']['Bytes'] = 0

    return j_d


@sn.sanity_function
def otf2cli_perf_patterns(obj):
    '''Dictionary of default ``perf_patterns`` for the tool
    '''
    json_d = otf2cli_read_json_rpt(obj)
    res_d = {
        'otf2_serial_time': json_d['SerialRegionTime'],
        'otf2_parallel_time': json_d['ParallelRegionTime'],
        'otf2_func_compiler_cnt': json_d['Functions']['COMPILER']['Count'],
        'otf2_func_compiler_time': json_d['Functions']['COMPILER']['Time'],
        'otf2_func_mpi_cnt': json_d['Functions']['MPI']['Count'],
        'otf2_func_mpi_time': json_d['Functions']['MPI']['Time'],
        'otf2_func_openacc_cnt': json_d['Functions']['OpenACC']['Count'],
        'otf2_func_openacc_time': json_d['Functions']['OpenACC']['Time'],
        'otf2_messages_mpi_cnt': json_d['Messages']['MPI']['Count'],
        'otf2_messages_mpi_size': json_d['Messages']['MPI']['Bytes'],
        'otf2_coll_mpi_cnt': json_d['CollectiveOperations']['MPI']['Count'],
        'otf2_coll_mpi_size': json_d['CollectiveOperations']['MPI']['Bytes'],
        'otf2_rusage': json_d['HWCounters']['rusage'],
    }
    return res_d


@sn.sanity_function
def otf2cli_tool_reference(obj):
    '''Dictionary of default ``reference`` for the tool
    '''
    ref = ScopedDict()
    # first, copy the existing self.reference (if any):
    if obj.reference:
        for kk in obj.reference:
            ref[kk] = obj.reference['*:%s' % kk]

    # then add more:
    myzero = (0, None, None, '')
    myzero_b = (0, None, None, 'Bytes')
    myzero_rusage = (0, None, None, '%s' % obj.rusage_name)
    ref['*:otf2_serial_time'] = myzero
    ref['*:otf2_parallel_time'] = myzero
    ref['*:otf2_func_compiler_cnt'] = myzero
    ref['*:otf2_func_compiler_time'] = myzero
    ref['*:otf2_func_mpi_cnt'] = myzero
    ref['*:otf2_func_mpi_time'] = myzero
    ref['*:otf2_func_openacc_cnt'] = myzero
    ref['*:otf2_func_openacc_time'] = myzero
    ref['*:otf2_messages_mpi_cnt'] = myzero
    ref['*:otf2_messages_mpi_size'] = myzero_b
    ref['*:otf2_coll_mpi_cnt'] = myzero
    ref['*:otf2_coll_mpi_size'] = myzero_b
    ref['*:otf2_rusage'] = myzero_rusage
    return ref


@sn.sanity_function
def otf2cli_metric_name(obj):
    '''If SCOREP_METRIC_RUSAGE is defined then return the metric name.
    '''
    result = ''
    if 'SCOREP_METRIC_RUSAGE' in obj.variables:
        if len(obj.variables['SCOREP_METRIC_RUSAGE']) > 0:
            len_rusage = len(obj.variables['SCOREP_METRIC_RUSAGE'].split(','))
            if len_rusage > 1:
                result = '(deactivated)'
            else:
                result = obj.variables['SCOREP_METRIC_RUSAGE'].split(',')[0]
    return result


@sn.sanity_function
def otf2cli_metric_flag(obj):
    '''If SCOREP_METRIC_RUSAGE is defined then return the ``otf-profiler``
    flags so that it will not segfault.
    '''
    otf_flag = ''
    if 'SCOREP_METRIC_RUSAGE' in obj.variables:
        if len(obj.variables['SCOREP_METRIC_RUSAGE']) > 0:
            len_rusage = len(obj.variables['SCOREP_METRIC_RUSAGE'].split(','))
            if len_rusage > 1:
                # use --no-metrics to avoid segfault
                # https://github.com/score-p/otf2_cli_profile/issues/26
                otf_flag = '--no-metrics'
    return otf_flag
# }}}
