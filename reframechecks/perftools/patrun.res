[----------] waiting for spawned checks to finish
[       OK ] sphexa_patrun_sqpatch_024mpi_001omp_100n_4steps on daint:gpu using PrgEnv-gnu
[       OK ] sphexa_patrun_sqpatch_048mpi_001omp_125n_4steps on daint:gpu using PrgEnv-gnu
[       OK ] sphexa_patrun_sqpatch_096mpi_001omp_157n_4steps on daint:gpu using PrgEnv-gnu
[----------] all spawned checks have finished

[  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))
==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_patrun_sqpatch_024mpi_001omp_100n_4steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 16.8663 s
      * _Elapsed: 20 s
      * domain_distribute: 0.4024 s
      * mpi_synchronizeHalos: 0.7946 s
      * BuildTree: 0 s
      * FindNeighbors: 1.9453 s
      * Density: 1.9057 s
      * EquationOfState: 0.0171 s
      * IAD: 4.6122 s
      * MomentumEnergyIAD: 6.6714 s
      * Timestep: 0.1536 s
      * UpdateQuantities: 0.0245 s
      * EnergyConservation: 0.0034 s
      * SmoothingLength: 0.0168 s
      * %MomentumEnergyIAD: 39.55 %
      * %Timestep: 0.91 %
      * %mpi_synchronizeHalos: 4.71 %
      * %FindNeighbors: 11.53 %
      * %IAD: 27.35 %
      * patrun_cn: 1
      * patrun_wallt_max: 17.8108 s
      * patrun_wallt_avg: 17.8041 s
      * patrun_wallt_min: 17.7824 s
      * patrun_mem_max: 36.7 MiBytes
      * patrun_mem_min: 35.6 MiBytes
      * patrun_memory_traffic_global: 50.71 GB
      * patrun_memory_traffic_local: 50.71 GB
      * %patrun_memory_traffic_peak: 4.2 %
      * patrun_memory_traffic: 2.11 GB
      * patrun_ipc: 0.66
      * %patrun_stallcycles: 59.8 %
      * %patrun_user: 88.6 % (slow: 1646.0 smp [pe13] / mean:1563.4 median:1623.5 / fast:451.0 [pe23])
      * %patrun_mpi: 6.6 % (slow: 1265.0 smp [pe23] / mean:116.5 median:55.5 / fast:37.0 [pe7])
      * %patrun_etc: 4.8 % (slow: 109.0 smp [pe17] / mean:84.3 median:84.5 / fast:51.0 [pe23])
      * %patrun_total: 100.0 % (slow: 1768.0 smp [pe20] / mean:1764.2 median:1764.5 / fast:1756.0 [pe8])
      * %patrun_user_slowest: 93.2 % (pe.13)
      * %patrun_mpi_slowest: 2.2 % (pe.13)
      * %patrun_etc_slowest: 4.7 % (pe.13)
      * %patrun_user_fastest: 25.5 % (pe.23)
      * %patrun_mpi_fastest: 71.6 % (pe.23)
      * %patrun_etc_fastest: 2.9 % (pe.23)
      * %patrun_avg_usr_reported: 88.4 %
      * %patrun_avg_mpi_reported: 6.6 %
      * %patrun_avg_etc_reported: 5.0 %
      * %patrun_hotspot1: 36.6 % (sphexa::sph::computeMomentumAndEnergyIADImpl<>)
      * %patrun_mpi_h1: 4.0 % (MPI_Recv)
      * %patrun_mpi_h1_imb: 94.3 % (MPI_Recv)
      * patrun_avg_energy: 3069.0 J
      * patrun_avg_power: 172.376 W
------------------------------------------------------------------------------
sphexa_patrun_sqpatch_048mpi_001omp_125n_4steps
   - PrgEnv-gnu
      * num_tasks: 48
      * Elapsed: 18.0427 s
      * _Elapsed: 23 s
      * domain_distribute: 0.3898 s
      * mpi_synchronizeHalos: 1.6116 s
      * BuildTree: 0 s
      * FindNeighbors: 1.8666 s
      * Density: 1.9936 s
      * EquationOfState: 0.017 s
      * IAD: 4.706 s
      * MomentumEnergyIAD: 6.7254 s
      * Timestep: 0.4579 s
      * UpdateQuantities: 0.0245 s
      * EnergyConservation: 0.0061 s
      * SmoothingLength: 0.0166 s
      * %MomentumEnergyIAD: 37.27 %
      * %Timestep: 2.54 %
      * %mpi_synchronizeHalos: 8.93 %
      * %FindNeighbors: 10.35 %
      * %IAD: 26.08 %
      * patrun_cn: 2
      * patrun_wallt_max: 19.012 s
      * patrun_wallt_avg: 19.0043 s
      * patrun_wallt_min: 18.9892 s
      * patrun_mem_max: 56.4 MiBytes
      * patrun_mem_min: 50.0 MiBytes
      * patrun_memory_traffic_global: 53.4 GB
      * patrun_memory_traffic_local: 53.4 GB
      * %patrun_memory_traffic_peak: 4.1 %
      * patrun_memory_traffic: 2.12 GB
      * patrun_ipc: 0.66
      * %patrun_stallcycles: 56.8 %
      * %patrun_user: 82.6 % (slow: 1665.0 smp [pe10] / mean:1555.0 median:1618.0 / fast:25.0 [pe46])
      * %patrun_mpi: 13.4 % (slow: 1818.0 smp [pe47] / mean:252.0 median:185.5 / fast:131.0 [pe10])
      * %patrun_etc: 4.0 % (slow: 95.0 smp [pe7] / mean:76.1 median:76.0 / fast:42.0 [pe47])
      * %patrun_total: 100.0 % (slow: 1887.0 smp [pe47] / mean:1883.2 median:1884.0 / fast:1870.0 [pe33])
      * %patrun_user_slowest: 88.7 % (pe.10)
      * %patrun_mpi_slowest: 7.0 % (pe.10)
      * %patrun_etc_slowest: 4.3 % (pe.10)
      * %patrun_user_fastest: 1.3 % (pe.46)
      * %patrun_mpi_fastest: 96.3 % (pe.46)
      * %patrun_etc_fastest: 2.3 % (pe.46)
      * %patrun_avg_usr_reported: 82.4 %
      * %patrun_avg_mpi_reported: 13.4 %
      * %patrun_avg_etc_reported: 4.2 %
      * %patrun_hotspot1: 34.4 % (sphexa::sph::computeMomentumAndEnergyIADImpl<>)
      * %patrun_mpi_h1: 5.2 % (MPI_Recv)
      * %patrun_mpi_h1_imb: 28.8 % (MPI_Recv)
      * patrun_avg_energy: 3416.0 J
      * patrun_avg_power: 179.7485 W
------------------------------------------------------------------------------
sphexa_patrun_sqpatch_096mpi_001omp_157n_4steps
   - PrgEnv-gnu
      * num_tasks: 96
      * Elapsed: 17.6017 s
      * _Elapsed: 23 s
      * domain_distribute: 0.4415 s
      * mpi_synchronizeHalos: 1.1111 s
      * BuildTree: 0 s
      * FindNeighbors: 2.0165 s
      * Density: 1.9299 s
      * EquationOfState: 0.0166 s
      * IAD: 4.5522 s
      * MomentumEnergyIAD: 6.5513 s
      * Timestep: 0.6166 s
      * UpdateQuantities: 0.0235 s
      * EnergyConservation: 0.0162 s
      * SmoothingLength: 0.0163 s
      * %MomentumEnergyIAD: 37.22 %
      * %Timestep: 3.5 %
      * %mpi_synchronizeHalos: 6.31 %
      * %FindNeighbors: 11.46 %
      * %IAD: 25.86 %
      * patrun_cn: 4
      * patrun_wallt_max: 18.7552 s
      * patrun_wallt_avg: 18.7445 s
      * patrun_wallt_min: 18.7213 s
      * patrun_mem_max: 60.1 MiBytes
      * patrun_mem_min: 53.8 MiBytes
      * patrun_memory_traffic_global: 53.95 GB
      * patrun_memory_traffic_local: 53.95 GB
      * %patrun_memory_traffic_peak: 4.2 %
      * patrun_memory_traffic: 2.15 GB
      * patrun_ipc: 0.64
      * %patrun_stallcycles: 58.0 %
      * %patrun_user: 84.7 % (slow: 1677.0 smp [pe14] / mean:1570.2 median:1630.0 / fast:26.0 [pe95])
      * %patrun_mpi: 11.1 % (slow: 1793.0 smp [pe94] / mean:205.9 median:146.0 / fast:91.0 [pe56])
      * %patrun_etc: 4.2 % (slow: 97.0 smp [pe63] / mean:78.3 median:78.5 / fast:38.0 [pe93])
      * %patrun_total: 100.0 % (slow: 1862.0 smp [pe92] / mean:1854.4 median:1854.0 / fast:1835.0 [pe5])
      * %patrun_user_slowest: 90.5 % (pe.14)
      * %patrun_mpi_slowest: 5.6 % (pe.14)
      * %patrun_etc_slowest: 3.9 % (pe.14)
      * %patrun_user_fastest: 1.4 % (pe.95)
      * %patrun_mpi_fastest: 96.3 % (pe.95)
      * %patrun_etc_fastest: 2.3 % (pe.95)
      * %patrun_avg_usr_reported: 84.5 %
      * %patrun_avg_mpi_reported: 11.1 %
      * %patrun_avg_etc_reported: 4.4 %
      * %patrun_hotspot1: 34.7 % (sphexa::sph::computeMomentumAndEnergyIADImpl<>)
      * %patrun_mpi_h1: 6.6 % (MPI_Allreduce)
      * %patrun_mpi_h1_imb: 94.1 % (MPI_Allreduce)
      * patrun_avg_energy: 3274.0 J
      * patrun_avg_power: 174.665 W
