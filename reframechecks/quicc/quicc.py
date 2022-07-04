# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class run_quicc(rfm.RunOnlyRegressionTest):
    dims = parameter(['63;127;127'])
    sourcesdir = '/scratch/snx3000tds/piccinal/DEL/quicc/src'
    use_tool = variable(str, value='notool')  # scorep+p,perftools,extrae,mpip
    mypath = variable(str,
                      value='build/Models/BoussinesqSphereDynamo/Executables')
    cfg = variable(str, value='parameters.cfg')
    rpt = variable(str, value='OUT_stdout')
    target_executable = variable(str,
                                 value='BoussinesqSphereDynamoExplicitModel')
    csv_rpt = variable(str, value='rpt.csv')
    compute_nodes = parameter([1])
    gpus_per_cn = parameter([1])
    steps = parameter([2])
    valid_systems = ['hohgant:mc', 'manali:mc', 'dom:gpu', 'dom:mc']
    valid_prog_environs = ['PrgEnv-cray', 'builtin', 'PrgEnv-gnu']
    # only PrgEnv-cray supports affinity correctly
    use_multithreading = False
    strict_check = False

    #{{{ run
    @run_before('run')
    def set_prgenv(self):
        self.modules = [
            'cray-fftw', 'cray-hdf5-parallel', 'cray-python', 'cray-tpsl',
            'Boost'
        ]

    @run_before('run')
    def set_prgenv_tool(self):
        if self.use_tool == 'perftools':
            self.modules += ['perftools-base', 'perftools-preload']
            self.tool = 'pat_run'
        elif self.use_tool == 'extrae':
            self.modules += ['Extrae/3.8.3-CrayGNU-21.09']
        elif self.use_tool == 'scorep+p':
            self.modules += ['Score-P/7.1-CrayGNU-21.09']
        elif self.use_tool == 'mpip':
            self.modules += ['mpiP/c22011b-CrayGNU-21.09']

    @run_before('run')
    def set_runtime(self):
        self.num_tasks = self.compute_nodes * 36
        self.num_tasks_per_node = 36
        self.time_limit = '10m'  # if self.cubeside_per_gpu < 600 else '30m'

    @run_before('run')
    def set_exe(self):
        if self.use_tool == 'perftools':
            self.executable = 'pat_run'
            self.executable_name = f'{self.mypath}/{self.target_executable}'
            self.executable_opts = ['-r', self.executable_name]
        else:
            self.executable = f'{self.mypath}/{self.target_executable}'

        self.omp = {
            'dom': {'omp': '12', '-c': '24'},
            'manali': {'omp': '16', '-c': '32'},
        }
        self.job.launcher.options = [
            '-n', str(self.num_tasks), '--cpu-bind=cores'
        ]
        self.prerun_cmds += [
            'module list',
            'echo SLURM_NTASKS=$SLURM_NTASKS',
            'echo SLURM_NTASKS_PER_NODE=$SLURM_NTASKS_PER_NODE',
            'echo SLURM_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK',
            'echo SLURM_DISTRIBUTION=$SLURM_DISTRIBUTION',
            'echo starttime=`date +%s`',
        ]
        self.postrun_cmds += [
            'echo stoptime=`date +%s`',
            'echo "job done"',
            'echo "SLURMD_NODENAME=$SLURMD_NODENAME"',
            'echo "SLURM_JOBID=$SLURM_JOBID"',
            # f'# dims={self.dims} ',
            # 'rm -f core*',
        ]

    @run_before('run')
    def set_cfg(self):
        nr = int(self.dims.split(";")[0])
        nl = int(self.dims.split(";")[1])
        nm = int(self.dims.split(";")[2])
        self.prerun_cmds += [
            '# --- sed ---',
            rf'sed -i "s@<cpus>[0-9]\+</cpus>@<cpus>{self.num_tasks}</cpus>@" '
            f'{self.cfg}',
            rf'sed -i "s@<dim1D>[0-9]\+</dim1D>@<dim1D>{nr}</dim1D>@" '
            f'{self.cfg}',
            rf'sed -i "s@<dim2D>[0-9]\+</dim2D>@<dim2D>{nl}</dim2D>@" '
            f'{self.cfg}',
            rf'sed -i "s@<dim3D>[0-9]\+</dim3D>@<dim3D>{nm}</dim3D>@" '
            f'{self.cfg}',
            rf'sed -i "s@<sim>-[0-9]\+</sim>@<sim>{self.steps}</sim>@" '
            f'{self.cfg}',
            #
            rf'sed -i "s@<ascii>[0-9]\+</ascii>@<ascii>0</ascii>@" {self.cfg}',
            rf'sed -i "s@<hdf5>[0-9]\+</hdf5>@<hdf5>0</hdf5>@" {self.cfg}',
            rf'sed -i "s@<enable>1</enable>@<enable>0</enable>@" {self.cfg}',
        ]
    #}}}

    #{{{ perftools
    @run_before('run')
    def set_tool_rpt(self):
        if self.use_tool == 'perftools':
            # convert report to csv for some sanity functions:
            csv_options = ('-v -O load_balance_group -s sort_by_pe=\'yes\' '
                           '-s show_data=\'csv\' -s pe=\'ALL\'')
            self.postrun_cmds += [
                # patrun_num_of_compute_nodes
                f'ls -1 {self.target_executable}+*s/xf-files/',
                # f'cp *_job.out {self.rpt}',
                f'pat_report {csv_options} %s+*s/index.ap2 &> %s' %
                (self.target_executable, self.csv_rpt)
            ]
    #}}}

    #{{{ extrae
    @run_before('run')
    def set_extrae(self):
        if self.use_tool == 'extrae':
            # Create a wrapper script to insert Extrae libs (LD_PRELOAD)
            # into the executable at runtime
            # PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_L1_DCM,PAPI_BR_INS,PAPI_BR_MSP
            # openmp:
            # "# clone of:
            #    $EBROOTEXTRAE/share/example/MPI+OMP/ld-preload/trace.sh"
            #    "export LD_PRELOAD=$EXTRAE_HOME/lib/libompitrace.so"
            multistr = (
                "#!/bin/bash\n"
                "# clone of"
                "$EBROOTEXTRAE/share/example/MPI/ld-preload/trace.sh\n"
                "export EXTRAE_HOME=$EBROOTEXTRAE\n"
                "source $EXTRAE_HOME/etc/extrae.sh\n"
                "EXTRAE_CONFIG_FILE=./extrae.xml\n"
                "export EXTRAE_CONFIG_FILE\n"
                "export LD_PRELOAD=$EXTRAE_HOME/lib/libmpitrace.so\n"
                " \"$@\""
                # f"{self.executable} \"$@\""
            )
            # run with: srun ... ./extrae.sh myexe ...
            tool_scriptname = './extrae.sh'
            papi_set1 = (
                'PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_L1_DCM,PAPI_L2_DCM,'
                'PAPI_L3_TCM,PAPI_BR_INS,PAPI_BR_MSP,RESOURCE_STALLS')
            papi_set1_bwl = (
                'PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_L1_DCM,PAPI_L3_TCM,'
                'PAPI_BR_INS,PAPI_BR_MSP')
            papi_set2 = (
                'PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_VEC_SP,PAPI_SR_INS,'
                'PAPI_LD_INS,PAPI_FP_INS')
            papi_set2_bwl = 'PAPI_TOT_INS,PAPI_TOT_CYC,PAPI_VEC_SP,PAPI_SR_INS'
            self.prerun_cmds += [
                f'# ---------------------------------------------------------',
                f'sed -e "s@{papi_set1}@{papi_set1_bwl}@" '
                f'    -e "s@{papi_set2}@{papi_set2_bwl}@" '
                '$EBROOTEXTRAE/share/example/MPI/extrae.xml > extrae.xml',
                f'echo -e \'{multistr}\' > {tool_scriptname}',
                f'chmod u+x {tool_scriptname}',
                # f'cat {tool_scriptname}',
                f'# ---------------------------------------------------------',
            ]
            self.job.launcher.options += [tool_scriptname]

            # postproc with:
            self.prepost_tool = 'papi_best_set'
            self.postproc_tool = 'stats-wrapper.sh'
            self.postrun_cmds += [
                f'# ---------------------------------------------------------',
                f'{self.postproc_tool} *.prv -comms_histo',
                f'# use {self.prepost_tool} to check PAPI hardware counters',
                f'# Download paraver from https://tools.bsc.es/downloads',
                f'# and open {self.target_executable}.prv'
                f'# https://tools.bsc.es/paraver-tutorials',
                '# reframe -c quicc.py -r -p PrgEnv-gnu '
                '# -S mypath=build/Models/BoussinesqSphereDynamo/Executables '
                '# -S use_tool=extrae',
                '# ---------------------------------------------------------',
            ]
    #}}}

    #{{{ mpip
    @run_before('run')
    def set_mpip(self):
        if self.use_tool == 'mpip':
            self.job.launcher.options += [
                '--export=LD_PRELOAD=$EBROOTMPIP/lib/libmpiP.so'
            ]
            # self.job.launcher.options += [tool_scriptname]
    #}}}

    #{{{ scorep/profiling
    @run_before('run')
    def set_scorep_profiling(self):
        if self.use_tool == 'scorep+p':
            self.variables = {
                'SCOREP_ENABLE_PROFILING': 'true',
                'SCOREP_ENABLE_TRACING': 'false',
                'SCOREP_ENABLE_UNWINDING': 'true',
                # 'SCOREP_SAMPLING_EVENTS': f'perf_cycles@{self.cycles}',
                # 'SCOREP_METRIC_RUSAGE': 'ru_maxrss',
                # 'SCOREP_TIMER': 'clock_gettime',
                # 'SCOREP_VERBOSE': 'true',
                'SCOREP_PROFILING_MAX_CALLPATH_DEPTH': '10',
                'SCOREP_TOTAL_MEMORY': '1G',
            }
            self.rpt_score = 'scorep-score.rpt'
            self.rpt_inclusive = 'cube_calltree_inclusive.rpt'
            self.rpt_exclusive = 'cube_calltree_exclusive.rpt'
            self.rpt_otf2 = 'otf2-print.rpt'
            #
            cubetree = 'cube_calltree -m time -p -t 1'
            # -m metricname -- print out values for the metric <metricname>
            # -i            -- calculate inclusive values instead of exclusive
            # -t treshold   -- print out only call path with a value larger
            #                  than <treshold>%
            # -p            -- diplay percent value
            self.postrun_cmds += [
                f'# ---------------------------------------------------------',
                'echo "--- scorep ---"',
                # working around memory crash in scorep-score:
                f'(scorep-score -r scorep-*/profile.cubex ;rm -f core*) &>'
                f' {self.rpt_score}',
                # exclusive time (+ workaround memory crash):
                f'({cubetree} scorep-*/profile.cubex ;rm -f core*) &>'
                f' {self.rpt_exclusive}',
                # inclusive time (+ workaround memory crash):
                f'({cubetree} -i scorep-*/profile.cubex ;rm -f core*) &>'
                f' {self.rpt_inclusive}',
                f'# ---------------------------------------------------------',
            ]
    #}}}

#{{{ scorep: python failures:
# Traceback (most recent call last):
#   File "build+sc/lib64/python/quicc/base/base_model.py", line 81, in
# explicit_linear
#     mat = self.explicit_block(res, eq_params, eigs, bcs, field_row,
#    field_col, restriction = restriction)
#   File "build+sc/lib64/python/quicc_solver/model/boussinesq/sphere/dynamo/
#   explicit/physical_model.py", line 248, in explicit_block
#     mat = geo.i4(res[0], l, bc, (Pm**2*Ra*T/Pr))
# ValueError: (2, 'No such file or directory')
# Python method with arguments call error!

# Traceback (most recent call last):
#   File "build+sc/lib64/python/quicc_solver/model/boussinesq/sphere/dynamo/
#   explicit/physical_model.py", line 35, in automatic_parameters
#     "cfl_torsional":0.1*E**0.5,
# ValueError: (2, 'No such file or directory')
# Python method with arguments call error!
#}}}

    #{{{ sanity
    @sanity_function
    def assert_sanity(self):
        regex1 = r'Total execution time:'
        sanity_list = [
            sn.assert_found(regex1, self.rpt),
        ]
        if self.use_tool == 'scorep+p':
            sanity_list.append(
                sn.assert_found(r'Estimated aggregate size of event trace',
                                self.rpt_score)
            )
        elif self.use_tool == 'extrae':
            sanity_list.append(
                sn.assert_found(r'Congratulations! \S+ has been generated.',
                                self.stdout)
            )
        elif self.use_tool == 'mpip':
            sanity_list.append(
                sn.assert_found(r'^mpiP: Storing mpiP output in',
                                self.stdout)
            )

        return sn.all(sanity_list)
    #}}}

    #{{{ timers
    def report_params(self, regex_str):
        if regex_str not in ('dim1D', 'dim2D', 'dim3D', 'cpus', 'Timesteps'):
            raise ValueError(f'illegal value in argument ({regex_str!r})')

        # rpt = 'OUT_stdout'
        regex = r'^\s+%s: (\d+)' % regex_str
        return sn.extractsingle(regex, self.rpt, 1, int)

    @performance_function('')
    def rpt_dim1(self):
        return self.report_params('dim1D')

    @performance_function('')
    def rpt_dim2(self):
        return self.report_params('dim2D')

    @performance_function('')
    def rpt_dim3(self):
        return self.report_params('dim3D')

    @performance_function('')
    def rpt_cpus(self):
        return self.report_params('cpus')

    @performance_function('')
    def rpt_steps(self):
        return self.report_params('Timesteps')

    def report_time(self, regex_str):
        """
        *********** Execution time information ***********
        --------------------------------------------------
           Initialisation [s]: 14.161 / 14.169 / 14.155
                PreRun [s]: 3.627 / 3.631 / 3.624
              Computation [s]: 2.575 / 2.575 / 2.575
                PostRun [s]: 3.427 / 3.427 / 3.427
        """
        if regex_str not in ('Initialisation', 'PreRun', 'Computation',
                             'PostRun'):
            raise ValueError(f'illegal value in argument ({regex_str!r})')

        # rpt = 'OUT_stdout'
        regex = r'^\s+%s \[s\]: (\S+)' % regex_str
        return sn.extractsingle(regex, self.rpt, 1, float)

    @performance_function('s')
    def rpt_t_Initialisation(self):
        return self.report_time('Initialisation')

    @performance_function('s')
    def rpt_t_PreRun(self):
        return self.report_time('PreRun')

    @performance_function('s')
    def rpt_t_Computation(self):
        return self.report_time('Computation')

    @performance_function('s')
    def rpt_t_PostRun(self):
        return self.report_time('PostRun')

    @performance_function('s')
    def rpt_elapsed_internal(self):
        """Total execution time: 260.064 / 260.070 / 260.056 seconds
                                 t / max(t) / min(t)
        """
        regex = r'^ Total execution time: (\S+) \/'
        return sn.extractsingle(regex, self.rpt, 1, float)
    #}}}

    #{{{ mpi
    @performance_function('%', perf_key='mpi')
    def rpt_mpi(self):
        """
        Number of PEs (MPI ranks):   36
        1,36.2%,734.5,MPI
        2,34.9%,707.0,MPI/pe.0
        2,35.7%,723.0,MPI/pe.1
        """
        if self.use_tool == 'pat_run':
            regex = r'\d+,(?P<pct>\S+)%,\d+\S+,MPI$'
            return sn.extractsingle(regex, self.csv_rpt, 'pct', float)
        elif self.use_tool == 'mpip':
            # As the report output file is hardcoded ( using getpid:
            # https://github.com/LLNL/mpiP/blob/master/mpiPi.c#L935 ) i.e
            # for every job the filename must be extracted from stdout:
            # BoussinesqSphereDynamoExplicitModel.36.10579.1.mpiP
            rpt_mpip = sn.extractsingle(
                r'^mpiP: Storing mpiP output in \[(?P<rpt>.*)\]',
                self.stdout, 'rpt', str)
            regex = r'^\s+\*\s+(?P<appt>\S+)\s+(?P<mpit>\S+)\s+(?P<pct>\S+)$'
            return sn.extractsingle(regex, rpt_mpip, 'pct', float)
        else:
            return -1
    #}}}

    #{{{ scorep+p
    @performance_function('MB', perf_key='scorep_trace_size')
    def rpt_scorep_p(self):
        if self.use_tool == 'scorep+p':
            regex = r'Estimated aggregate size of event trace:\s+(\d+)'
            return sn.extractsingle(regex, self.rpt_score, 1, int)
        else:
            return -1
    #}}}

#{{{ nsys:TODO
#         profiler = 'nsys'
#         self.rpt = 'rk0.rpt'
#         # NOTE: Warning: LBR backtrace method is not supported on this
#         # platform. DWARF backtrace method will be used.
#         if self.use_tool:
#             self.job.launcher.options = [
#                 profiler, 'profile', '--force-overwrite=true',
#                 '-o', '%h.%q{SLURM_NODEID}.%q{SLURM_PROCID}',
#                 '--trace=cuda,mpi,nvtx', '--mpi-impl=mpich',
#                 '--stats=true',
#                 '--cuda-memory-usage=true',
#                 '--backtrace=dwarf',
#                 '--gpu-metrics-set=ga100',
#                 '--gpu-metrics-device=all',
#                 # '--gpu-metrics-device=0,1',
#                 '--gpu-metrics-frequency=15000',
#                 #--sampling-period=3000000
#                 # '--nic-metrics=true'
#             ]
#               self.postrun_cmds += [
#                   f'{profiler} stats *.0.nsys-rep &> {self.rpt}',
#                   # f'{profiler} stats *$SLURMD_NODENAME.*.qdrep &>
#                   # {self.rpt}',
#               ]
#}}}

    #{{{ memory:TODO
#     @performance_function('%', perf_key='highmem_rss')
#     def report_highmem_rss(self):
#         #regex = r'^.*%\s+(?P<pct>\S+)%\s+\S+%\s+$'
#         regex = r'^.*\s+(?P<pct>\S+)% $'
#         if self.current_environ.name in ['PrgEnv-arm-A64FX']:
#             return sn.max(sn.extractall(regex, 'smem.rpt', 'pct', float))
#         else:
#             return 0
    #}}}
