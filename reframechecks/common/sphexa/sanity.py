import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict


# {{{ stdout:
# new # domain::distribute: 0.00520047s
# new # mpi::synchronizeHalos: 0.000225831s
# new # domain::buildTree: 0.000213763s
# new # updateTasks: 0.000205979s
# new # FindNeighbors: 0.000209769s
# new # Density: 0.000205721s
# new # EquationOfState: 0.000200632s
# new # mpi::synchronizeHalos: 0.000202482s
# new # IAD: 0.000200948s
# new # mpi::synchronizeHalos: 0.000202029s
# new # MomentumEnergyIAD: 0.000208447s
# new # Timestep: 3.02641s
# new # UpdateQuantities: 0.000228198s
# new # EnergyConservation: 0.00259888s
# new # UpdateSmoothingLength: 0.000214242s
# new ### Check ### Global Tree Nodes: 73, Particles: 0, Halos: 0
# new ### Check ### Computational domain: -48.7503 48.7503 -48.7503 48.7503 -50 50
# new ### Check ### Total Neighbors: 15933232, Avg neighbor count per particle: 248
# new ### Check ### Total time: 2.31e-06, current time-step: 1.21e-06
# new ### Check ### Total energy: 2.08214e+10, (internal: 999895, cinetic: 2.08204e+10)
# new === Total time for iteration(1) 3.04279s

# rpt PERFORMANCE REPORT
# rpt ------------------------------------------------------------------------------
# rpt sphexa_timers_sqpatch_036mpi_001omp_100n_30steps
# rpt - dom:mc
#rpt    - PrgEnv-gnu
# rpt       * num_tasks: 36
# rpt       * Elapsed: 45.1345 s
# rpt       * _Elapsed: 47 s
# rpt       * domain_build: 0.8706 s
# rpt       * mpi_synchronizeHalos: 5.6912 s
# rpt       * BuildTree: 0 s
# rpt       * FindNeighbors: 5.4531 s
# rpt       * Density: 3.2674 s
# rpt       * EquationOfState: 0.0563 s
# rpt       * IAD: 5.1007 s
# rpt       * MomentumEnergyIAD: 13.6478 s
# rpt       * Timestep: 10.137 s
# rpt       * UpdateQuantities: 0.0654 s
# rpt       * EnergyConservation: 0.0062 s
# rpt       * SmoothingLength: 0.0563 s
# rpt       * top1-MomentumEnergyIAD: 30.24 %
# rpt       * top2-Timestep: 22.46 %
# rpt       * top3-mpi_synchronizeHalos: 12.61 %
# rpt       * top4-FindNeighbors: 12.08 %
# rpt       * top5-IAD: 11.3 %
# }}}

# {{{ sanity_function: date as timer
@sn.sanity_function
def elapsed_time_from_date(self):
    '''Reports elapsed time in seconds using the linux date command
    '''
    regex_start_sec = r'^starttime=(?P<sec>\d+.\d+)'
    regex_stop_sec = r'^stoptime=(?P<sec>\d+.\d+)'
    start_sec = sn.extractall(regex_start_sec, self.stdout, 'sec', int)
    stop_sec = sn.extractall(regex_stop_sec, self.stdout, 'sec', int)
    return (stop_sec[0] - start_sec[0])
# }}}

# {{{ sanity_function: internal timers
# @property
@sn.sanity_function
def seconds_elaps(self):
    '''Reports elapsed time in seconds using the internal timer from the code
    '''
    regex = '^=== Total time for iteration\(\d+\)\s+(?P<sec>\d+\D\d+)s'
    # regex = r'^=== Total time for iteration\(\d+\)\s+(?P<sec>\d+\D\d+)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_build(self):
    '''Reports `domain::distribute` time in seconds using the internal timer
    from the code
    '''
    regex = '^# domain::distribute:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_halos(self):
    '''Reports `mpi::synchronizeHalos` time in seconds using the internal timer
    from the code
    '''
    regex = '^# mpi::synchronizeHalos:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_tree(self):
    '''Reports `domain:BuildTree` time in seconds using the internal timer
    from the code
    '''
    regex = '^# domain:BuildTree:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_neigh(self):
    '''Reports `FindNeighbors` time in seconds using the internal timer
    from the code
    '''
    regex = '^# FindNeighbors:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_denst(self):
    '''Reports `Density` time in seconds using the internal timer
    from the code
    '''
    regex = '^# Density:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_state(self):
    '''Reports `EquationOfState` time in seconds using the internal timer
    from the code
    '''
    regex = '^# EquationOfState:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_iad(self):
    '''Reports `IAD` time in seconds using the internal timer
    from the code
    '''
    regex = '^# IAD:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_energ(self):
    '''Reports `MomentumEnergyIAD` time in seconds using the internal timer
    from the code
    '''
    regex = '^# MomentumEnergyIAD:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_step(self):
    '''Reports `Timestep` time in seconds using the internal timer
    from the code
    '''
    regex = '^# Timestep:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_updat(self):
    '''Reports `UpdateQuantities` time in seconds using the internal timer
    from the code
    '''
    regex = '^# UpdateQuantities:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_consv(self):
    '''Reports `EnergyConservation` time in seconds using the internal timer
    from the code
    '''
    regex = '^# EnergyConservation:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)


@sn.sanity_function
def seconds_smoothinglength(self):
    '''Reports `UpdateSmoothingLength` time in seconds using the internal timer
    from the code
    '''
    regex = '^# UpdateSmoothingLength:\s+(?P<sec>.*)s'
    return sn.round(sn.sum(sn.extractall(regex, self.stdout, 'sec', float)), 4)
# }}}

# {{{ sanity_function: internal timers %
@sn.sanity_function
def pctg_MomentumEnergyIAD(obj):
    return sn.round((100 * seconds_energ(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_Timestep(obj):
    return sn.round((100 * seconds_step(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_mpi_synchronizeHalos(obj):
    return sn.round((100 * seconds_halos(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_FindNeighbors(obj):
    return sn.round((100 * seconds_neigh(obj) / seconds_elaps(obj)), 2)


@sn.sanity_function
def pctg_IAD(obj):
    return sn.round((100 * seconds_iad(obj) / seconds_elaps(obj)), 2)

# del @property
# del @sn.sanity_function
# del def walltime_pctg_neigh(self):
# del     return sn.round((100 * self.seconds_neigh / self.seconds_elaps), 2)
# del
# del @property
# del @sn.sanity_function
# del def walltime_pctg_denst(self):
# del     return sn.round((100 * self.seconds_denst / self.seconds_elaps), 2)
# del
# del @property
# del @sn.sanity_function
# del def walltime_pctg_energ(self):
# del     return sn.round((100 * self.seconds_energ / self.seconds_elaps), 2)

# }}}
