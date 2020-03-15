[----------] waiting for spawned checks to finish
[       OK ] sphexa_patrun_sqpatch_024mpi_001omp_100n_2steps on daint:gpu using PrgEnv-gnu
[       OK ] sphexa_patrun_sqpatch_048mpi_001omp_125n_2steps on daint:gpu using PrgEnv-gnu
[       OK ] sphexa_patrun_sqpatch_096mpi_001omp_157n_2steps on daint:gpu using PrgEnv-gnu
[----------] all spawned checks have finished

[  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))
==============================================================================

PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_patrun_sqpatch_024mpi_001omp_100n_2steps
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 9.9621 s
      * _Elapsed: 13 s
      * domain_distribute: 0.2595 s
      * mpi_synchronizeHalos: 0.4512 s
      * BuildTree: 0 s
      * FindNeighbors: 1.1777 s
      * Density: 1.0982 s
      * EquationOfState: 0.0097 s
      * IAD: 2.7133 s
      * MomentumEnergyIAD: 3.9158 s
      * Timestep: 0.1067 s
      * UpdateQuantities: 0.0147 s
      * EnergyConservation: 0.0019 s
      * SmoothingLength: 0.0101 s
      * %MomentumEnergyIAD: 39.31 %
      * %Timestep: 1.07 %
      * %mpi_synchronizeHalos: 4.53 %
      * %FindNeighbors: 11.82 %
      * %IAD: 27.24 %
      * patrun_cn: 1
      * patrun_wallt_max: 10.9292 s
      * patrun_wallt_avg: 10.9222 s
      * patrun_wallt_min: 10.9019 s
      * patrun_mem_max: 41.8 MiBytes
      * patrun_mem_min: 35.5 MiBytes
      * patrun_memory_traffic_global: 31.06 GB
      * patrun_memory_traffic_local: 31.06 GB
      * %patrun_memory_traffic_peak: 4.2 %
      * patrun_memory_traffic: 1.29 GB
      * patrun_ipc: 0.68
      * %patrun_stallcycles: 58.3 %
      * %patrun_avg_usr: 86.7 %
      * %patrun_avg_mpi: 6.6 %
      * %patrun_avg_etc: 6.7 %
      * %patrun_hotspot1: 35.4 % (sphexa::sph::computeMomentumAndEnergyIADImpl<>)
      * %patrun_mpi_h1: 4.0 % (MPI_Recv)
      * %patrun_mpi_h1_imb: 94.0 % (MPI_Recv)
      * patrun_avg_power: 172.034 W
------------------------------------------------------------------------------
sphexa_patrun_sqpatch_048mpi_001omp_125n_2steps
   - PrgEnv-gnu
      * num_tasks: 48
      * Elapsed: 10.5494 s
      * _Elapsed: 15 s
      * domain_distribute: 0.2345 s
      * mpi_synchronizeHalos: 0.8505 s
      * BuildTree: 0 s
      * FindNeighbors: 1.1166 s
      * Density: 1.1834 s
      * EquationOfState: 0.0097 s
      * IAD: 2.7673 s
      * MomentumEnergyIAD: 4.0016 s
      * Timestep: 0.2005 s
      * UpdateQuantities: 0.0143 s
      * EnergyConservation: 0.0026 s
      * SmoothingLength: 0.01 s
      * %MomentumEnergyIAD: 37.93 %
      * %Timestep: 1.9 %
      * %mpi_synchronizeHalos: 8.06 %
      * %FindNeighbors: 10.58 %
      * %IAD: 26.23 %
      * patrun_cn: 2
      * patrun_wallt_max: 11.4836 s
      * patrun_wallt_avg: 11.4734 s
      * patrun_wallt_min: 11.457 s
      * patrun_mem_max: 76.3 MiBytes
      * patrun_mem_min: 41.5 MiBytes
      * patrun_memory_traffic_global: 34.21 GB
      * patrun_memory_traffic_local: 34.21 GB
      * %patrun_memory_traffic_peak: 4.4 %
      * patrun_memory_traffic: 1.35 GB
      * patrun_ipc: 0.67
      * %patrun_stallcycles: 57.0 %
      * %patrun_avg_usr: 83.0 %
      * %patrun_avg_mpi: 10.8 %
      * %patrun_avg_etc: 6.2 %
      * %patrun_hotspot1: 34.3 % (sphexa::sph::computeMomentumAndEnergyIADImpl<>)
      * %patrun_mpi_h1: 5.2 % (MPI_Allreduce)
      * %patrun_mpi_h1_imb: 96.5 % (MPI_Allreduce)
      * patrun_avg_power: 176.9315 W
------------------------------------------------------------------------------
sphexa_patrun_sqpatch_096mpi_001omp_157n_2steps
   - PrgEnv-gnu
      * num_tasks: 96
      * Elapsed: 11.6253 s
      * _Elapsed: 17 s
      * domain_distribute: 0.2299 s
      * mpi_synchronizeHalos: 0.7762 s
      * BuildTree: 0 s
      * FindNeighbors: 1.2119 s
      * Density: 1.1493 s
      * EquationOfState: 0.0096 s
      * IAD: 2.6812 s
      * MomentumEnergyIAD: 3.9174 s
      * Timestep: 1.4355 s
      * UpdateQuantities: 0.0135 s
      * EnergyConservation: 0.003 s
      * SmoothingLength: 0.0097 s
      * %MomentumEnergyIAD: 33.7 %
      * %Timestep: 12.35 %
      * %mpi_synchronizeHalos: 6.68 %
      * %FindNeighbors: 10.42 %
      * %IAD: 23.06 %
      * patrun_cn: 4
      * patrun_wallt_max: 12.6109 s
      * patrun_wallt_avg: 12.6028 s
      * patrun_wallt_min: 12.5795 s
      * patrun_mem_max: 58.0 MiBytes
      * patrun_mem_min: 53.8 MiBytes
      * patrun_memory_traffic_global: 33.65 GB
      * patrun_memory_traffic_local: 33.65 GB
      * %patrun_memory_traffic_peak: 3.9 %
      * patrun_memory_traffic: 1.34 GB
      * patrun_ipc: 0.67
      * %patrun_stallcycles: 53.7 %
      * %patrun_avg_usr: 76.2 %
      * %patrun_avg_mpi: 18.2 %
      * %patrun_avg_etc: 5.6 %
      * %patrun_hotspot1: 31.0 % (sphexa::sph::computeMomentumAndEnergyIADImpl<>)
      * %patrun_mpi_h1: 13.5 % (MPI_Allreduce)
      * %patrun_mpi_h1_imb: 86.5 % (MPI_Allreduce)
      * patrun_avg_power: 174.64375 W
