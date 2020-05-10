MPI VERSION    : CRAY MPICH version 7.7.10 (ANL base 3.2)
...
Rank 1633 [Tue May  5 19:30:24 2020] [c9-2c0s1n2] application called MPI_Abort(MPI_COMM_WORLD, 7) - process 1633
Rank 1721 [Tue May  5 19:30:24 2020] [c9-2c0s3n1] application called MPI_Abort(MPI_COMM_WORLD, 7) - process 1721
...
Rank 757 [Tue May  5 19:30:24 2020] [c7-1c0s4n1] application called MPI_Abort(MPI_COMM_WORLD, 7) - process 757
Application 22398835 is crashing. ATP analysis proceeding...

ATP Stack walkback for Rank 1743 starting:
  _start@start.S:120
  __libc_start_main@0x2aaaac3ddf89
  main@sqpatch.cpp:85
  MPI::Comm::Abort(int) const@mpicxx.h:1236
  PMPI_Abort@0x2aaaab1f15e5
  MPID_Abort@0x2aaaab2e4267
  __GI_abort@0x2aaaac3f4740
  __GI_raise@0x2aaaac3f3160
ATP Stack walkback for Rank 1743 done
Process died with signal 6: 'Aborted'
Forcing core dumps of ranks 1743, 0
View application merged backtrace tree with: stat-view atpMergedBT.dot
You may need to: module load stat

srun: error: nid04079: tasks 1344-1355: Killed
srun: Terminating job step 22398835.0
srun: error: nid03274: tasks 672-683: Killed
srun: error: nid04080: tasks 1356-1367: Killed
...
srun: error: nid03236: tasks 216-227: Killed
srun: error: nid05581: tasks 1716-1727: Killed
srun: error: nid05583: task 1743: Aborted (core dumped)
srun: Force Terminated job step 22398835.0
