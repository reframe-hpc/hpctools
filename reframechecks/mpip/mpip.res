------------------------------------
@--- MPI Time (seconds) ------------
------------------------------------
Task    AppTime    MPITime     MPI%
   0       4.23     0.0544     1.29
   1       4.23     0.0182     0.43
   2       4.23     0.0538     1.27
   3       4.23     0.0391     0.93
   4       4.23     0.0684     1.62
   5       4.23        3.2    75.65
   *       25.4       3.43    13.53

[----------] waiting for spawned checks to finish
[       OK ] sphexa_mpiP_sqpatch_024mpi_001omp_100n_3steps on dom:gpu using PrgEnv-gnu
[       OK ] sphexa_mpiP_sqpatch_048mpi_001omp_125n_3steps on dom:gpu using PrgEnv-gnu
[       OK ] sphexa_mpiP_sqpatch_096mpi_001omp_157n_3steps on dom:gpu using PrgEnv-gnu
[----------] all spawned checks have finished

[  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))

==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_mpiP_sqpatch_024mpi_001omp_100n_3steps
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 13.4471 s
      * _Elapsed: 15 s
      * domain_distribute: 0.3437 s
      * mpi_synchronizeHalos: 0.5791 s
      * BuildTree: 0 s
      * FindNeighbors: 1.5056 s
      * Density: 1.4952 s
      * EquationOfState: 0.0132 s
      * IAD: 3.6953 s
      * MomentumEnergyIAD: 5.3335 s
      * Timestep: 0.1549 s
      * UpdateQuantities: 0.0211 s
      * EnergyConservation: 0.0082 s
      * SmoothingLength: 0.0133 s
      * %MomentumEnergyIAD: 39.66 %
      * %Timestep: 1.15 %
      * %mpi_synchronizeHalos: 4.31 %
      * %FindNeighbors: 11.2 %
      * %IAD: 27.48 %
      * mpip_avg_app_time: 14.29 s
      * mpip_avg_mpi_time: 1.01 s
      * %mpip_avg_mpi_time: 7.05 %
      * %mpip_avg_mpi_time_max: 70.93 %
      * %mpip_avg_mpi_time_min: 2.38 %
      * %mpip_avg_non_mpi_time: 92.95 %
------------------------------------------------------------------------------
sphexa_mpiP_sqpatch_048mpi_001omp_125n_3steps
   - PrgEnv-gnu
      * num_tasks: 48
      * Elapsed: 14.4052 s
      * _Elapsed: 17 s
      * domain_distribute: 0.2892 s
      * mpi_synchronizeHalos: 1.5153 s
      * BuildTree: 0 s
      * FindNeighbors: 1.4522 s
      * Density: 1.5638 s
      * EquationOfState: 0.0134 s
      * IAD: 3.7332 s
      * MomentumEnergyIAD: 5.3611 s
      * Timestep: 0.23 s
      * UpdateQuantities: 0.0208 s
      * EnergyConservation: 0.003 s
      * SmoothingLength: 0.0132 s
      * %MomentumEnergyIAD: 37.22 %
      * %Timestep: 1.6 %
      * %mpi_synchronizeHalos: 10.52 %
      * %FindNeighbors: 10.08 %
      * %IAD: 25.92 %
      * mpip_avg_app_time: 15.25 s
      * mpip_avg_mpi_time: 2.08 s
      * %mpip_avg_mpi_time: 13.7 %
      * %mpip_avg_mpi_time_max: 95.45 %
      * %mpip_avg_mpi_time_min: 7.75 %
      * %mpip_avg_non_mpi_time: 86.3 %
------------------------------------------------------------------------------
sphexa_mpiP_sqpatch_096mpi_001omp_157n_3steps
   - PrgEnv-gnu
      * num_tasks: 96
      * Elapsed: 16.0431 s
      * _Elapsed: 19 s
      * domain_distribute: 0.3262 s
      * mpi_synchronizeHalos: 0.8793 s
      * BuildTree: 0 s
      * FindNeighbors: 1.557 s
      * Density: 1.5117 s
      * EquationOfState: 0.0132 s
      * IAD: 3.6159 s
      * MomentumEnergyIAD: 5.2786 s
      * Timestep: 2.5658 s
      * UpdateQuantities: 0.0202 s
      * EnergyConservation: 0.0092 s
      * SmoothingLength: 0.0131 s
      * %MomentumEnergyIAD: 32.9 %
      * %Timestep: 15.99 %
      * %mpi_synchronizeHalos: 5.48 %
      * %FindNeighbors: 9.71 %
      * %IAD: 22.54 %
      * mpip_avg_app_time: 16.88 s
      * mpip_avg_mpi_time: 3.59 s
      * %mpip_avg_mpi_time: 21.27 %
      * %mpip_avg_mpi_time_max: 95.86 %
      * %mpip_avg_mpi_time_min: 15.75 %
      * %mpip_avg_non_mpi_time: 78.73 %
