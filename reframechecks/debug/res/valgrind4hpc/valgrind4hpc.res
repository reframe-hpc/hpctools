[==========] Running 1 check(s)

[----------] started processing sphexa_valgrind4hpc_sqpatch_012mpi_001omp_20n_0steps (Tool validation)
[ RUN      ] sphexa_valgrind4hpc_sqpatch_012mpi_001omp_20n_0steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_valgrind4hpc_sqpatch_012mpi_001omp_20n_0steps (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/1) sphexa_valgrind4hpc_sqpatch_012mpi_001omp_20n_0steps on daint:gpu using PrgEnv-gnu [compile: 5.379s run: 34.391s total: 39.901s]
==> setup: 0.018s compile: 5.379s run: 34.391s sanity: 0.061s performance: 0.030s total: 39.901s
[----------] all spawned checks have finished

[  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))

==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_valgrind4hpc_sqpatch_012mpi_001omp_20n_0steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 12
      * Elapsed: 10.8635 s
      * _Elapsed: 27 s
      * domain_distribute: 0.4425 s
      * mpi_synchronizeHalos: 0.5094 s
      * BuildTree: 0.9389 s
      * FindNeighbors: 1.5847 s
      * Density: 1.0027 s
      * EquationOfState: 0.0115 s
      * IAD: 1.6033 s
      * MomentumEnergyIAD: 4.6046 s
      * Timestep: 0.0438 s
      * UpdateQuantities: 0.0682 s
      * EnergyConservation: 0.0093 s
      * SmoothingLength: 0.0101 s
      * %MomentumEnergyIAD: 42.39 %
      * %Timestep: 0.4 %
      * %mpi_synchronizeHalos: 4.69 %
      * %FindNeighbors: 14.59 %
      * %IAD: 14.76 %
      * v4hpc_errors_found: 1 
      * v4hpc_heap: 0 bytes
      * v4hpc_blocks: 0 
------------------------------------------------------------------------------
