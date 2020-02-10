PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_scalascaS+T_sqpatch_024mpi_001omp_100n_4steps_5000000cycles
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 20.5242 s
      * _Elapsed: 28 s
      * domain_distribute: 0.4712 s
      * mpi_synchronizeHalos: 2.4623 s
      * BuildTree: 0 s
      * FindNeighbors: 1.8752 s
      * Density: 1.8066 s
      * EquationOfState: 0.0174 s
      * IAD: 3.7259 s
      * MomentumEnergyIAD: 6.1355 s
      * Timestep: 3.572 s
      * UpdateQuantities: 0.0273 s
      * EnergyConservation: 0.0079 s
      * SmoothingLength: 0.017 s
      * %MomentumEnergyIAD: 29.89 %
      * %Timestep: 17.4 %
      * %mpi_synchronizeHalos: 12.0 %
      * %FindNeighbors: 9.14 %
      * %IAD: 18.15 %
      * mpi_latesender: 2090 count
      * mpi_latesender_wo: 19 count
      * mpi_latereceiver: 336 count
      * mpi_wait_nxn: 1977 count
      * max_ipc_rk0: 1.294516 ins/cyc
      * max_rumaxrss_rk0: 127932 kilobytes

> sphexa_scalascaS+T_sqpatch_024mpi_001omp_100n_4steps_5000000cycles/scorep_sqpatch_24_trace/trace.stat

PatternName               Count      Mean    Median      Minimum      Maximum      Sum     Variance    Quartil25    Quartil75
mpi_latesender                  2087 0.0231947 0.0024630 0.0000001623 0.2150408312 48.4074203231 0.0029201162 0.0007851545 0.0067652356
- cnode 126 enter: 5.6760874812 exit: 5.8911956069 duration: 0.2150408312 rank: 1
- cnode 214 enter: 13.1130577932 exit: 13.1222300611 duration: 0.0090998069 rank: 4

mpi_latesender_wo                 15 0.0073685 0.0057757 0.0011093750 0.0301200084 0.1105282126 0.0000531833 0.0025275522 0.0104651418
- cnode 126 enter: 1.9057012610 exit: 1.9137143761 duration: 0.0301200084 rank: 19

mpi_latereceiver                 327 0.0047614 0.0000339 0.0000362101 0.0139404002 1.5569782562 0.0000071413 0.0000338690 0.0000338690
- cnode 127 enter: 18.3111556757 exit: 18.2765743494 duration: 0.0139404002 rank: 5
- cnode 34 enter: 0.7930921639 exit: 0.7856820722 duration: 0.0037187669 rank: 19
- cnode 216 enter: 17.3076404451 exit: 17.3069618898 duration: 0.0000507720 rank: 18

mpi_wait_nxn                    1978 0.0324812 0.0002649 0.0000000015 0.7569314451 64.2478221177 0.0164967346 0.0001135482 0.0004163433
- cnode 178 enter: 12.3218564561 exit: 13.0788456301 duration: 12.8871397782 rank: 11
- cnode 26 enter: 0.8414042015 exit: 0.9143717324 duration: 1.0955616203 rank: 3
- cnode 67 enter: 0.9517634149 exit: 0.9699780405 duration: 0.2699331878 rank: 7
- cnode 8 enter: 0.6460198397 exit: 0.6670789483 duration: 0.2042088494 rank: 13
- cnode 83 enter: 8.8629042512 exit: 8.8688473081 duration: 0.0884655322 rank: 16

mpi_nxn_completion              1978 0.0000040 0.0001135 0.0000000008 0.0000607473 0.0078960137 0.0000000001 0.0000378494 0.0001892469
- cnode 26 enter: 0.7115359880 exit: 0.7165400164 duration: 0.0007932730 rank: 20
- cnode 83 enter: 0.9749535833 exit: 0.9803317518 duration: 0.0007682808 rank: 7
- cnode 8 enter: 0.6672693320 exit: 0.6673159309 duration: 0.0001230580 rank: 22
- cnode 67 enter: 13.0904414454 exit: 13.0910728391 duration: 0.0000874705 rank: 15
- cnode 178 enter: 4.0130686059 exit: 4.6360335855 duration: 0.0000609792 rank: 6
