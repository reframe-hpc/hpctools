[==========] Running 3 check(s)

[----------] started processing sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_TMA (Tool validation)
[ RUN      ] sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_TMA on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_TMA (Tool validation)

[----------] started processing sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_MEM (Tool validation)
[ RUN      ] sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_MEM on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_MEM (Tool validation)

[----------] started processing sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_CLOCK (Tool validation)
[ RUN      ] sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_CLOCK on daint:gpu using PrgEnv-gnu
[----------] finished processing sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_CLOCK (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] (1/3) sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_TMA on daint:gpu using PrgEnv-gnu
[       OK ] (2/3) sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_MEM on daint:gpu using PrgEnv-gnu
[       OK ] (3/3) sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_CLOCK on daint:gpu using PrgEnv-gnu
[----------] all spawned checks have finished

[  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))
==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_TMA
- daint:gpu
   - PrgEnv-gnu
      * num_tasks: 1
      * Elapsed: 9.6342 s
      * _Elapsed: 12 s
      * domain_distribute: 0.0466 s
      * mpi_synchronizeHalos: 0.0002 s
      * BuildTree: 0.0415 s
      * FindNeighbors: 1.3547 s
      * Density: 1.1326 s
      * EquationOfState: 0.0126 s
      * IAD: 2.5873 s
      * MomentumEnergyIAD: 4.4339 s
      * Timestep: 0.0015 s
      * UpdateQuantities: 0.0074 s
      * EnergyConservation: 0.0007 s
      * SmoothingLength: 0.0139 s
      * %MomentumEnergyIAD: 46.02 %
      * %Timestep: 0.02 %
      * %mpi_synchronizeHalos: 0.0 %
      * %FindNeighbors: 14.06 %
      * %IAD: 26.86 %
      * likwid_runtime: 10.1767 s
      * likwid_cpi: 0.9806 
      * %likwid_topdown_frontend: 1.1896 %
      * %likwid_topdown_speculation: 4.9775 %
      * %likwid_topdown_retiring: 26.1019 %
      * %likwid_topdown_backend: 67.731 %
------------------------------------------------------------------------------
sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_MEM
   - PrgEnv-gnu
      * num_tasks: 1
      * Elapsed: 9.6676 s
      * _Elapsed: 11 s
      * domain_distribute: 0.0476 s
      * mpi_synchronizeHalos: 0.0002 s
      * BuildTree: 0.0423 s
      * FindNeighbors: 1.3742 s
      * Density: 1.1313 s
      * EquationOfState: 0.0126 s
      * IAD: 2.5785 s
      * MomentumEnergyIAD: 4.4561 s
      * Timestep: 0.0015 s
      * UpdateQuantities: 0.0074 s
      * EnergyConservation: 0.0007 s
      * SmoothingLength: 0.014 s
      * %MomentumEnergyIAD: 46.09 %
      * %Timestep: 0.02 %
      * %mpi_synchronizeHalos: 0.0 %
      * %FindNeighbors: 14.21 %
      * %IAD: 26.67 %
      * likwid_runtime: 10.1956 s
      * likwid_cpi: 0.9816 
      * likwid_memory_bw: 196.6158 MBytes/s
      * likwid_memory: 2.0046 GBytes
------------------------------------------------------------------------------
sphexa_likwid_sqpatch_001mpi_001omp_35n_5steps_CLOCK
   - PrgEnv-gnu
      * num_tasks: 1
      * Elapsed: 9.6508 s
      * _Elapsed: 12 s
      * domain_distribute: 0.0469 s
      * mpi_synchronizeHalos: 0.0003 s
      * BuildTree: 0.0418 s
      * FindNeighbors: 1.362 s
      * Density: 1.1201 s
      * EquationOfState: 0.0126 s
      * IAD: 2.5756 s
      * MomentumEnergyIAD: 4.4666 s
      * Timestep: 0.0014 s
      * UpdateQuantities: 0.0073 s
      * EnergyConservation: 0.0008 s
      * SmoothingLength: 0.0141 s
      * %MomentumEnergyIAD: 46.28 %
      * %Timestep: 0.01 %
      * %mpi_synchronizeHalos: 0.0 %
      * %FindNeighbors: 14.11 %
      * %IAD: 26.69 %
      * likwid_runtime: 10.1941 s
      * likwid_cpi: 0.9798 
      * likwid_energy: 411.4058 J
      * likwid_power: 40.3573 W
------------------------------------------------------------------------------
