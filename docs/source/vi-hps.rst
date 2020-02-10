============
VI-HPS tools
============

The `VI-HPS <http://www.vi-hps.org/tools/>`__ Institute (Virtual Institute for
High Productivity Supercomputing) provides tools that can assist developers of
simulation codes to address their needs in performance analysis:

  - `Score-P <http://www.score-p.org>`__ is a highly scalable instrumentation
    and measurement infrastructure for profiling, event tracing, and online
    analysis.  It supports a wide range of HPC platforms and programming
    models. Score-P provides core measurement services for a range of
    specialized analysis tools, such as Vampir, Scalasca and others.
  - `Scalasca <http://www.vi-hps.org/tools/scalasca.html>`__ supports the
    performance optimization of parallel programs with a collection of scalable
    trace-based tools for in-depth analyses of concurrent behavior. The
    analysis identifies potential performance bottlenecks - in particular those
    concerning communication and synchronization - and offers guidance in
    exploring their causes.
  - `Vampir <http://www.vi-hps.org/tools/vampir.html>`__ is a performance
    visualizer that allows to quickly study the program runtime behavior at a
    fine level of details. This includes the display of detailed performance
    event recordings over time in timelines and aggregated profiles.
    Interactive navigation and zooming are the key features of the tool, which
    help to quickly identify inefficient or faulty parts of a program.

For further information, please check: 
 - `Training material <https://www.vi-hps.org/training/>`__

.. include:: scorep_profiling.rst
.. include:: scorep_tracing.rst
.. include:: scalasca_profiling.rst
.. include:: scalasca_tracing.rst
