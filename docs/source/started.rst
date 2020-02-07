===============
Getting started
===============

.. the ReFrame regression tests used in production on the Cray systems, in
  particular with respect to the debugging and performance tools used at CSCS,

Usage of performance tools to identify and remove bottlenecks is part of most
modern performance engineering workflows. `ReFrame
<https://github.com/eth-cscs/reframe>`__ is a regression testing
framework for HPC systems that allows to write portable regression tests,
focusing only on functionality and performance. It has been used in production
at CSCS since 2016 and is being actively developed. All the tests used in this
guide are freely available `here
<https://github.com/eth-cscs/hpctools/tree/master/reframechecks>`__.

This page will guide you through writing ReFrame tests to analyze the
performance of your code. You should be familiar with ReFrame, this link to the
ReFrame `tutorial
<https://reframe-hpc.readthedocs.io/en/stable/tutorial.html>`__ can serve as a
starting point. As a reference test code, we will use the `SPH-EXA
<https://github.com/unibas-dmi-hpc/SPH-EXA_mini-app>`__ mini-app. This code is
based on the smoothed particle hydrodynamics (SPH) method, which is a
particle-based, meshfree, Lagrangian method for simulating multidimensional
fluids with arbitrary geometries, commonly employed in astrophysics, cosmology,
and computational fluid-dynamics. The mini-app is a C++14, lightweight,
flexible, and header-only code with no external software dependencies.
Parallelism is expressed via multiple programming models such as OpenMP and HPX
for node level parallelism, MPI for internode communication and Cuda, OpenACC
and OpenMP targets for accelerators. Our reference HPC system is `Piz Daint
<http://www.cscs.ch/computers/piz_daint/>`__.

.. ---------------------------------------------------------------------------- ko
 # https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#embedded-uris-and-aliases
 This page will guide you through writing a `_ReFrame`_ test to analyze the
 parallel performance of your code. You should be familiar with ReFrame, this
 `_ReFrame tutorial`_ can serve as a starting point.

 .. _ReFrame: https://github.com/eth-cscs/reframe
 .. _ReFrame tutorial: https://reframe-hpc.readthedocs.io/en/stable/tutorial.html

 .. literalinclude:: /conf.py
   :dedent: 4
   :language: python
   :lines: 4-6
   :linenos:
   :emphasize-lines: 1,2
   ----------------------------------------------------------------------------

The most simple case of a ReFrame test is a test that compiles, runs and
checks the output of the job. Looking into the :class:`Class
<reframechecks.notool.internal_timers_mpi>` shows how to setup and run the code
with the tool. In this example, we set the 3 parameters as follows: 24 mpi
tasks, a cube size of :math:`{100}^3` particles in the 3D square patch test and
only 1 step of simulation.

.. .. literalinclude:: ../../reframechecks/notool/internal_timers_mpi.py
  :language: python
  :lines: 9-39
  :emphasize-lines: 1

Running the test
================

The test can be run from the command-line:

.. code-block:: bash

    module load reframe
    cd hpctools.git/reframechecks/notool/

    ~/reframe.git/reframe.py \
    -C ~/reframe.git/config/cscs.py \
    --system daint:gpu \
    --prefix=$SCRATCH -r \
    --keep-stage-files \
    -c ./internal_timers_mpi.py

where:
    * ``-C`` points to the site config-file, 
    * ``--system`` selects the targeted system,
    * ``--prefix`` sets output directory,
    * ``-r`` runs the selected check,
    * ``-c`` points to the check.

.. --keep-stage-files 

A typical output from ReFrame will look like this:

.. code-block:: bash

 Reframe version: 2.22
 Launched on host: daint101
 Reframe paths
 =============
     Check prefix      :
     Check search path : 'internal_timers_mpi.py'
     Stage dir prefix     : /scratch/snx3000tds/piccinal/stage/
     Output dir prefix    : /scratch/snx3000tds/piccinal/output/
     Perf. logging prefix : /scratch/snx3000tds/piccinal/perflogs
 [==========] Running 1 check(s)
 
 [----------] started processing sphexa_timers_sqpatch_024mpi_001omp_100n_0steps (Strong scaling study)
 [ RUN      ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-cray
 [       OK ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-cray
 [ RUN      ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-cray_classic
 [       OK ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-cray_classic
 [ RUN      ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-gnu
 [       OK ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-gnu
 [ RUN      ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-intel
 [       OK ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-intel
 [ RUN      ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-pgi
 [       OK ] sphexa_timers_sqpatch_024mpi_001omp_100n_0steps on daint:gpu using PrgEnv-pgi
 [----------] finished processing sphexa_timers_sqpatch_024mpi_001omp_100n_0steps (Strong scaling study)
 
 [  PASSED  ] Ran 5 test case(s) from 1 check(s) (0 failure(s))

By default, the test is run with every programming environment set inside the
check. It is possible to select only one programming environment with the *-p*
flag (``-p PrgEnv-gnu`` for instance).

Sanity checking
===============

All of our tests passed. Sanity checking checks if a test passed or not. In
this simple example, we check that the job output reached the end of the first
step, this is coded in the ``self.sanity_patterns`` part of the :class:`Class
<reframechecks.notool.internal_timers_mpi>`.

.. .. literalinclude:: ../../reframechecks/notool/internal_timers_mpi.py
  :language: python
  :lines: 175-178
  :emphasize-lines: 3

Performance reporting
=====================

The mini-app calls the ``std::chrono`` library to measure and report the
elapsed time for each timestep from different parts of the code in the job
output.
ReFrame supports the extraction and manipulation of performance data from the
program output, as well as a comprehensive way of setting performance
thresholds per system and per system partitions. In addition to performance
checking, it is possible to print a performance report with the
``--performance-report`` flag. A typical report for the mini-app with
PrgEnv-gnu will look like this:

.. literalinclude:: ../../reframechecks/notool/internal_timers_mpi.res
  :lines: 25-49

This report is generated from the data collected from the job output and
processed in the ``self.perf_patterns`` part of the check. For example, the 
time spent in the ``MomentumEnergyIAD`` is extracted with the
:meth:`seconds_energ <reframechecks.common.sphexa.sanity.seconds_energ>`
method.
Similarly, the percentage of walltime spent in the ``MomentumEnergyIAD`` is
calculated with the :meth:`pctg_MomentumEnergyIAD 
<reframechecks.common.sphexa.sanity.pctg_MomentumEnergyIAD>` method.

.. .. literalinclude:: ../../reframechecks/notool/internal_timers_mpi.py
  :language: python
  :lines: 190-192, 201, 209
  :emphasize-lines: 4


.. :meth:`sanity.elapsed_time_from_date <reframechecks.common.sphexa.sanity.elapsed_time_from_date>` method
.. * The :class:`internal_timers_mpi.py <reframechecks.notool.internal_timers_mpi>` 
  will compile and run 
 * This :class:`function <reframechecks.common.sphexa.sanity.pctg_MomentumEnergyIAD>` function
 * This :class:`function <reframechecks.common.sphexa.sanity>` function
 .. reframechecks/notool/internal_timers_mpi.py  -> class SphExaNativeCheck(rfm.RegressionTest):
 .. reframechecks/common/sphexa/sanity.py        -> def elapsed_time_from_date(self):

Summary
=======

We have covered the basic aspects of a ReFrame test. The next section will
expand this test with the integration of a list of commonly used performance
tools.

