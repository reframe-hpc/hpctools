[==========] Running 1 check(s)

[----------] started processing sphexa_papiw_sqpatch_012mpi_001omp_78n_0steps (Tool validation)
[ RUN      ] sphexa_papiw_sqpatch_012mpi_001omp_78n_0steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_papiw_sqpatch_012mpi_001omp_78n_0steps (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/1) sphexa_papiw_sqpatch_012mpi_001omp_78n_0steps on daint:gpu using PrgEnv-gnu [compile: 9.565s run: 8.549s total: 18.250s]
==> setup: 0.030s compile: 9.565s run: 8.549s sanity: 0.054s performance: 0.028s total: 18.250s
[----------] all spawned checks have finished

[  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))

==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_papiw_sqpatch_012mpi_001omp_78n_0steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 12
      * Elapsed: 1.7092 s
      * _Elapsed: 4 s
      * domain_distribute: 0.0225 s
      * mpi_synchronizeHalos: 0.0612 s
      * BuildTree: 0.0317 s
      * FindNeighbors: 0.2573 s
      * Density: 0.2038 s
      * EquationOfState: 0.0015 s
      * IAD: 0.4401 s
      * MomentumEnergyIAD: 0.6759 s
      * Timestep: 0.0102 s
      * UpdateQuantities: 0.0017 s
      * EnergyConservation: 0.0005 s
      * SmoothingLength: 0.0025 s
      * %MomentumEnergyIAD: 39.54 %
      * %Timestep: 0.6 %
      * %mpi_synchronizeHalos: 3.58 %
      * %FindNeighbors: 15.05 %
      * %IAD: 25.75 %
      * papiwrap_hwc_min: 404229 
      * papiwrap_hwc_avg: 2286110.9 
      * papiwrap_hwc_max: 2737786 
------------------------------------------------------------------------------

