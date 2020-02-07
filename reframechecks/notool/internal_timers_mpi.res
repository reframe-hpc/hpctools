starttime=1579725956
# domain::distribute: 0.0983208s
# mpi::synchronizeHalos: 0.0341479s
# domain::buildTree: 0.084004s
# updateTasks: 0.000900428s
# FindNeighbors: 0.354712s
# Density: 0.296224s
# EquationOfState: 0.00244751s
# mpi::synchronizeHalos: 0.0770191s
# IAD: 0.626564s
# mpi::synchronizeHalos: 0.344856s
# MomentumEnergyIAD: 1.05951s
# Timestep: 0.621583s
# UpdateQuantities: 0.00498222s
# EnergyConservation: 0.00137127s
# UpdateSmoothingLength: 0.00321161s
### Check ### Global Tree Nodes: 1097, Particles: 40947, Halos: 109194
### Check ### Computational domain: -49.5 49.5 -49.5 49.5 -50 50
### Check ### Total Neighbors: 244628400, Avg neighbor count per particle: 244
### Check ### Total time: 1.1e-06, current time-step: 1.1e-06
### Check ### Total energy: 2.08323e+10, (internal: 1e+06, cinetic: 2.08313e+10)
=== Total time for iteration(0) 3.61153s
stoptime=1579725961

PERFORMANCE REPORT
-----------------------------------------------
sphexa_timers_sqpatch_024mpi_001omp_100n_0steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 3.6201 s
      * _Elapsed: 5 s
      * domain_build: 0.0956 s
      * mpi_synchronizeHalos: 0.4567 s
      * BuildTree: 0 s
      * FindNeighbors: 0.3547 s
      * Density: 0.296 s
      * EquationOfState: 0.0024 s
      * IAD: 0.6284 s
      * MomentumEnergyIAD: 1.0914 s
      * Timestep: 0.6009 s
      * UpdateQuantities: 0.0051 s
      * EnergyConservation: 0.0012 s
      * SmoothingLength: 0.0033 s
      * %MomentumEnergyIAD: 30.15 %
      * %Timestep: 16.6 %
      * %mpi_synchronizeHalos: 12.62 %
      * %FindNeighbors: 9.8 %
      * %IAD: 17.36 %
