Reframe version: 3.0-dev6 (rev: 3f0c45d4)
Launched on host: daint101

[----------] started processing sphexa_cudagdb_sqpatch_001mpi_001omp_30n_0steps (Tool validation)
[ RUN      ] sphexa_cudagdb_sqpatch_001mpi_001omp_30n_0steps on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_cudagdb_sqpatch_001mpi_001omp_30n_0steps (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/1) sphexa_cudagdb_sqpatch_001mpi_001omp_30n_0steps on daint:gpu using PrgEnv-gnu
[----------] all spawned checks have finished

[  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))
==============================================================================

PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_cudagdb_sqpatch_001mpi_001omp_30n_0steps
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 1
      * info_kernel_nblocks: 106
      * info_kernel_nthperblock: 256
      * info_kernel_np: 27000
      * info_threads_np: 27008
      * SMs: 56
      * WarpsPerSM: 64
      * LanesPerWarp: 32
      * max_threads_per_sm: 2048
      * max_threads_per_device: 114688
      * best_cubesize_per_device: 49
      * cubesize: 30
      * vec_len: 27000
      * threadid_of_last_sm: 14335
      * last_threadid: 27007
------------------------------------------------------------------------------
