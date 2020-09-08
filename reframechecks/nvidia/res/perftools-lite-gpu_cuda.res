[==========] Running 3 check(s)

[----------] started processing sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_40n_3steps (Tool validation)
[ RUN      ] sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_40n_3steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_40n_3steps (Tool validation)

[----------] started processing sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_80n_3steps (Tool validation)
[ RUN      ] sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_80n_3steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_80n_3steps (Tool validation)

[----------] started processing sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_100n_3steps (Tool validation)
[ RUN      ] sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_100n_3steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_100n_3steps (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/3) sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_40n_3steps on daint:gpu using PrgEnv-gnu [compile: 16.159s run: 43.685s total: 60.633s]
==> setup: 0.151s compile: 16.159s run: 43.685s sanity: 0.030s performance: 0.075s total: 60.633s
[       OK ] (2/3) sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_80n_3steps on daint:gpu using PrgEnv-gnu [compile: 16.595s run: 50.174s total: 68.092s]
==> setup: 0.572s compile: 16.595s run: 50.174s sanity: 0.095s performance: 0.368s total: 68.092s
[       OK ] (3/3) sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_100n_3steps on daint:gpu using PrgEnv-gnu [compile: 16.395s run: 92.883s total: 110.056s]
==> setup: 0.308s compile: 16.395s run: 92.883s sanity: 0.087s performance: 0.100s total: 110.056s
[----------] all spawned checks have finished

[  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))

==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_40n_3steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 2
      * Elapsed: 4.0119 s
      * _Elapsed: 7 s
      * domain_distribute: 0.2429 s
      * mpi_synchronizeHalos: 0.0671 s
      * BuildTree: 0.2642 s
      * FindNeighbors: 3.1839 s
      * Density: 0.053 s
      * EquationOfState: 0.01 s
      * IAD: 0.0557 s
      * MomentumEnergyIAD: 0.0761 s
      * Timestep: 0.0036 s
      * UpdateQuantities: 0.0358 s
      * EnergyConservation: 0.002 s
      * SmoothingLength: 0.0137 s
      * %MomentumEnergyIAD: 1.9 %
      * %Timestep: 0.09 %
      * %mpi_synchronizeHalos: 1.67 %
      * %FindNeighbors: 79.36 %
      * %IAD: 1.39 %
      * host_time%: 100.0 %
      * device_time%: 100.0 %
      * acc_copyin: 490.24 MiBytes
      * acc_copyout: 18.8 MiBytes
------------------------------------------------------------------------------
sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_80n_3steps
   - PrgEnv-gnu
      * num_tasks: 2
      * Elapsed: 32.9057 s
      * _Elapsed: 43 s
      * domain_distribute: 2.0813 s
      * mpi_synchronizeHalos: 0.21 s
      * BuildTree: 2.0356 s
      * FindNeighbors: 26.8083 s
      * Density: 0.355 s
      * EquationOfState: 0.0763 s
      * IAD: 0.3821 s
      * MomentumEnergyIAD: 0.5018 s
      * Timestep: 0.026 s
      * UpdateQuantities: 0.2851 s
      * EnergyConservation: 0.0144 s
      * SmoothingLength: 0.109 s
      * %MomentumEnergyIAD: 1.52 %
      * %Timestep: 0.08 %
      * %mpi_synchronizeHalos: 0.64 %
      * %FindNeighbors: 81.47 %
      * %IAD: 1.16 %
      * host_time%: 100.0 %
      * device_time%: 100.0 %
      * acc_copyin: 3840.0 MiBytes
      * acc_copyout: 118.16 MiBytes
------------------------------------------------------------------------------
sphexa_perftools-gpu-cuda_sqpatch_002mpi_001omp_100n_3steps
   - PrgEnv-gnu
      * num_tasks: 2
      * Elapsed: 66.3381 s
      * _Elapsed: 86 s
      * domain_distribute: 4.088 s
      * mpi_synchronizeHalos: 0.3704 s
      * BuildTree: 3.5407 s
      * FindNeighbors: 54.9545 s
      * Density: 0.6645 s
      * EquationOfState: 0.1489 s
      * IAD: 0.732 s
      * MomentumEnergyIAD: 0.9555 s
      * Timestep: 0.0495 s
      * UpdateQuantities: 0.5553 s
      * EnergyConservation: 0.0273 s
      * SmoothingLength: 0.2126 s
      * %MomentumEnergyIAD: 1.44 %
      * %Timestep: 0.07 %
      * %mpi_synchronizeHalos: 0.56 %
      * %FindNeighbors: 82.84 %
      * %IAD: 1.1 %
      * host_time%: 100.0 %
      * device_time%: 100.0 %
      * acc_copyin: 7489.0 MiBytes
      * acc_copyout: 226.75 MiBytes
