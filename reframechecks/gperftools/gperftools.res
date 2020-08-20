[==========] Running 1 check(s)


[----------] started processing sphexa_gperf_sqpatch_012mpi_001omp_78n_1steps (Tool validation)
[ RUN      ] sphexa_gperf_sqpatch_012mpi_001omp_78n_1steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_gperf_sqpatch_012mpi_001omp_78n_1steps (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/1) sphexa_gperf_sqpatch_012mpi_001omp_78n_1steps on daint:gpu using PrgEnv-gnu [compile: 8.735s run: 11.154s total: 20.095s]
==> setup: 0.028s compile: 8.735s run: 11.154s sanity: 0.126s performance: 0.030s total: 20.095s
[----------] all spawned checks have finished

[  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))

==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_gperf_sqpatch_012mpi_001omp_78n_1steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 12
      * Elapsed: 3.5115 s
      * _Elapsed: 6 s
      * domain_distribute: 0.0496 s
      * mpi_synchronizeHalos: 0.1076 s
      * BuildTree: 0.0602 s
      * FindNeighbors: 0.512 s
      * Density: 0.4155 s
      * EquationOfState: 0.004 s
      * IAD: 0.9173 s
      * MomentumEnergyIAD: 1.4097 s
      * Timestep: 0.0256 s
      * UpdateQuantities: 0.0036 s
      * EnergyConservation: 0.0008 s
      * SmoothingLength: 0.005 s
      * %MomentumEnergyIAD: 40.15 %
      * %Timestep: 0.73 %
      * %mpi_synchronizeHalos: 3.06 %
      * %FindNeighbors: 14.58 %
      * %IAD: 26.12 %
      * gperftools_top_function1: 12.78 
------------------------------------------------------------------------------
