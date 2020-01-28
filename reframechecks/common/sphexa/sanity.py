import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ TODO: stdout:
# ### Check ### Global Tree Nodes: 1097, Particles: 40947, Halos: 109194
# ### Check ### Computational domain: -49.5 49.5 -49.5 49.5 -50 50
# ### Check ### Total Neighbors: 244628400, Avg neighbor count per particle: 244
# ### Check ### Total time: 1.1e-06, current time-step: 1.1e-06
# ### Check ### Total energy: 2.08323e+10, (internal: 1e+06, cinetic: 2.08313e+10)
# }}}

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
    start_sec = sn.extractall(regex_start_sec, self.stdout, 'sec', int)
    stop_sec = sn.extractall(regex_stop_sec, self.stdout, 'sec', int)
    return (stop_sec[0] - start_sec[0])
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
    regex = '^=== Total time for iteration\(\d+\)\s+(?P<sec>\d+\D\d+)s'
    # regex = r'^=== Total time for iteration\(\d+\)\s+(?P<sec>\d+\D\d+)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_domaindistrib(self):
    '''Reports `domain::distribute` time in seconds using the internal timer from the code

    .. code-block::

      # domain::distribute: 0.0983208s
      reports: * domain_distribute: 0.0983 s
    '''
    regex = '^# domain::distribute:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_halos(self):
    '''Reports `mpi::synchronizeHalos` time in seconds using the internal timer from the code

    .. code-block::

      # mpi::synchronizeHalos: 0.0341479s
      # mpi::synchronizeHalos: 0.0770191s
      # mpi::synchronizeHalos: 0.344856s
      reports: * mpi_synchronizeHalos: 0.4560 s
    '''
    regex = '^# mpi::synchronizeHalos:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_tree(self):
    '''Reports `domain:BuildTree` time in seconds using the internal timer from the code

    .. code-block::

      # domain::buildTree: 0.084004s
      reports: * BuildTree: 0 s
    '''
    regex = '^# domain:BuildTree:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_updateTasks(self):
    '''Reports `updateTasks` time in seconds using the internal timer from the code

    .. code-block::

      # updateTasks: 0.000900428s
      reports: ...
    '''
    regex = '^# updateTasks:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_neigh(self):
    '''Reports `FindNeighbors` time in seconds using the internal timer from the code

    .. code-block::

      # FindNeighbors: 0.354712s
      reports: * FindNeighbors: 0.3547 s
    '''
    regex = '^# FindNeighbors:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_denst(self):
    '''Reports `Density` time in seconds using the internal timer from the code

    .. code-block::

      # Density: 0.296224s
      reports: * Density: 0.296 s
    '''
    regex = '^# Density:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_state(self):
    '''Reports `EquationOfState` time in seconds using the internal timer from the code

    .. code-block::

      # EquationOfState: 0.00244751s
      reports: * EquationOfState: 0.0024 s
    '''
    regex = '^# EquationOfState:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_iad(self):
    '''Reports `IAD` time in seconds using the internal timer from the code

    .. code-block::

      # IAD: 0.626564s
      reports: * IAD: 0.6284 s
    '''
    regex = '^# IAD:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_energ(self):
    '''Reports `MomentumEnergyIAD` time in seconds using the internal timer from the code

    .. code-block::

       # MomentumEnergyIAD: 1.05951s
       reports: * MomentumEnergyIAD: 1.0595 s

    '''
    regex = '^# MomentumEnergyIAD:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_step(self):
    '''Reports `Timestep` time in seconds using the internal timer from the code

    .. code-block::

      # Timestep: 0.621583s
      reports: * Timestep: 0.6215 s
    '''
    regex = '^# Timestep:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_updat(self):
    '''Reports `UpdateQuantities` time in seconds using the internal timer from the code

    .. code-block::

      # UpdateQuantities: 0.00498222s
      reports: * UpdateQuantities: 0.0049 s
    '''
    regex = '^# UpdateQuantities:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_consv(self):
    '''Reports `EnergyConservation` time in seconds using the internal timer from the code

    .. code-block::

      # EnergyConservation: 0.00137127s
      reports: * EnergyConservation: 0.0013 s
    '''
    regex = '^# EnergyConservation:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_smoothinglength(self):
    '''Reports `UpdateSmoothingLength` time in seconds using the internal timer from the code

    .. code-block::

      # UpdateSmoothingLength: 0.00321161s
      reports: * SmoothingLength: 0.0032 s
    '''
    regex = '^# UpdateSmoothingLength:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)
# }}}

# {{{ sanity_function: internal timers %
@sn.sanity_function
def pctg_MomentumEnergyIAD(obj):
    '''reports: * %MomentumEnergyIAD: 30.15 %'''
    return sn.round((100 * seconds_energ(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_Timestep(obj):
    '''reports: * %Timestep: 16.6 %'''
    return sn.round((100 * seconds_step(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_mpi_synchronizeHalos(obj):
    '''reports: * %mpi_synchronizeHalos: 12.62 %'''
    return sn.round((100 * seconds_halos(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_FindNeighbors(obj):
    '''reports: * %FindNeighbors: 9.8 %'''
    return sn.round((100 * seconds_neigh(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_IAD(obj):
    '''reports: * %IAD: 17.36 %'''
    return sn.round((100 * seconds_iad(obj) / seconds_elaps(obj)), 2)

# }}}
