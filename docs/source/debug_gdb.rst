GNU GDB
=======

`GDB <http://www.gnu.org/savannah-checkouts/gnu/gdb/index.html>`__ is the
fundamental building block upon which other debuggers are being assembled.
GDB allows to see what is going on inside another program while it executes
— or what another program was doing at the moment it crashed (core files).

Running the test
----------------

The test can be run from the command-line:

.. code-block:: bash

 module load reframe
 cd hpctools.git/reframechecks/debug/

 ~/reframe.git/reframe.py \
 -C ~/reframe.git/config/cscs.py \
 --system daint:gpu \
 --prefix=$SCRATCH -r \
 -p PrgEnv-gnu \
 --keep-stage-files \
 -c ./gdb.py

A successful ReFrame output will look like the following:

.. code-block:: bash

 Reframe version: 3.0-dev6 (rev: e0f8d969)
 Launched on host: daint101

 [-----] started processing sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps (Tool validation)
 [ RUN ] sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps on dom:gpu using PrgEnv-cray
 [ RUN ] sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps on dom:gpu using PrgEnv-gnu
 [ RUN ] sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps on dom:gpu using PrgEnv-intel
 [ RUN ] sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps on dom:gpu using PrgEnv-pgi
 [-----] finished processing sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps (Tool validation)

 [  PASSED  ] Ran 4 test case(s) from 1 check(s) (0 failure(s))

Looking into the :class:`Class <reframechecks.debug.gdb.SphExaGDBCheck>` shows
how to setup and run the code with the tool. In this example, the code is
serial.

Bug reporting
-------------

Running gdb in non interactive mode (batch mode) is possible with a input file
that specify the commands to execute at runtime:

.. literalinclude:: ../../reframechecks/debug/src/GDB/gdb.input

An overview of the debugging data will typically look like this:

.. literalinclude:: ../../reframechecks/debug/res/gdb/rfm_sphexa_gdb_sqpatch_001mpi_001omp_15n_0steps_job.out
  :lines: 8-17, 36-38
