Tracing
=======

Running the test
----------------

The test can be run from the command-line:

.. code-block:: bash

 module load reframe
 cd hpctools.git/reframechecks/scorep/

 ~/reframe.git/reframe.py \
 -C ~/reframe.git/config/cscs.py \
 --system daint:gpu \
 --prefix=$SCRATCH -r \
 -p PrgEnv-gnu \
 --performance-report \
 --keep-stage-files \
 -c ./scorep_sampling_tracing.py

A successful ReFrame output will look like the following:

.. code-block:: bash

 Reframe version: 2.22
 Launched on host: daint101
 
 [----------] started processing sphexa_scorepS+T_sqpatch_024mpi_001omp_100n_10steps_1000000cycles (Tool validation)
 [ RUN      ] sphexa_scorepS+T_sqpatch_024mpi_001omp_100n_10steps_1000000cycles on daint:gpu using PrgEnv-gnu
 [       OK ] sphexa_scorepS+T_sqpatch_024mpi_001omp_100n_10steps_1000000cycles on daint:gpu using PrgEnv-gnu
 [----------] finished processing sphexa_scorepS+T_sqpatch_024mpi_001omp_100n_10steps_1000000cycles (Tool validation)
 
 [  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))

Looking into the :class:`Class
<reframechecks.scorep.scorep_sampling_tracing>` shows how to setup and run
the code with the tool. 

.. .. literalinclude:: ../../reframechecks/scorep/scorep_sampling_tracing.py
  :language: python
  :lines: 10-15
  :emphasize-lines: 1

Set ``self.build_system.cxx`` to instrument the code and set the SCOREP runtime
variables with ``self.variables`` to trigger the (sampling based) `tracing`
analysis.

Performance reporting
---------------------

A typical output from the ``--performance-report`` flag will look like this:

.. literalinclude:: ../../reframechecks/scorep/res/scorep_sampling_tracing.res
  :lines: 1-27
  :emphasize-lines: 26-27

This report is generated from the data collected from the tool and processed in
the ``self.perf_patterns`` part of the :class:`Class <reframechecks.scorep.scorep_sampling_tracing>`.
For example, the information about the ``ipc`` for rank 0 is extracted with the
:meth:`ipc_rk0 <reframechecks.common.sphexa.sanity_scorep.ipc_rk0>` method.
Looking at the report with the tool gives more insight into the performance of
the code:

.. (:ref:`Fig.1 <link_to_myfig1>`) shows that...
.. .. _link_to_myfig1:

.. figure:: img/scorep/vampir_01.png
   :align: center
   :alt: Vampir screenshot 01

   Score-P Vampir (launched with: vampir scorep-/traces.otf2)

.. figure:: img/scorep/vampir_02.png
   :align: center
   :alt: Vampir screenshot 02

   Score-P Vampir  (communication matrix)

