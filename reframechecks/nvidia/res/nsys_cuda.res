PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_nsyscuda_sqpatch_002mpi_001omp_100n_0steps
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 2
      * Elapsed: 3.6542 s
      * _Elapsed: 36 s
      * domain_distribute: 0.1663 s
      * mpi_synchronizeHalos: 0.0374 s
      * BuildTree: 0 s
      * FindNeighbors: 2.7624 s
      * Density: 0.1225 s
      * EquationOfState: 0.0187 s
      * IAD: 0.1518 s
      * MomentumEnergyIAD: 0.1824 s
      * Timestep: 0.0028 s
      * UpdateQuantities: 0.0143 s
      * EnergyConservation: 0.0018 s
      * SmoothingLength: 0.0276 s
      * %MomentumEnergyIAD: 4.99 %
      * %Timestep: 0.08 %
      * %mpi_synchronizeHalos: 1.02 %
      * %FindNeighbors: 75.6 %
      * %IAD: 4.15 %
      * %cudaMemcpy: 94.7 %
      * %CUDA_memcpy_HtoD_time: 97.5 %
      * %CUDA_memcpy_DtoH_time: 2.5 %
      * CUDA_memcpy_HtoD_KiB: 1929453.4 KiB
      * CUDA_memcpy_DtoH_KiB: 62826.5 KiB
      * %computeMomentumAndEnergyIAD: 45.4 %
      * %computeIAD: 35.4 %
