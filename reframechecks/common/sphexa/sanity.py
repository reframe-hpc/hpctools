# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ sanity_function: date as timer
@sn.sanity_function
def elapsed_time_from_date(self):
    '''Reports elapsed time in seconds using the linux date command:

    .. code-block::

     starttime=1579725956
     stoptime=1579725961
     reports: _Elapsed: 5 s
    '''
    regex_start_sec = r'^starttime=(?P<sec>\d+.\d+)'
    regex_stop_sec = r'^stoptime=(?P<sec>\d+.\d+)'
    if 'self.rpt_dep' in globals():
        rpt = self.rpt_dep
    else:
        rpt = self.stdout

    start_sec = sn.extractall(regex_start_sec, rpt, 'sec', int)
    stop_sec = sn.extractall(regex_stop_sec, rpt, 'sec', int)
    return (stop_sec[0] - start_sec[0])
# }}}


# {{{ seconds_timers
@sn.sanity_function
def seconds_timers(self, region):
    '''Reports timings (in seconds) using the internal timer from the code

    .. code-block::

      # domain::sync: 0.118225s
      # updateTasks: 0.00561256s
      # FindNeighbors: 0.266282s
      # Density: 0.120372s
      # EquationOfState: 0.00255166s
      # mpi::synchronizeHalos: 0.116917s
      # IAD: 0.185804s
      # mpi::synchronizeHalos: 0.0850162s
      # MomentumEnergyIAD: 0.423282s
      # Timestep: 0.0405346s
      # UpdateQuantities: 0.0140938s
      # EnergyConservation: 0.0224118s
      # UpdateSmoothingLength: 0.00413466s
    '''
    if region == 1:
        regex = r'^# domain::sync:\s+(?P<sec>.*)s'
    elif region == 2:
        regex = r'^# updateTasks:\s+(?P<sec>.*)s'
    elif region == 3:
        regex = r'^# FindNeighbors:\s+(?P<sec>.*)s'
    elif region == 4:
        regex = r'^# Density:\s+(?P<sec>.*)s'
    elif region == 5:
        regex = r'^# EquationOfState:\s+(?P<sec>.*)s'
    elif region == 6:
        regex = r'^# mpi::synchronizeHalos:\s+(?P<sec>.*)s'
    elif region == 7:
        regex = r'^# IAD:\s+(?P<sec>.*)s'
    elif region == 8:
        regex = r'^# MomentumEnergyIAD:\s+(?P<sec>.*)s'
    elif region == 9:
        regex = r'^# Timestep:\s+(?P<sec>.*)s'
    elif region == 10:
        regex = r'^# UpdateQuantities:\s+(?P<sec>.*)s'
    elif region == 11:
        regex = r'^# EnergyConservation:\s+(?P<sec>.*)s'
    elif region == 12:
        regex = r'^# UpdateSmoothingLength:\s+(?P<sec>.*)s'
    else:
        raise ValueError('unknown region id in sanity_function')

    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)
# }}}


#  {{{ sanity_function: internal timers
# @property
@sn.sanity_function
def seconds_elaps(self):
    '''Reports elapsed time in seconds using the internal timer from the code

    .. code-block::

      === Total time for iteration(0) 3.61153s
      reports: * Elapsed: 3.6115 s
    '''
    regex = r'^=== Total time for iteration\(\d+\)\s+(?P<sec>\d+\D\d+)s'
    # regex = r'^=== Total time for iteration\(\d+\)\s+(?P<sec>\d+\D\d+)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)
# }}}


# {{{ sanity_function: internal timers %
@sn.sanity_function
def pctg_MomentumEnergyIAD(obj):
    '''reports: * %MomentumEnergyIAD: 30.15 %'''
    return sn.round((100 * seconds_timers(obj, 8) / seconds_elaps(obj)), 2)
    # return sn.round((100 * seconds_energ(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_Timestep(obj):
    '''reports: * %Timestep: 16.6 %'''
    return sn.round((100 * seconds_timers(obj, 9) / seconds_elaps(obj)), 2)
    # return sn.round((100 * seconds_step(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_mpi_synchronizeHalos(obj):
    '''reports: * %mpi_synchronizeHalos: 12.62 %'''
    return sn.round((100 * seconds_timers(obj, 6) / seconds_elaps(obj)), 2)
    # return sn.round((100 * seconds_halos(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_FindNeighbors(obj):
    '''reports: * %FindNeighbors: 9.8 %'''
    return sn.round((100 * seconds_timers(obj, 3) / seconds_elaps(obj)), 2)
    # return sn.round((100 * seconds_neigh(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_IAD(obj):
    '''reports: * %IAD: 17.36 %'''
    return sn.round((100 * seconds_timers(obj, 7) / seconds_elaps(obj)), 2)
    # return sn.round((100 * seconds_iad(obj) / seconds_elaps(obj)), 2)

# }}}


# {{{ sanity_function: perf patterns for internal timers
@sn.sanity_function
def basic_perf_patterns(obj):
    '''Sets a set of basic perf_patterns to be shared between the tests.
    The equivalent from inside the check is:

    .. code-block:: python

     perf_patterns = {
         'Elapsed': sphs.seconds_elaps(self)
         }
    '''
    perf_patterns = {
        'Elapsed':              seconds_elaps(obj),
        '_Elapsed':             elapsed_time_from_date(obj),
        #
        'domain_sync': seconds_timers(obj, 1),
        'updateTasks': seconds_timers(obj, 2),
        'FindNeighbors': seconds_timers(obj, 3),
        'Density': seconds_timers(obj, 4),
        'EquationOfState': seconds_timers(obj, 5),
        'mpi_synchronizeHalos': seconds_timers(obj, 6),
        'IAD': seconds_timers(obj, 7),
        'MomentumEnergyIAD': seconds_timers(obj, 8),
        'Timestep': seconds_timers(obj, 9),
        'UpdateQuantities': seconds_timers(obj, 10),
        'EnergyConservation': seconds_timers(obj, 11),
        'UpdateSmoothingLength': seconds_timers(obj, 12),
        # 'domain_distribute'
        # 'BuildTree'
    }
    # top%
    perf_patterns.update({
        '%MomentumEnergyIAD':    pctg_MomentumEnergyIAD(obj),
        '%Timestep':             pctg_Timestep(obj),
        '%mpi_synchronizeHalos': pctg_mpi_synchronizeHalos(obj),
        '%FindNeighbors':        pctg_FindNeighbors(obj),
        '%IAD':                  pctg_IAD(obj),
    })
    return perf_patterns
# }}}


# {{{ sanity_function: perf reference for internal timers
@sn.sanity_function
def basic_reference_scoped_d(self):
    '''Sets a set of basic perf_reference to be shared between the tests.
    The equivalent from inside the check is:

    .. code-block:: python

      self.reference = {
          '*': {
              'Elapsed': (0, None, None, 's'),
          }
      }
    '''
    myzero_s = (0, None, None, 's')
    myzero_p = (0, None, None, '%')
    # self.myreference = ScopedDict({
    myreference = ScopedDict({
        '*': {
            'Elapsed': myzero_s,
            '_Elapsed': myzero_s,
            # timers
            'domain_distribute': myzero_s,
            'mpi_synchronizeHalos': myzero_s,
            'BuildTree': myzero_s,
            'FindNeighbors': myzero_s,
            'Density': myzero_s,
            'EquationOfState': myzero_s,
            'IAD': myzero_s,
            'MomentumEnergyIAD': myzero_s,
            'Timestep': myzero_s,
            'UpdateQuantities': myzero_s,
            'EnergyConservation': myzero_s,
            'SmoothingLength': myzero_s,
            # top%
            '%MomentumEnergyIAD': myzero_p,
            '%mpi_synchronizeHalos': myzero_p,
            '%FindNeighbors': myzero_p,
            '%IAD': myzero_p,
        }
    })
    return myreference
    # return self.myreference
# }}}


# {{{ TODO: stdout:
# ### Check ### Global Tree Nodes: 1097, Particles: 40947, Halos: 109194
# ### Check ### Computational domain: -49.5 49.5 -49.5 49.5 -50 50
# ### Check ### Total Neighbors: 244628400, Avg neighbor count per particle:244
# ### Check ### Total time: 1.1e-06, current time-step: 1.1e-06
# ### Check ### Total energy: 2.08323e+10, (internal: 1e+06, cinetic: 2.03e+10)
# }}}
