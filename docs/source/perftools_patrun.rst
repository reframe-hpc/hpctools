pat_run
=======

Running the test
----------------

The test can be run from the command-line:

.. code-block:: bash

 module load reframe
 cd hpctools.git/reframechecks/perftools/

 ~/reframe.git/reframe.py \
 -C ~/reframe.git/config/cscs.py \
 --system daint:gpu \
 --prefix=$SCRATCH -r \
 -p PrgEnv-gnu \
 --performance-report \
 --keep-stage-files \
 -c ./patrun.py

A successful ReFrame output will look like the following:

.. code-block:: bash

 Reframe version: 3.0-dev2 (rev: 6d543136)
 Launched on host: daint101

 [----------] waiting for spawned checks to finish
 [       OK ] sphexa_patrun_sqpatch_024mpi_001omp_100n_4steps on daint:gpu using PrgEnv-gnu
 [       OK ] sphexa_patrun_sqpatch_048mpi_001omp_125n_4steps on daint:gpu using PrgEnv-gnu
 [       OK ] sphexa_patrun_sqpatch_096mpi_001omp_157n_4steps on daint:gpu using PrgEnv-gnu
 [----------] all spawned checks have finished

 [  PASSED  ] Ran 3 test case(s) from 3 check(s) (0 failure(s))

Looking into the :class:`Class
<reframechecks.perftools.patrun.SphExaPatRunCheck>` shows how to setup and run
the code with the tool. Notice that this class is a derived class hence
``super().__init__()`` is required.

The performance report is generated automatically at the end of the job.

Performance reporting
---------------------

An overview of the performance data for a job with 96 mpi ranks will typically
look like this:

.. literalinclude:: ../../reframechecks/perftools/res/sphexa_patrun_sqpatch_096mpi_001omp_157n_4steps/sqpatch.exe+2773-4s/rpt-files/RUNTIME.rpt
  :lines: 461-472, 31-57, 409-416

As a result, a typical output from the ``--performance-report`` flag will look
like this:

.. literalinclude:: ../../reframechecks/perftools/patrun.res
  :lines: 141-169
  :emphasize-lines: 12, 22-24

This report is generated from the performance data collected from the tool and processed in
the :meth:`patrun_walltime_and_memory <reframechecks.common.sphexa.sanity_perftools.PerftoolsBaseTest.patrun_walltime_and_memory>`
and :meth:`set_tool_perf_patterns <reframechecks.common.sphexa.sanity_perftools.PerftoolsBaseTest.set_tool_perf_patterns>`
methods of the :class:`SphExaPatRunCheck <reframechecks.common.sphexa.sanity_perftools.PerftoolsBaseTest>` class.

.. include:: perftools_patrun_img.rst

