PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_scorepS+T_sqpatch_024mpi_001omp_100n_4steps_5000000cycles
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 20.5236 s
      * _Elapsed: 27 s
      * domain_distribute: 0.4484 s
      * mpi_synchronizeHalos: 2.4355 s
      * BuildTree: 0 s
      * FindNeighbors: 1.875 s
      * Density: 1.8138 s
      * EquationOfState: 0.019 s
      * IAD: 3.7302 s
      * MomentumEnergyIAD: 6.1363 s
      * Timestep: 3.5853 s
      * UpdateQuantities: 0.0272 s
      * EnergyConservation: 0.0087 s
      * SmoothingLength: 0.0232 s
      * %MomentumEnergyIAD: 29.9 %
      * %Timestep: 17.47 %
      * %mpi_synchronizeHalos: 11.87 %
      * %FindNeighbors: 9.14 %
      * %IAD: 18.18 %
      * max_ipc_rk0: 1.297827 ins/cyc
      * max_rumaxrss_rk0: 127448 kilobytes
------------------------------------------------------------------------------
sphexa_scorepS+T_sqpatch_192mpi_001omp_198n_4steps_5000000cycles
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 192
      * Elapsed: 63.8218 s
      * _Elapsed: 288 s
      * domain_distribute: 0.7738 s
      * mpi_synchronizeHalos: 1.5403 s
      * BuildTree: 0 s
      * FindNeighbors: 1.7797 s
      * Density: 1.8065 s
      * EquationOfState: 0.0189 s
      * IAD: 4.3111 s
      * MomentumEnergyIAD: 6.2124 s
      * Timestep: 46.8353 s
      * UpdateQuantities: 0.0284 s
      * EnergyConservation: 0.0431 s
      * SmoothingLength: 0.0188 s
      * %MomentumEnergyIAD: 9.73 %
      * %Timestep: 73.38 %
      * %mpi_synchronizeHalos: 2.41 %
      * %FindNeighbors: 2.79 %
      * %IAD: 6.75 %
      * max_ipc_rk0: 1.310455 ins/cyc
      * max_rumaxrss_rk0: 149828 kilobytes
