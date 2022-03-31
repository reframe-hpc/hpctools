# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


# {{{ global:
hdf5_mod = {
    "A64FX": {
        "PrgEnv-arm-A64FX": "",
        "PrgEnv-gnu-A64FX": "",
        "PrgEnv-nvidia-A64FX": "",
        # 'PrgEnv-arm-A64FX': 'hdf5/1.13.0-A64FX+ARM',
        # 'PrgEnv-gnu-A64FX': 'hdf5/1.13.0-A64FX+GNU',
        # 'PrgEnv-nvidia-A64FX': 'hdf5/1.13.0-A64FX+NVHPC',
    },
    "neoverse-n1": {
        "PrgEnv-arm-N1": "",
        "PrgEnv-gnu": "",
        "PrgEnv-nvidia": "",
        # 'PrgEnv-arm-N1': 'hdf5/1.13.0-N1+ARM',
        # 'PrgEnv-gnu': 'hdf5/1.13.0-N1+GNU',
        # 'PrgEnv-nvidia': 'hdf5/1.13.0-N1+NVHPC',
    },
    "TX2": {
        "PrgEnv-arm-TX2": "hdf5/1.13.0-TX2+ARM",
        "PrgEnv-gnu": "hdf5/1.13.0-TX2+GNU",
        "PrgEnv-nvidia": "hdf5/1.13.0-TX2+NVHPC",
    },
    "gpu": {"PrgEnv-gnu": ""},  # 'hdf5/1.13.0',
    "mc": {"PrgEnv-gnu": ""},  # 'hdf5/1.13.0',
    "a100": {"PrgEnv-gnu": ""},  # 'hdf5/1.13.0',
}
max_mpixomp = {
    "dom": {"gpu": 12, "mc": 36},
    "daint": {"gpu": 12, "mc": 36},
    "wombat": {"neoverse-n1": 40, "TX2": 64, "A64FX": 48},
    "lumi": {"gpu": 64},
    "dmi": {"a100": 112},
}
topology_mpixomp = {
    "dom": {"gpu": {"cps": 12, "s": 1}, "mc": {"cps": 18, "s": 2}},
    "lumi": {"gpu": {"cps": 64, "s": 1}},
    "wombat": {
        "neoverse-n1": {"cps": 40, "s": 1},
        "TX2": {"cps": 32, "s": 2},
        "A64FX": {"cps": 12, "s": 4},
    },
    "dmi": {"a100": {"cps": 28, "s": 2}},
}
install_dir = "../build_analytical_False_without_armpl_notool/build/JG/bin"
# }}}


# {{{ run_tests
@rfm.simple_test
class run_tests(rfm.RunOnlyRegressionTest):
    """
    x1='--module-path +/sw/wombat/ARM_Compiler/21.1/modulefiles'
    x2='--module-path +$HOME/modulefiles'
    x="$x1 $x2"
    R -c 0.py -n run_tests -r -S repeat=3 $x -S mypath='../JG/sbin/performance'
    dmi: salloc -pgpu -t 6:0:0 ; ssh cl-node027
    """
    sourcesdir = None
    use_tool = parameter(["ncu"])  # notool, nsys
    # scorep: cube_calltree -m time -i  profile.cubex -a -c / ok on juwels!
    # scorep: cube_stat
    kernel_name = parameter(["cudaDensity", "cudaGradP", "cudaIAD"])
    analytical = parameter(["analytical"])
    cubeside = parameter([200])
    steps = parameter([100])  # 800
    mypath = variable(str, value=install_dir)
    repeat = variable(int, value=1)
    compute_nodes = parameter([0])
    # compute_nodes = parameter([1])
    mpi_ranks = parameter([1])
    openmp_threads = parameter([40])
#    mpi_ranks = parameter([1, 2, 4, 7, 8, 14, 28, 56])
#    openmp_threads = parameter([1, 2, 4, 7, 8, 14, 28, 56])
#    mpi_ranks = parameter([1, 2, 4, 8, 12, 16, 32, 40, 48, 64])
#    openmp_threads = parameter([1, 2, 4, 8, 12, 16, 32, 40, 48, 64])
    # openmp_threads = parameter([1, 2, 4])
    valid_systems = ["wombat:gpu", "dom:gpu", "dom:mc"]
    valid_prog_environs = [
        "PrgEnv-arm-N1",
        "PrgEnv-arm-TX2",
        "PrgEnv-arm-A64FX",
        "PrgEnv-nvidia",
        "PrgEnv-nvidia-A64FX",
        "PrgEnv-gnu",
        "PrgEnv-gnu-A64FX",
        "PrgEnv-cray",
    ]
    time_limit = "120m"
    use_multithreading = False
    strict_check = False

    # {{{ run
    @run_before("run")
    def set_hdf5(self):
        if hdf5_mod[self.current_partition.name][self.current_environ.name]:
            self.modules = [
                hdf5_mod[self.current_partition.name][
                    self.current_environ.name]
            ]

    @run_before("run")
    def set_run(self):
        self.executable = "$HOME/affinity"
        self.prerun_cmds += [
            "module list",
            "mpicxx --version || true",
            "nvcc --version || true",
            "module rm gnu10/10.2.0 binutils/10.2.0",
        ]
        # {{{ mpi:
        self.num_tasks = self.mpi_ranks
        self.num_tasks_per_node = self.mpi_ranks
        self.num_cpus_per_task = self.openmp_threads
        # TODO:
        # procinfo = self.current_partition.processor.info
        # self.skip_if_no_procinfo()
        mpixomp = self.num_tasks_per_node * self.num_cpus_per_task
        current_max_mpixomp = max_mpixomp[self.current_system.name][
            self.current_partition.name]
        # skip if too many/too few processes:
        self.skip_if(
            # mpixomp != current_max_mpixomp / 2,
            mpixomp > current_max_mpixomp,
            f"{mpixomp} != {current_max_mpixomp} max mpi*openmp",
        )
        self.variables = {
            "OMP_NUM_THREADS": str(self.num_cpus_per_task),
            # 'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
            "OMP_PLACES": "sockets",
            "OMP_PROC_BIND": "close",
            "CUDA_VISIBLE_DEVICES": "0",
            "HIP_VISIBLE_DEVICES": "0",
        }
        mpi_type = ""
        for_loop = "for ii in `seq {self.repeat}` ;do"
        if self.current_system.name in ["wombat"]:
            mpi_type = "--mpi=pmix"
            self.job.launcher.options = [mpi_type, "numactl",
                                         "--interleave=all"]
            mysrun = f'{for_loop} srun {" ".join(self.job.launcher.options)}'
        elif self.current_system.name in ["dom"]:
            mpi_type = ""
            self.job.launcher.options = [mpi_type, "numactl",
                                         "--interleave=all"]
            mysrun = f'{for_loop} srun {" ".join(self.job.launcher.options)}'
        elif self.current_system.name in ["dmi"]:
            # MUST: salloc THEN ssh THEN rfm -r
            # '--use-hwthread-cpus'
            self.job.launcher.options = [
                f"-np {self.mpi_ranks}",
                "--hostfile $OMPI_HOSTFILE",
                f"--map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS",
                "numactl",
                "--interleave=all",
            ]
            mysrun = f'{for_loop} mpirun {" ".join(self.job.launcher.options)}'
            myexe = f"{self.mypath}/sedov-cuda"
        elif self.current_system.name in ["lumi"]:
            self.job.launcher.options = [
                f"-np {self.mpi_ranks}",
                "--hostfile $OMPI_HOSTFILE",
                f"--map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS",
                "numactl",
                "--interleave=all",
            ]
            mysrun = f'{for_loop} mpirun {" ".join(self.job.launcher.options)}'
            myexe = f"{self.mypath}/sphexa-hip --init sedov"
        else:
            self.job.launcher.options = ["numactl", "--interleave=all"]
            mysrun = (
                f'{for_loop} mpirun -np {self.mpi_ranks} '
                f'--map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS '
                f'{" ".join(self.job.launcher.options)}'
            )
            self.postrun_cmds += [
                f'mpirun -np {self.mpi_ranks} '
                f'--map-by ppr:{self.mpi_ranks}:node:pe=$OMP_NUM_THREADS '
                f'{self.executable}'
            ]
        # }}}

        # if self.current_system.name in {'daint', 'dom'}:
        #    self.job.launcher.options = ['numactl', '--interleave=all']
        # self.prerun_cmds += ['echo starttime=`date +%s`']
        if self.analytical in ["analytical"]:
            # NOTE: -n 400 means:
            # === Total time for iteration(0) 282.116s = 5min
            # Total execution time of 0 iterations of Sedov: 344.003s
            #                                                (i/o=62) = 6min
            # 6.7G dump_sedov.h5part (1 step, 7168008752/1024^3)
            # 14 variables:
            #   c,grad_P_x,grad_P_y,grad_P_z,h,p,rho,u,vx,vy,vz,x,y,z
            # 14 variables * 64e6 particles * 8 b
            # 14*64*1000000*8 = 7'168'000'000
            # cubeside = 100 # 50
            # steps = 30 # 200
            output_frequency = -1  # steps
            # r'-o %h.%q{SLURM_NODEID}.%q{SLURM_PROCID}.qdstrm '
            # r'--trace=cuda,mpi,nvtx --mpi-impl=mpich '
            # r'--delay=2')
            # {{{ nsys
            if self.use_tool in ["nsys"]:
                self.tool_opts = (
                    r"nsys profile --force-overwrite=true "
                    r"-o %h.qdstrm "
                    r"--trace=cuda,mpi,nvtx "
                    r"--stats=true "
                    # 'nsys', 'profile', '--force-overwrite=true',
                    # '-o', '%h.%q{SLURM_NODEID}.%q{SLURM_PROCID}',
                    # '--trace=cuda,mpi,nvtx', '--mpi-impl=mpich',
                    # '--stats=true',
                    # '--cuda-memory-usage=true',
                    # '--backtrace=dwarf',
                    # '--gpu-metrics-set=ga100',
                    # '--gpu-metrics-device=all',
                    # # '--gpu-metrics-device=0,1',
                    # '--gpu-metrics-frequency=15000',
                    # #--sampling-period=3000000
                    # # '--nic-metrics=true'
                )
            # }}}
            # {{{ ncu
            # {{{ roofline metrics: ~/git/jgphpc.git/hpc/roofline/readme
            roof_metrics = (
                # Time
                "sm__cycles_elapsed.avg,sm__cycles_elapsed.avg.per_second,"
                # DP
                r"sm__sass_thread_inst_executed_op_dadd_pred_on.sum,"
                r"sm__sass_thread_inst_executed_op_dfma_pred_on.sum,"
                r"sm__sass_thread_inst_executed_op_dmul_pred_on.sum,"
                # SP
                r"sm__sass_thread_inst_executed_op_fadd_pred_on.sum,"
                r"sm__sass_thread_inst_executed_op_ffma_pred_on.sum,"
                r"sm__sass_thread_inst_executed_op_fmul_pred_on.sum,"
                # HP
                r"sm__sass_thread_inst_executed_op_hadd_pred_on.sum,"
                r"sm__sass_thread_inst_executed_op_hfma_pred_on.sum,"
                r"sm__sass_thread_inst_executed_op_hmul_pred_on.sum,"
                # Tensor Core
                r"sm__inst_executed_pipe_tensor.sum,"
                # DRAM, L2 and L1
                "dram__bytes.sum,"
                "lts__t_bytes.sum,"
                "l1tex__t_bytes.sum"
            )
            occupancy_metrics = (
                '--metrics sm__throughput.avg.pct_of_peak_sustained_elapsed,'
                'gpu__compute_memory_throughput.avg.'
                'pct_of_peak_sustained_elapsed '
            )
            measurements = f'^{self.kernel_name}:"24|49|74|99"'
            # {{{ help:
            # ls -1 22.2/profilers/Nsight_Compute/sections/ |grep section
            # ComputeWorkloadAnalysis.section
            # InstructionStatistics.section
            # LaunchStatistics.section
            # MemoryWorkloadAnalysis_Chart.section
            # MemoryWorkloadAnalysis_Deprecated.section
            # MemoryWorkloadAnalysis.section
            # MemoryWorkloadAnalysis_Tables.section
            # Nvlink.section
            # Nvlink_Tables.section
            # Nvlink_Topology.section
            # Occupancy.section
            # SchedulerStatistics.section
            # SourceCounters.section
            # SpeedOfLight_HierarchicalDoubleRooflineChart.section
            # SpeedOfLight_HierarchicalHalfRooflineChart.section
            # SpeedOfLight_HierarchicalSingleRooflineChart.section
            # SpeedOfLight_HierarchicalTensorRooflineChart.section
            # SpeedOfLight_RooflineChart.section                    <---
            # SpeedOfLight.section                                  <---
            # WarpStateStatistics.section
            #
            # > ncu --list-sections
            # }}}
            # }}}
            elif self.use_tool in ["ncu"]:
                # --- Occupancy: ok
                # kernel_name = rf'--kernel-id ::regex:{measurements} '
                # metrics = occupancy_metrics

                # --- SpeedOfLight: ok
                # kernel_name = rf'--kernel-id ::regex:{measurements} '
                # metrics = '--section SpeedOfLight'

                # --- Roofline: ok
                # no need to set roof_metrics, use section instead!
                # kernel_name = rf'--kernel-id ::regex:{measurements} '
                # metrics = '--section SpeedOfLight_RooflineChart'

                # --- Source/SAAS: ok
                kernel_name = rf'--kernel-id ::regex:{measurements} '
                metrics = "--set full"
                self.tool_opts = (
                    rf"ncu {kernel_name} {metrics} "
                    r"--force-overwrite -o rpt "  # -> rpt.ncu-rep
                    # r'--launch-skip 1 --launch-count 2 '
                    # r'--section SpeedOfLight_RooflineChart '
                    # -> .../sections/SpeedOfLight_RooflineChart.section
                    # r'--import-source on '
                    # compile with -lineinfo (but not -G)
                    # r'-o %h.%q{SLURM_NODEID}.%q{SLURM_PROCID} '
                    # ok: --kernel-id ::regex:^cudaIAD:"2|6|8" = -s1,-s5,-s7
                    # or: --kernel-name "cudaIAD"
                    # --kernel-id arg:
                    # Set the identifier to use for matching the kernel to
                    # profile. The identifier is of the format
                    # "context-id:stream-id:[name-op:]kernel-name:invocationnr"
                    # Skip entries that shouldnot be matched, e.g.
                    # use "::foobar:2" to match the second invocation of
                    # "foobar" in any context or stream. Use ":7:regex:^foo:"
                    # to match any kernel in stream 7 beginning with "foo"
                    # (according to --kernel-name-base).
                )
            # }}}
            # {{{ memory
            elif self.use_tool in ["mem"]:
                self.prerun_cmds += ['$HOME/smem.sh &']
                self.postrun_cmds += [
                    "smem_pid=`ps x|grep -m1 $HOME/smem.sh |awk '{print $1}'`",
                    "kill -9 $smem_pid"
                ]
            # }}}
            else:
                self.tool_opts = ""

            self.postrun_cmds += [
                # sedov
                f"echo sedov: -s={self.steps} -n={self.cubeside}",
                "t0=`date +%s` ;"
                f"{mysrun} {self.tool_opts} {myexe} -n {self.cubeside} "
                f"-s {self.steps} -w {output_frequency};"
                "done; t1=`date +%s`",
                "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
                'echo "sedov_t=$tt"',
                'echo -e "\\n\\n"',
                # 'source ~/myvenv_gcc11_py399/bin/activate',
                # f'ln -s {self.mypath}/sedov_solution',
                # f'python3 {self.mypath}/compare_solutions.py -s {steps} "
                # "dump_sedov.h5part',
            ]
        else:
            self.postrun_cmds += [
                # octree_perf
                "echo octree_perf:",
                "t0=`date +%s` ;"
                f"{mysrun} {self.mypath}/octree_perf ;"
                "done; t1=`date +%s`",
                "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
                'echo "octree_perf_t=$tt"',
                # 'echo peers:',
                # f'{mysrun} {self.mypath}/peers_perf',
                # hilbert_perf
                "echo hilbert_perf:",
                "t0=`date +%s` ;"
                f"{mysrun} {self.mypath}/hilbert_perf ;"
                "done; t1=`date +%s`",
                "tt=`echo $t0 $t1 |awk '{print $2-$1}'`",
                'echo "hilbert_perf_t=$tt"',
            ]
        self.postrun_cmds += [
            'echo "done"',
            # 'rm -f core*',
            'echo "SLURMD_NODENAME=$SLURMD_NODENAME"',
            'echo "SLURM_JOBID=$SLURM_JOBID"',
        ]

    # }}}
    # {{{ nsys / ncu
    @run_before("run")
    def get_rpt(self):
        if self.use_tool in ["nsys"]:
            nsys = 'nsys stats -f csv *.nsys-rep --timeunit sec --report'
            self.postrun_cmds += [
                f"{nsys} nvtxsum *.nsys-rep > nvtxsum.rpt",
                f"{nsys} gpumemsizesum *.nsys-rep > gpumemsizesum.rpt",
            ]
        elif self.use_tool in ["ncu"]:
            self.postrun_cmds += [
                "#",
                # 'ncu --csv -i rpt.ncu-rep > rpt.csv',
                # roofline:
                "ncu --page raw --csv -i rpt.ncu-rep > rpt.csv",
            ]

    # }}}
    # {{{ analytical
    @run_before('run')
    def set_compare(self):
        # print(self.steps, type(self.steps))
        solution.exe =
        f'{self.mypath}/../analytical_solutions/sedov_solution/sedov_solution'
        solution.py =
        f'{self.mypath}/../../../src/analytical_solutions/compare_solutions.py'
        if self.steps == 200:
            self.executable_opts += ['-w', str(self.steps)]
            self.postrun_cmds += [
                '# analytical_solution:',
                'source ~/myvenv_matplotlib/bin/activate',
                f'ln -s {solution.exe}',
                f'ln -s {solution.py}',
                'python3 ./compare_solutions.py sedov -bf ./sedov_solution '
                '-n 125000 -sf ./dump_sedov200.txt -cf ./constants.txt -i 200 '
                '-np --error_rho --error_p --error_vel '
                # FIXME: add after we move to glass initial model
                # '--error_u --error_cs '
            ]
    # }}}

    #     @run_before('run')
    #     def set_mpirun(self):
    #         if self.current_system.name in ['dmi']:
    #             self.job.launcher.options = [
    #               '--mca btl_openib_warn_default_gid_prefix 0']

    # {{{ sanity
    @sanity_function
    def assert_sanity(self):
        if self.analytical in ["analytical"]:
            return sn.all(
                [
                    sn.assert_found(
                        r"Total execution time of \d+ iterations", self.stdout
                    ),
                ]
            )
        else:
            regex01 = r"octree_perf_t=\d+"
            regex02 = r"hilbert_perf_t=\d+"
            # regex03 = r'scan_perf_t=\d+'
            regex1 = r"compute time for \d+ hilbert keys: \S+ s on CPU"
            regex2 = r"compute time for \d+ morton keys: \S+ s on CPU"
            # regex3 = r'(serial scan|parallel scan scan) test: PASS'
            return sn.all(
                [
                    sn.assert_found(regex01, self.stdout),
                    sn.assert_found(regex1, self.stdout),
                    sn.assert_found(regex02, self.stdout),
                    sn.assert_found(regex2, self.stdout),
                    # sn.assert_found(regex03, self.stdout),
                    # sn.assert_found(regex3, self.stdout),
                ]
            )

    # }}}
    # {{{ timers
    @performance_function("cn", perf_key="compute_nodes")
    def report_cn(self):
        return self.compute_nodes

    @performance_function("mpi", perf_key="mpi_ranks")
    def report_mpi(self):
        regex = r"# (\d+) MPI-\S+ process\(es\) with \d+ OpenMP-\S+ thread"
        return sn.extractsingle(regex, self.stdout, 1, int)
        # return self.num_tasks

    @performance_function("openmp", perf_key="openmp_threads")
    def report_omp(self):
        regex = r"# \d+ MPI-\S+ process\(es\) with (\d+) OpenMP-\S+ thread"
        return sn.extractsingle(regex, self.stdout, 1, int)
        # return self.num_cpus_per_task

    # 1 MPI-3.1 process(es) with 112 OpenMP-201511 thread(s)/process
    @performance_function("", perf_key="repeat")
    def report_repeat(self):
        return self.repeat

    @performance_function("", perf_key="-n")
    def report_L1_n(self):
        regex = r"sedov: -s=\d+ -n=(\d+)"
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function("steps", perf_key="-s")
    def report_L1_s(self):
        regex = r"sedov: -s=(\d+) -n="
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function("s", perf_key="elapsed_internal")
    def report_elapsed_internal(self):
        # Total execution time of 0 iterations of Sedov: 0.373891s
        regex = r"Total execution time of \d+ iterations of \S+: (?P<s>\S+)s$"
        sec = sn.extractsingle(regex, self.stdout, "s", float)
        return sn.round(sec, 1)

    # {{{ report_regions
    def report_region(self, index):
        # domain::sync: 0.109453s
        # FindNeighbors: 0.781538s
        # Density: 0.13732s
        # EquationOfState: 0.000330948s
        # mpi::synchronizeHalos: 0.00315571s
        # IAD: 0.230027s
        # mpi::synchronizeHalos: 0.0174127s
        # MomentumEnergyIAD: 0.560612s
        # Timestep: 0.0533516s
        # UpdateQuantities: 0.0130277s
        # EnergyConservation: 0.00435739s
        # UpdateSmoothingLength: 0.00656605s
        regex = {
            1: r"^# domain::sync:\s+(?P<sec>.*)s",
            2: r"^# updateTasks:\s+(?P<sec>.*)s",
            3: r"^# FindNeighbors:\s+(?P<sec>.*)s",
            4: r"^# Density:\s+(?P<sec>.*)s",
            5: r"^# EquationOfState:\s+(?P<sec>.*)s",
            6: r"^# mpi::synchronizeHalos:\s+(?P<sec>.*)s",
            7: r"^# IAD:\s+(?P<sec>.*)s",
            8: r"^# MomentumEnergyIAD:\s+(?P<sec>.*)s",
            9: r"^# Timestep:\s+(?P<sec>.*)s",
            10: r"^# UpdateQuantities:\s+(?P<sec>.*)s",
            11: r"^# EnergyConservation:\s+(?P<sec>.*)s",
            12: r"^# UpdateSmoothingLength:\s+(?P<sec>.*)s",
        }
        return sn.round(
            sn.sum(sn.extractall(regex[index], self.stdout, "sec", float)), 4
        )

    @performance_function("s")
    def t_domain_sync(self):
        return self.report_region(1)

    @performance_function("s")
    def t_updateTasks(self):
        return self.report_region(2)

    @performance_function("s")
    def t_FindNeighbors(self):
        return self.report_region(3)

    @performance_function("s")
    def t_Density(self):
        return self.report_region(4)

    @performance_function("s")
    def t_EquationOfState(self):
        return self.report_region(5)

    @performance_function("s")
    def t_mpi_synchronizeHalos(self):
        return self.report_region(6)

    @performance_function("s")
    def t_IAD(self):
        return self.report_region(7)

    @performance_function("s")
    def t_MomentumEnergyIAD(self):
        return self.report_region(8)

    @performance_function("s")
    def t_Timestep(self):
        return self.report_region(9)

    @performance_function("s")
    def t_UpdateQuantities(self):
        return self.report_region(10)

    @performance_function("s")
    def t_EnergyConservation(self):
        return self.report_region(11)

    @performance_function("s")
    def t_UpdateSmoothingLength(self):
        return self.report_region(12)
    # }}}

    # # {{{ hilbert_perf (hilbert, morton)
    # # compute time for 32000000 hilbert keys: 13.2216 s on CPU
    # # compute time for 32000000 morton keys: 0.11014 s on CPU
    # @performance_function('', perf_key='hilbert_perf_keys')
    # def report_keys(self):
    #     regex = r'compute time for (\d+) hilbert keys: \S+ s on CPU'
    #     return sn.extractsingle(regex, self.stdout, 1, int)
    #
    # @performance_function('s', perf_key='hilbert_perf_hilbert')
    # def report_cput_hilbert(self):
    #     regex = r'compute time for \d+ hilbert keys: (\S+) s on CPU'
    #     return sn.round(sn.avg(
    #         sn.extractall(regex, self.stdout, 1, float)), 5)
    #
    # @performance_function('s', perf_key='hilbert_perf_morton')
    # def report_cput_morton(self):
    #     regex = r'compute time for \d+ morton keys: (\S+) s on CPU'
    #     return sn.round(sn.avg(
    #         sn.extractall(regex, self.stdout, 1, float)), 5)
    # # }}}
    #     # {{{ octree_perf
    #  {{{ There are actually three interesting metrics to extract:
    #    - build time from scratch 0.0577186 nNodes(tree): 441365 count: ...
    #    - first td-update: 0.0285318 construction of the internal octree
    #    - td-octree halo discovery: 0.0378064 collidingNodes: 8042 octree...
    #    the other metrics are not adding much in addition: the 2nd time you
    #    see build time from scratch it s for a slightly different particle
    #    distribution (plummer instead of gaussian)
    #  octree_perf:
    # *build time from scratch 0.174687 nNodes(tree): 441365 count: 2000000
    #  build time with guess 0.00604045 nNodes(tree): 441365 count: 2000000 ...
    #  binary tree halo discovery: 0.105535 collidingNodes: 8042
    # *first td-update: 0.0232271
    #  second td-update: 0.0231308
    # *td-octree halo discovery: 0.0720088 collidingNodes: 8042
    #  plummer box: -55.4645 56.2188 -54.7943 53.6066 -56.9695 57.3319
    #  build time from scratch 0.161216 nNodes(tree): 434211 count: 2000000
    #  build time with guess 0.00580249 nNodes(tree): 434211 count: 2000000 ...
    #  }}}
    #     @performance_function('s', perf_key='octree_perfcstone_construction')
    #     def report_octree_perf_0(self):
    #         regex = r'build time from scratch (\S+) nNodes'
    #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1,
    #         float)), 6)
    #
    #     @performance_function('s', perf_key='octree_perf_internal_octree')
    #     def report_octree_perf_1(self):
    #         regex = r'first td-update: (\S+)'
    #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1,
    #         float)), 6)
    #
    #     @performance_function('s', perf_key='octree_perf_tree_traversal')
    #     def report_octree_perf_2(self):
    #         regex = r'td-octree halo discovery: (\S+) collidingNodes'
    #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1,
    #         float)), 6)
    #     # }}}
    #     # {{{ scan_perf
    #     # serial benchmark bandwidth: 2035.05 MB/s
    #     # parallel benchmark bandwidth: 8181.65 MB/s
    #     # parallel inplace benchmark bandwidth: 31884.3 MB/s
    #     @performance_function('', perf_key='scan_perf_elements')
    #     def report_scan_perf_0(self):
    #         regex = r'scanning (\d+) elements'
    #         return sn.extractsingle(regex, self.stdout, 1, int)
    #
    #     @performance_function('MB/s', perf_key='scan_perf_serial')
    #     def report_scan_perf_1(self):
    #         regex = r'serial benchmark bandwidth: (\S+) MB/s'
    #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1,
    #           float)), 2)
    #
    #     @performance_function('MB/s', perf_key='scan_perf_parallel')
    #     def report_scan_perf_2(self):
    #         regex = r'parallel benchmark bandwidth: (\S+) MB/s'
    #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1,
    #           float)), 2)
    #
    #     @performance_function('MB/s', perf_key='scan_perf_parallel_inplace')
    #     def report_scan_perf_3(self):
    #         regex = r'parallel inplace benchmark bandwidth: (\S+) MB/s'
    #         return sn.round(sn.avg(sn.extractall(regex, self.stdout, 1,
    #           float)), 2)
    #     # }}}
    #
    # }}}
    # {{{ nsys
    # {{{ nvtxsum
    def report_nvtxsum(self, region="___01_domain.sync"):
        regex = r"(?P<pct>\S+),(\S+,){7}PushPop," + region
        return sn.round(sn.sum(sn.extractall(regex, "nvtxsum.rpt", "pct",
                                             float)), 2)

    @performance_function("%", perf_key="nsys_domain.sync")
    def nsys_p01(self):
        return self.report_nvtxsum("___01_domain.sync")

    @performance_function("%", perf_key="nsys_FindNeighbors")
    def nsys_p02(self):
        return self.report_nvtxsum("___02_FindNeighbors")

    @performance_function("%", perf_key="nsys_computeDensity")
    def nsys_p03(self):
        return self.report_nvtxsum("___03_computeDensity")

    @performance_function("%", perf_key="nsys_EquationOfState")
    def nsys_p04(self):
        return self.report_nvtxsum("___04_EquationOfState")

    @performance_function("%", perf_key="nsys_synchronizeHalos1")
    def nsys_p05(self):
        return self.report_nvtxsum("___05_synchronizeHalos1")

    @performance_function("%", perf_key="nsys_IAD")
    def nsys_p06(self):
        return self.report_nvtxsum("___06_IAD")

    @performance_function("%", perf_key="nsys_synchronizeHalos2")
    def nsys_p07(self):
        return self.report_nvtxsum("___07_synchronizeHalos2")

    @performance_function("%", perf_key="nsys_MomentumEnergyIAD")
    def nsys_p08(self):
        return self.report_nvtxsum("___08_MomentumEnergyIAD")

    @performance_function("%", perf_key="nsys_Timestep")
    def nsys_p09(self):
        return self.report_nvtxsum("___09_Timestep")

    @performance_function("%", perf_key="nsys_UpdateQuantities")
    def nsys_p10(self):
        return self.report_nvtxsum("___10_UpdateQuantities")

    @performance_function("%", perf_key="nsys_EnergyConservation")
    def nsys_p11(self):
        return self.report_nvtxsum("___11_EnergyConservation")

    @performance_function("%", perf_key="nsys_UpdateSmoothingLength")
    def nsys_p12(self):
        return self.report_nvtxsum("___12_UpdateSmoothingLength")

    @performance_function("%", perf_key="nsys_printIterationTimings")
    def nsys_p13(self):
        return self.report_nvtxsum("___13_printIterationTimings")

    @performance_function("%", perf_key="nsys_MPI")
    def nsys_p14(self):
        return self.report_nvtxsum("MPI:")
    # }}}

    # {{{ gpumemsizesum
    @performance_function("MB")
    def nsys_H2D(self):
        regex = r"(?P<mb>\S+),(\S+,){6}\[CUDA memcpy HtoD\]"
        return sn.extractsingle(regex, "gpumemsizesum.rpt", "mb", float)

    @performance_function("MB")
    def nsys_D2H(self):
        regex = r"(?P<mb>\S+),(\S+,){6}\[CUDA memcpy DtoH\]"
        return sn.extractsingle(regex, "gpumemsizesum.rpt", "mb", float)
    # }}}
    # }}}
    # {{{ ncu
    # {{{ occupancy metrics:
    # void sphexa::sph::cuda::cudaDensity
    # void sphexa::sph::cuda::cudaGradP
    # void sphexa::sph::cuda::cudaIAD

    # {{{ compute_peak
    @performance_function("%")
    def ncu_compute_peak_min(self):
        """Compute (SM) Througput (minimum)"""
        regex = (
            r"sphexa::sph::cuda::"
            + self.kernel_name
            + r".*\"sm__throughput.avg.pct_of_peak_sustained_elapsed\","
            + r"\"%\",\"(?P<pct>\S+)\"$"
        )
        return sn.round(sn.min(sn.extractall(regex, "rpt.csv", "pct", float)),
                        2)

    @performance_function("%")
    def ncu_compute_peak_avg(self):
        """Compute (SM) Througput (avg)"""
        regex = (
            r"sphexa::sph::cuda::"
            + self.kernel_name
            + r".*\"sm__throughput.avg.pct_of_peak_sustained_elapsed\","
            + r"\"%\",\"(?P<pct>\S+)\"$"
        )
        return sn.round(sn.avg(sn.extractall(regex, "rpt.csv", "pct", float)),
                        2)

    @performance_function("%")
    def ncu_compute_peak_max(self):
        """Compute (SM) Througput (maximum)"""
        regex = (
            r"sphexa::sph::cuda::"
            + self.kernel_name
            + r".*\"sm__throughput.avg.pct_of_peak_sustained_elapsed\","
            + r"\"%\",\"(?P<pct>\S+)\"$"
        )
        return sn.round(sn.max(sn.extractall(regex, "rpt.csv", "pct", float)),
                        2)
    # }}}

    # {{{ memory_peak
    @performance_function("%")
    def ncu_mem_peak_min(self):
        """Memory Througput (min)"""
        regex = (
            r"sphexa::sph::cuda::"
            + self.kernel_name
            + r".*\"gpu__compute_memory_throughput.avg."
            + r"pct_of_peak_sustained_elapsed\",\"%\",\"(?P<pct>\S+)\"$"
        )
        return sn.round(sn.min(sn.extractall(regex, "rpt.csv", "pct", float)),
                        2)

    @performance_function("%")
    def ncu_mem_peak_avg(self):
        """Memory Througput (avg)"""
        regex = (
            r"sphexa::sph::cuda::"
            + self.kernel_name
            + r".*\"gpu__compute_memory_throughput.avg."
            + r"pct_of_peak_sustained_elapsed\",\"%\",\"(?P<pct>\S+)\"$"
        )
        return sn.round(sn.avg(sn.extractall(regex, "rpt.csv", "pct", float)),
                        2)

    @performance_function("%")
    def ncu_mem_peak_max(self):
        """Memory Througput (max)"""
        regex = (
            r"sphexa::sph::cuda::"
            + self.kernel_name
            + r".*\"gpu__compute_memory_throughput.avg."
            + r"pct_of_peak_sustained_elapsed\",\"%\",\"(?P<pct>\S+)\"$"
        )
        return sn.round(sn.max(sn.extractall(regex, "rpt.csv", "pct", float)),
                        2)
    # }}}
    # }}}
    # }}}

    # {{{ memory
    @performance_function('%', perf_key='highmem_rss')
    def report_highmem_rss(self):
        # regex = r'^.*%\s+(?P<pct>\S+)%\s+\S+%\s+$'
        regex = r'^.*\s+(?P<pct>\S+)% $'
        if self.current_environ.name in ['PrgEnv-arm-A64FX']:
            return sn.max(sn.extractall(regex, 'smem.rpt', 'pct', float))
        else:
            return 0
    # }}}

#     # {{{ L1 errors
#     @performance_function("np", perf_key="L1_particles")
#     def report_L1_np(self):
#         regex = r"Loaded (\S+) particles"
#         return sn.extractsingle(regex, self.stdout, 1, int)
#
#     @performance_function("", perf_key="L1_error_density")
#     def report_L1_density(self):
#         regex = r"Density L1 error (\S+)"
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, float), 6)
#
#     @performance_function("", perf_key="L1_error_pressure")
#     def report_L1_pressure(self):
#         regex = r"Pressure L1 error (\S+)"
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, float), 6)
#
#     @performance_function("", perf_key="L1_error_velocity")
#     def report_L1_velocity(self):
#         regex = r"Velocity L1 error (\S+)"
#         return sn.round(sn.extractsingle(regex, self.stdout, 1, float), 6)
#     # }}}
# }}}


# {{{ build
@rfm.simple_test
class build(rfm.CompileOnlyRegressionTest):
    """
    x1='--module-path +/sw/wombat/ARM_Compiler/21.1/modulefiles'
    x2='--module-path +$HOME/modulefiles'
    x="$x1 $x2"
    R -c 0.py -n build -r $x -m nvhpc-nompi/21.9 -m gcc/9.3.0 -p PrgEnv-gnu
    """
    sourcesdir = "SPH-EXA.git"
    use_info = parameter([False])
    use_armpl = parameter(["without_armpl"])
    # use_armpl = parameter(["with_armpl", "without_armpl"])
    # use_tool = parameter([False, True])
    # use_tool = parameter(["Score-P/7.1-CrayNvidia-21.09"])
    # use_tool = parameter(["Score-P"])
    # sourcepath = "$HOME"
    # use_tool = parameter(["notool"])
    # mypath = variable(str, value=".")
    # compute_nodes = parameter([1])
    # compute_nodes = parameter([1, 2, 4, 8, 16])
    # np_per_c = parameter([5.34e6]) #ko 6.4e6
    # sk wants 5.34e6 ok 6.0e6, 6.2e6 does not scale
    # ---- wombat
    # compute_nodes = parameter([1, 2, 4])
    # np_per_c = parameter([45e5]) # OK <------------- -n572 = 187"149"248/2gpu
    # donotscale np_per_c = parameter([47e5]) # OK <-- -n572 = 187"149"248/2gpu
    # 47e5 ok  / 48e5 ko
    # ----
    valid_systems = ["wombat:gpu", "dom:gpu", "dom:mc", "lumi:gpu"]
    valid_prog_environs = [
        # 'builtin',
        "PrgEnv-arm-N1",
        "PrgEnv-arm-TX2",
        "PrgEnv-arm-A64FX",
        "PrgEnv-nvidia",
        "PrgEnv-nvidia-A64FX",
        "PrgEnv-gnu",
        "PrgEnv-gnu-A64FX",
        "PrgEnv-cray",
    ]

    # {{{ compile
    @run_before("compile")
    def set_compile(self):
        self.build_system = "CMake"
        partition = self.current_partition.name
        env = self.current_environ.name
        if hdf5_mod[partition][env]:
            self.modules = [hdf5_mod[partition][env]]

        compiler_flags = {
            "mc": {
                "PrgEnv-cray": "",
                "PrgEnv-gnu": "",
                "PrgEnv-intel": "",
                "PrgEnv-nvidia": "",
            },
            "gpu": {
                "PrgEnv-cray": "",
                "PrgEnv-gnu": "",
                "PrgEnv-intel": "",
                "PrgEnv-nvidia": "",
            },
            "a100": {
                "PrgEnv-cray": "",
                "PrgEnv-gnu": "-mcpu=cascadelake",
                "PrgEnv-intel": "",
                "PrgEnv-nvidia": "",
            },
            # [current_partition.name][current_environ.name]
            "neoverse-n1": {
                "PrgEnv-arm-N1": "-g -mcpu=neoverse-n1",
                "PrgEnv-gnu": "-g -mcpu=neoverse-n1",
                "PrgEnv-nvidia": "-tp=neoverse-n1",
                # -tp=host|native|neoverse-n1
                #     host   Link native version of HPC SDK cpu math library
                #     native Alias for -tp host
                #     neoverse-n1 Arm Neoverse N1 architecture
                # Jeff Hammond (NVIDIA): "NVC++ currently does not specialize
                #                        "for ARM microarchitectures"
            },
            "TX2": {
                "PrgEnv-arm-TX2": "-g -mcpu=thunderx2t99",
                "PrgEnv-gnu": "-g -mcpu=thunderx2t99",
                "PrgEnv-nvidia": "-tp=host",
            },
            "A64FX": {
                "PrgEnv-arm-A64FX": "-g -mcpu=a64fx",
                "PrgEnv-gnu-A64FX": "-g -mcpu=a64fx",
                # i.e -march=armv8.2-a+sve -mtune=a64fx (Wael Elwasif)
                "PrgEnv-nvidia-A64FX": "",
            },
        }
        self.build_system.flags_from_environ = False
        if self.current_environ.name in ["PrgEnv-gnu", "PrgEnv-gnu-A64FX"]:
            self.prebuild_cmds = [
                # TODO: https://reframe-hpc.readthedocs.io
                # config_reference.html -> unload#general-.unload_modules
                "module rm gnu10/10.2.0 binutils/10.2.0",
            ]
        elif self.current_environ.name in ["PrgEnv-nvidia",
                                           "PrgEnv-nvidia-A64FX"]:
            file1 = 'CMakeLists.txt'
            file2 = 'domain/test/coord_samples/CMakeLists.txt'
            file3 = 'domain/test/integration_mpi/CMakeLists.txt'
            file4 = 'ryoanji/test/cpu/CMakeLists.txt'
            self.prebuild_cmds = [
                f'sed -i "s@-fno-math-errno@@" {file1}',
                f'sed -i "s@-Wno-unknown-pragmas@-w@" {file2}',
                f'sed -i "s@-Wno-unknown-pragmas@-w@" {file3}',
                f'sed -i "s@-Wno-unknown-pragmas@-w@" {file4}',
                "echo > src/evrard/CMakeLists.txt",
                # 1 catastrophic error detected in the compilation of
                # "src/evrard/evrard.cpp".
                "echo > domain/test/unit/CMakeLists.txt",
                "echo > ryoanji/test/cpu/CMakeLists.txt",
                "## echo > src/analytical_solutions/CMakeLists.txt",
                # sedov_solution/main.cpp", line 134: error: namespace "std"
                # has no member "setw"
                # TODO: domain/test/integration_mpi/CMakeLists.txt /
                # mpi_wrappers.hpp, line 115: internal error: assertion failed:
                # missing rescan info (exprutil.cpp, line 4772 in
                # get_expr_rescan_info)
                'sed -i "s@addMpiTest(exchange_focus.cpp@'
                '#addMpiTest(exchange_focus.cpp@" {file3}',
                'sed -i "s@addMpiTest(exchange_general.cpp@'
                '#addMpiTest(exchange_general.cpp@" {file3}',
                # avoid warnings:
                "echo >> domain/include/cstone/cuda/annotation.hpp",
                "echo >> domain/include/cstone/traversal/collisions.hpp",
                "echo >> domain/include/cstone/tree/btree.cuh",
                "echo >> domain/include/cstone/traversal/peers.hpp",
                "echo >> domain/test/performance/timing.cuh",
                "echo >> ryoanji/src/ryoanji/cpu/multipole.hpp",
                "echo >> domain/include/cstone/cuda/gather.cu",
            ]
        elif self.current_environ.name in [
            "PrgEnv-arm-N1",
            "PrgEnv-arm-TX2",
            "PrgEnv-arm-A64FX",
        ]:
            self.prebuild_cmds = [
                'sed -i "s@inline static constexpr std::array fieldNames@'
                'inline static std::array fieldNames@" '
                'include/particles_data.hpp',
            ]

        info_flag = {
            "PrgEnv-gnu": "-fopt-info-vec-missed",
            "PrgEnv-gnu-A64FX": "-fopt-info-vec-missed",
            #
            # -fsave-optimization-record
            "PrgEnv-arm-N1": "-Rpass-analysis=loop-vectorize",
            "PrgEnv-arm-TX2": "-Rpass-analysis=loop-vectorize",
            "PrgEnv-arm-A64FX": "-Rpass-analysis=loop-vectorize",
            #
            "PrgEnv-nvidia": "-Minfo",
            "PrgEnv-nvidia-A64FX": "-Minfo",
        }
        compiler_info_flag = ""
        if self.use_info:
            compiler_info_flag = info_flag[self.current_environ.name]

        cp = self.current_partition.name
        envn = self.current_environ.name
        self.prebuild_cmds += [
            "module list",
            "mpicxx --version || true",
            "nvcc --version || true",
            "rm -fr docs LICENSE Makefile README.* scripts test tools",
            'sed -i "s@project(sphexa CXX C)@project(sphexa CXX)@" '
            'CMakeLists.txt',
            # C needed with h5part
            f'sed -i "s@-march=native@{compiler_flags[cp][envn]} '
            f'{compiler_info_flag}@" CMakeLists.txt',
            'sed -i "s@constexpr operator MPI_Datatype@'
            'operator MPI_Datatype@" '
            'domain/include/cstone/primitives/mpi_wrappers.hpp',
        ]
        if self.current_partition.name in ["A64FX"]:
            self.build_system.nvcc = ""

        self.build_system.builddir = "build"
        self.build_system.config_opts = [
            # "-DCMAKE_CXX_COMPILER=CC",
            # "-DCMAKE_CUDA_FLAGS="-ccbin cc"",
            "-DCMAKE_CXX_COMPILER=mpicxx",
            "-DCMAKE_CUDA_FLAGS=\"-ccbin mpicxx -arch=sm_80\"",
            # "-DCMAKE_CUDA_COMPILER=`which nvcc`",
            # f"-DCMAKE_CUDA_COMPILER={self.hasnvcc}",
            "-DBUILD_TESTING=ON",
            "-DBUILD_ANALYTICAL=OFF",
            "-DSPH_EXA_WITH_HIP=OFF",
            # "-DBUILD_RYOANJI=ON",
            "-DCMAKE_INSTALL_PREFIX=$PWD/JG",
            # "-DCMAKE_BUILD_TYPE=Debug",
            "-DCMAKE_BUILD_TYPE=Release",
        ]

        if self.use_armpl == "with_armpl":
            if self.current_environ.name in [
                "PrgEnv-arm-N1",
                "PrgEnv-arm-TX2",
                "PrgEnv-arm-A64FX",
            ]:
                self.build_system.config_opts +=
                ["-DCMAKE_EXE_LINKER_FLAGS=-armpl"]
            else:
                if self.current_environ.name in [
                    "PrgEnv-nvidia",
                    "PrgEnv-nvidia-A64FX",
                ]:
                    self.skip_if(
                        self.use_armpl == "with_armpl",
                        "no armpl with nvhpc compilers"
                    )
                    self.build_system.config_opts += [
                        "-DCMAKE_EXE_LINKER_FLAGS='-lgfortran -larmpl'"
                    ]
                else:
                    self.build_system.config_opts += [
                        "-DCMAKE_EXE_LINKER_FLAGS='-larmpl'"
                    ]

        if self.use_tool:
            self.build_system.config_opts += ['-DUSE_PROFILING=ON']
        else:
            self.build_system.config_opts += ['-DUSE_PROFILING=OFF']

        self.build_system.max_concurrency = 10
        self.build_system.make_opts = [
            "sphexa",
            "sphexa-cuda",
            "hilbert_perf",
            "hilbert_perf_gpu",
        ]  # ['install']
        if self.use_info:
            self.build_system.make_opts = ["hilbert_perf"]
            self.postbuild_cmds += ["ldd sphexa |grep armpl || true"]
    # }}}

    @sanity_function
    def assert_sanity(self):
        return sn.all([
            sn.assert_not_found("error", self.stdout),
        ])
# }}}
