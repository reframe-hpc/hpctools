# ----------------------------------------------------------------------------
> scalasca -h
Scalasca 2.5
Toolset for scalable performance analysis of large-scale parallel applications
usage: scalasca [OPTION]... ACTION <argument>...
    1. prepare application objects and executable for measurement:
       scalasca -instrument <compile-or-link-command> # skin (using scorep)
    2. run application under control of measurement system:
       scalasca -analyze <application-launch-command> # scan
    3. interactively explore measurement analysis report:
       scalasca -examine <experiment-archive|report>  # square

> scan -h
Scalasca 2.5: measurement collection & analysis nexus
usage: scan {options} [launchcmd [launchargs]] target [targetargs]
      where {options} may include:
  -h    Help      : show this brief usage message and exit.
  -v    Verbose   : increase verbosity.
  -n    Preview   : show command(s) to be launched but don't execute.
  -q    Quiescent : execution with neither summarization nor tracing.
  -s    Summary   : enable runtime summarization. [Default]
  -t    Tracing   : enable trace collection and analysis.
  -a    Analyze   : skip measurement to (re-)analyze an existing trace.
  -e exptdir      : Experiment archive to generate and/or analyze.
                    (overrides default experiment archive title)
  -f filtfile     : File specifying measurement filter.
  -l lockfile     : File that blocks start of measurement.
  -R #runs        : Specify the number of measurement runs per config.
  -M cfgfile      : Specify a config file for a multi-run measurement.

> square -h
Scalasca 2.5: analysis report explorer
usage: square [OPTIONS] <experiment archive | cube file>
   -c <none | quick | full> : Level of sanity checks for newly created reports
   -F                       : Force remapping of already existing reports
   -f filtfile              : Use specified filter file when doing scoring (-s)
   -s                       : Skip display and output textual score report
   -v                       : Enable verbose mode
   -n                       : Do not include idle thread metric
   -S <mean | merge>        : Aggregation method for summarization results of
                              each configuration (default: merge)
   -T <mean | merge>        : Aggregation method for trace analysis results of
                              each configuration (default: merge)
   -A                       : Post-process every step of a multi-run experiment

> cube_calltree -h
usage: cube_calltree -a -m metricname -t threashold -c -i -u -h [-f] filename

-m metricname -- print out values for the metric <metricname>;
-a            -- annotate call path;
-t threshold  -- print out only call path with a value, which is larger
                 than <threshold>% of the total metric value.
                 0<=treashold<=100;
-i            -- calculate inclusive values instead of exclusive.
-f            -- open <filename>;
-p            -- diplay percent value;
-c            -- diplay callpath for every region;
-h            -- display this help.

# ----------------------------------------------------------------------------

[----------] started processing sphexa_scalascaS+P_sqpatch_024mpi_001omp_100n_4steps_5000000cycles (Tool validation)
[ RUN      ] sphexa_scalascaS+P_sqpatch_024mpi_001omp_100n_4steps_5000000cycles on dom:gpu using PrgEnv-gnu
[----------] finished processing sphexa_scalascaS+P_sqpatch_024mpi_001omp_100n_4steps_5000000cycles (Tool validation)

[----------] waiting for spawned checks to finish
[       OK ] sphexa_scalascaS+P_sqpatch_024mpi_001omp_100n_4steps_5000000cycles on dom:gpu using PrgEnv-gnu
[----------] all spawned checks have finished

[  PASSED  ] Ran 1 test case(s) from 1 check(s) (0 failure(s))
[==========] Finished on Sun Feb  9 16:35:27 2020
==============================================================================

PERFORMANCE REPORT
------------------------------------------------------------------------------
sphexa_scalascaS+P_sqpatch_024mpi_001omp_100n_4steps_5000000cycles
- dom:gpu
   - PrgEnv-gnu
      * num_tasks: 24
      * Elapsed: 20.4549 s
      * _Elapsed: 38 s
      * domain_distribute: 0.4089 s
      * mpi_synchronizeHalos: 2.4644 s
      * BuildTree: 0 s
      * FindNeighbors: 1.8787 s
      * Density: 1.8009 s
      * EquationOfState: 0.0174 s
      * IAD: 3.726 s
      * MomentumEnergyIAD: 6.1141 s
      * Timestep: 3.5887 s
      * UpdateQuantities: 0.0424 s
      * EnergyConservation: 0.0177 s
      * SmoothingLength: 0.017 s
      * %MomentumEnergyIAD: 29.89 %
      * %Timestep: 17.54 %
      * %mpi_synchronizeHalos: 12.05 %
      * %FindNeighbors: 9.18 %
      * %IAD: 18.22 %
      * scorep_elapsed: 21.4262 s
      * %scorep_USR: 71.0 %
      * %scorep_MPI: 23.3 %
      * scorep_top1: 30.1 % (void sphexa::sph::computeMomentumAndEnergyIADImpl)
      * %scorep_Energy_exclusive: 30.112 %
      * %scorep_Energy_inclusive: 30.112 %
