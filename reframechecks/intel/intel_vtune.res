Available analysis types are: ``vtune -h collect``

    .. code-block:: none

      hotspots            <--
      memory-consumption
      uarch-exploration
      memory-access
      threading
      hpc-performance
      system-overview
      graphics-rendering
      io
      fpga-interaction
      gpu-offload
      gpu-hotspots
      throttling
      platform-profiler

Available reports are: ``vtune -h report``

    .. code-block:: none

      affinity
      callstacks    Display CPU or wait time for callstacks.
      gprof-cc      Display CPU or wait time in the gprof-like format.
      hotspots      Display CPU time.
      hw-events     Display hardware events.
      platform-power-analysis
                    Display CPU sleep time, wake-up reasons and CPU frequency
                    scaling time.
      summary       Display data about overall performance.
      top-down      Display a call tree for your target application and provide
                    CPU and wait time for each function.
      vectspots     Display statistics that helps identify code regions for
                    tracing on a HW simulator.
      Load balancing report with -group-by=process

..    .. code-block:: none

Valid arguments for 'group-by':
  basic-block : Basic Block
  function : Function
  function-mangled : Function
  module : Module
  module-path : Module Path
  process : Process
  thread-id : TID
  process-id : PID
  source-file : Source File
  source-line : Source Line
  source-file-path : Source File Path
  thread : Thread
  callstack : Call Stack
  cpuid : Logical Core
  address : Code Location
  function-start-address : Start Address
  source-function : Source Function
  package : Package
  source-function-stack : Source Function Stack
  core : Physical Core
  class : Class
  cacheline : Cacheline
  data-address : Data Address
  tasks-and-interrupts : Task and Interrupt
  context : Context
  vcore : VCore

Available values for '-column' option are:
  CPU Time:Self
  CPU Time:Effective Time:Self
  CPU Time:Effective Time:Idle:Self
  CPU Time:Effective Time:Poor:Self
  CPU Time:Effective Time:Ok:Self
  CPU Time:Effective Time:Ideal:Self
  CPU Time:Effective Time:Over:Self
  CPU Time:Spin Time:Self
  CPU Time:Spin Time:MPI Busy Wait Time:Self
  CPU Time:Spin Time:Other:Self
  CPU Time:Overhead Time:Self
  CPU Time:Overhead Time:Other:Self

[----------] waiting for spawned checks to finish
[       OK ] sphexa_vtune_sqpatch_024mpi_001omp_100n_1steps on dom:gpu using PrgEnv-intel
[       OK ] sphexa_vtune_sqpatch_048mpi_001omp_125n_1steps on dom:gpu using PrgEnv-intel
[       OK ] sphexa_vtune_sqpatch_096mpi_001omp_157n_1steps on dom:gpu using PrgEnv-intel
[----------] all spawned checks have finished

[  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))
[==========] Finished on Thu Mar 12 10:57:58 2020
==============================================================================
PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_vtune_sqpatch_024mpi_001omp_100n_1steps
- dom:gpu
   - PrgEnv-intel
      * num_tasks: 24
      * Elapsed: 4.5728 s
      * _Elapsed: 22 s
      * domain_distribute: 0.1656 s
      * mpi_synchronizeHalos: 0.2716 s
      * BuildTree: 0 s
      * FindNeighbors: 0.8124 s
      * Density: 0.5593 s
      * EquationOfState: 0.0009 s
      * IAD: 1.0046 s
      * MomentumEnergyIAD: 1.5271 s
      * Timestep: 0.1028 s
      * UpdateQuantities: 0.0098 s
      * EnergyConservation: 0.0014 s
      * SmoothingLength: 0.0021 s
      * %MomentumEnergyIAD: 33.4 %
      * %Timestep: 2.25 %
      * %mpi_synchronizeHalos: 5.94 %
      * %FindNeighbors: 17.77 %
      * %IAD: 21.97 %
      * vtune_elapsed_min: 6.695 s
      * vtune_elapsed_max: 6.695 s
      * vtune_elapsed_cput: 5.0858 s
      * vtune_elapsed_cput_efft: 4.8549 s
      * vtune_elapsed_cput_spint: 0.2309 s
      * vtune_elapsed_cput_spint_mpit: 0.2187 s
      * %vtune_effective_physical_core_utilization: 85.3 %
      * %vtune_effective_logical_core_utilization: 84.6 %
      * vtune_cput_cn0: 122.06 s
      * %vtune_cput_cn0_efft: 95.5 %
      * %vtune_cput_cn0_spint: 4.5 %
------------------------------------------------------------------------------
sphexa_vtune_sqpatch_048mpi_001omp_125n_1steps
   - PrgEnv-intel
      * num_tasks: 48
      * Elapsed: 5.0867 s
      * _Elapsed: 30 s
      * domain_distribute: 0.1936 s
      * mpi_synchronizeHalos: 0.5284 s
      * BuildTree: 0 s
      * FindNeighbors: 0.7833 s
      * Density: 0.5815 s
      * EquationOfState: 0.001 s
      * IAD: 1.0091 s
      * MomentumEnergyIAD: 1.5565 s
      * Timestep: 0.2773 s
      * UpdateQuantities: 0.0098 s
      * EnergyConservation: 0.0019 s
      * SmoothingLength: 0.0021 s
      * %MomentumEnergyIAD: 30.6 %
      * %Timestep: 5.45 %
      * %mpi_synchronizeHalos: 10.39 %
      * %FindNeighbors: 15.4 %
      * %IAD: 19.84 %
      * vtune_elapsed_min: 7.093 s
      * vtune_elapsed_max: 7.94 s
      * vtune_elapsed_cput: 6.6291 s
      * vtune_elapsed_cput_efft: 6.3795 s
      * vtune_elapsed_cput_spint: 0.3266 s
      * vtune_elapsed_cput_spint_mpit: 0.3204 s
      * %vtune_effective_physical_core_utilization: 92.0 %
      * %vtune_effective_logical_core_utilization: 90.9 %
      * vtune_cput_cn0: 141.61 s
      * %vtune_cput_cn0_efft: 94.5 %
      * %vtune_cput_cn0_spint: 5.5 %
      * vtune_cput_cn1: 159.1 s
      * %vtune_cput_cn1_efft: 96.2 %
      * %vtune_cput_cn1_spint: 3.8 %
------------------------------------------------------------------------------
sphexa_vtune_sqpatch_096mpi_001omp_157n_1steps
   - PrgEnv-intel
      * num_tasks: 96
      * Elapsed: 5.0388 s
      * _Elapsed: 37 s
      * domain_distribute: 0.207 s
      * mpi_synchronizeHalos: 0.5091 s
      * BuildTree: 0 s
      * FindNeighbors: 0.8136 s
      * Density: 0.5672 s
      * EquationOfState: 0.001 s
      * IAD: 0.9999 s
      * MomentumEnergyIAD: 1.5887 s
      * Timestep: 0.1516 s
      * UpdateQuantities: 0.0087 s
      * EnergyConservation: 0.0028 s
      * SmoothingLength: 0.002 s
      * %MomentumEnergyIAD: 31.53 %
      * %Timestep: 3.01 %
      * %mpi_synchronizeHalos: 10.1 %
      * %FindNeighbors: 16.15 %
      * %IAD: 19.84 %
      * vtune_elapsed_min: 7.408 s
      * vtune_elapsed_max: 9.841 s
      * vtune_elapsed_cput: 8.1791 s
      * vtune_elapsed_cput_efft: 7.985 s
      * vtune_elapsed_cput_spint: 0.3246 s
      * vtune_elapsed_cput_spint_mpit: 0.3191 s
      * %vtune_effective_physical_core_utilization: 87.8 %
      * %vtune_effective_logical_core_utilization: 86.6 %
      * vtune_cput_cn0: 196.3 s
      * %vtune_cput_cn0_efft: 96.0 %
      * %vtune_cput_cn0_spint: 4.0 %
      * vtune_cput_cn1: 195.71 s
      * %vtune_cput_cn1_efft: 97.9 %
      * %vtune_cput_cn1_spint: 2.1 %
      * vtune_cput_cn2: 189.77 s
      * %vtune_cput_cn2_efft: 98.1 %
      * %vtune_cput_cn2_spint: 1.9 %
      * vtune_cput_cn3: 148.46 s
      * %vtune_cput_cn3_efft: 97.6 %
      * %vtune_cput_cn3_spint: 2.4 %

