[==========] Running 1 check(s)

[----------] started processing sphexa_nvprofcuda_sqpatch_002mpi_001omp_40n_3steps (Tool validation)
[ RUN      ] sphexa_nvprofcuda_sqpatch_002mpi_001omp_40n_3steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_nvprofcuda_sqpatch_002mpi_001omp_40n_3steps (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/1) sphexa_nvprofcuda_sqpatch_002mpi_001omp_40n_3steps on daint:gpu using PrgEnv-gnu [compile: 8.437s run: 9.818s total: 18.407s]
==> setup: 0.033s compile: 8.437s run: 9.818s sanity: 0.060s performance: 0.035s total: 18.407s
[----------] all spawned checks have finished

[  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))
==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_nvprofcuda_sqpatch_002mpi_001omp_40n_3steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 2
      * Elapsed: 1.2884 s
      * _Elapsed: 4 s
      * domain_distribute: 0.0397 s
      * mpi_synchronizeHalos: 0.0226 s
      * BuildTree: 0.0427 s
      * FindNeighbors: 0.9736 s
      * Density: 0.0525 s
      * EquationOfState: 0.0091 s
      * IAD: 0.0552 s
      * MomentumEnergyIAD: 0.0752 s
      * Timestep: 0.0012 s
      * UpdateQuantities: 0.0054 s
      * EnergyConservation: 0.0006 s
      * SmoothingLength: 0.0101 s
      * %MomentumEnergyIAD: 5.84 %
      * %Timestep: 0.09 %
      * %mpi_synchronizeHalos: 1.75 %
      * %FindNeighbors: 75.57 %
      * %IAD: 4.28 %
      * %cudaMemcpy: 45.6 %
      * %CUDA_memcpy_HtoD_time: 52.2 %
      * %CUDA_memcpy_DtoH_time: 2.1 %
      * CUDA_memcpy_HtoD_KiB: -1 KiB
      * CUDA_memcpy_DtoH_KiB: -1 KiB
      * %computeMomentumAndEnergyIAD: 25.1 %
      * %computeIAD: 11.6 %
