# Copyright 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.hooks as hooks
from reframe.core.backends import getlauncher


# {{{ class SphExaGdb4hpcCheck
@rfm.simple_test
class SphExa_Gdb4hpc_Check(rfm.RegressionTest, hooks.setup_pe,
                           hooks.setup_code):
    # {{{
    '''
    This class runs the test code with Cray gdb4hpc
    '''
    # }}}
    steps = parameter([1])
    compute_node = parameter([1])
    tool_compute_node = parameter([2])
    # tool_compute_node = parameter([1, 2, 4, 8, 16, 32, 64, 128])
    np_per_c = parameter([1e4])

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            'PrgEnv-aocc', 'cpeAMD', 'cpeCray', 'cpeGNU', 'cpeIntel']
        # NOTE: dom (slurm/20.11.4) is failing
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.tool = 'gdb4hpc'
        self.modules = [self.tool]
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.sourcepath = f'{self.testname}.cpp'
        # TODO: self.prgenv_flags = -O0
        self.executable = self.tool
        self.target_executable = './mpi+omp'
        # self.sourcepath = f'{self.testname}.cpp'
        # self.target_executable = f'./{self.testname}.exe'
        # self.postbuild_cmds = [f'mv {self.tool} {self.target_executable}']
        # }}}

        # {{{ run
        self.time_limit = '10m'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.gdb_slm = './gdb4hpc.slm'
        self.gdb_in = './gdb4hpc.in'
        self.gdb_rpt = './gdb4hpc.rpt'
        self.executable_opts = [f'-b {self.gdb_in} #']
        self.prerun_cmds = [
            f'srun --version >> {self.version_rpt}',
            f'{self.tool} --version >> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
            'echo starttime=`date +%s`',  # this is needed because:
            '# Everything between the "#cray_debug_xxx" lines will be ignored',
            '#cray_debug_start',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Shutting down debugger and killing application',
                            self.stdout),
        ])
        # }}}

    # {{{ performance
    # see common/sphexa/hooks.py
    # }}}

    # {{{ hooks
    # {{{ NOTE: gdb4hpc launches another job, we must use a trick here:
    # step1: rfm_job.sh calls gdb4hpc:
    #   #SBATCH == 1cn   <--- job1 --> rfm_job.sh
    #   #cray_debug_start : gdb4hpc -b ./gdb4hpc.in : #cray_debug_stop
    #   TODO: use login node (require to find a way to generate SBATCH lines)
    # step2: gdb4hpc launches another job:
    #   #SBATCH >= 1cn  <--- job2 --> gdb4hpc.slm
    #   #cray_debug_start : gdb4hpc -b ./gdb4hpc.in : #cray_debug_stop
    #   where gdb4hpc.in lists the commands to execute:
    #       launch $tst{4} ./mpi+omp --sbatch=./gdb4hpc.slm --args="-s 1 -n 50"
    # step3: squeue
    #   JOBID  ACCOUNT           NAME EXEC_HOST ST NODES
    #   35669  csstaff rfm_SphExa_Gdb nid001082  R     1
    #   35670  csstaff rfm_SphExa_Gdb nid001368  R     2
    # NOTE: gdb4hpc uses $HOME/.gdb4hpc/batch*
    # NOTE: > f'--launcher-args="-C mc" '
    #       > --args: '' are ignored, use "" instead
    # }}}
    # {{{ setup_tool
    @rfm.run_before('run')
    def setup_tool(self):
        # {{{ TODO: remove this when cpuinfo is merged
        cpf = self.current_partition.fullname  # cpf=dom:gpu
        processor = {
            'eiger:mc': {
                'arch': 'zen2', 'num_cpus': 256, 'num_cpus_per_core': 2,
                'num_cpus_per_socket': 128, 'num_sockets': 2,
                'num_cores': 128, 'num_cores_per_socket': 64,
                'num_numa_nodes': 8, 'num_cores_per_numa_node': 16,
            },
            'daint:mc': {
                'arch': 'broadwell', 'num_cpus': 72, 'num_cpus_per_core': 2,
                'num_cpus_per_socket': 36, 'num_sockets': 2,
                'num_cores': 36, 'num_cores_per_socket': 18,
                'num_numa_nodes': 2, 'num_cores_per_numa_node': 18,
            },
            'daint:gpu': {
                'arch': 'haswell', 'num_cpus': 24, 'num_cpus_per_core': 2,
                'num_cpus_per_socket': 24, 'num_sockets': 1,
                'num_cores': 12, 'num_cores_per_socket': 12,
                'num_numa_nodes': 1, 'num_cores_per_numa_node': 12,
            },
        }
        processor['pilatus:mc'] = processor['eiger:mc'].copy()
        processor['dom:mc'] = processor['daint:mc'].copy()
        processor['dom:gpu'] = processor['daint:gpu'].copy()
        #
        # self.arch = processor[cpf]['arch']
        # self.num_cpus = processor[cpf]['num_cpus']
        # self.num_cpus_per_core = processor[cpf]['num_cpus_per_core']
        # self.num_cpus_per_socket = processor[cpf]['num_cpus_per_socket']
        self.num_sockets = processor[cpf]['num_sockets']
        self.num_cores = processor[cpf]['num_cores']
        self.num_cores_per_socket = processor[cpf]['num_cores_per_socket']
        #
        self.tool_num_tasks = self.tool_compute_node * self.num_sockets
        # 1*2=2, 2*2=4, 4*2=8
        self.num_tasks_per_node = self.num_cores // self.num_cores_per_socket
        # 128/64=2, =2, =2
        self.num_cpus_per_task = self.num_cores // self.num_tasks_per_node
        # 128/2=64, =64, =64
        # }}}
        tmpf = './eff.slm'
        self.prerun_cmds += [
            f'#{{{{{{ ---- jobscript for gdb ({self.gdb_slm}) ----',
            f'sed "s/^#SBATCH --ntasks=.*'
            f'/#SBATCH --ntasks={self.tool_num_tasks}/" '
            f'{self.job.script_filename} &> {tmpf}',
            # ntasks-per-node, cpus-per-task and OMP_NUM_THREADS are the same
            f'egrep -v "#@|^gdb4hpc|^egrep|^mv|^rm|^which|^sed" {tmpf} &>'
            f' {self.gdb_slm}',
            f'rm -f {tmpf}',
            f'# ---- jobscript for gdb ({self.gdb_slm}) ---- #}}}}}}',
        ]
        self.postrun_cmds += [
            '#cray_debug_stop',
        ]
        self.executable = self.tool
        # debug on smaller cubesize (self.np_per_c/2):
        total_np = (self.tool_compute_node * self.num_tasks_per_node *
                    self.num_cpus_per_task * self.np_per_c/2)
        self.cubeside = int(pow(total_np, 1 / 3))
        tool_launch_str = (
            f'launch $tst{{{self.tool_num_tasks}}} {self.target_executable} '
            f'--sbatch={self.gdb_slm} '
            f'--args="-s {self.steps} -n {self.cubeside}"'
        )
        # {{{ gdb commands to execute:
        gdb4hpc_in = f"""#@ # ------------------------------------------------
        #@ # gdb4hpc --help: --batch=FILE, Execute debugger commands from FILE
        #@ # --- make gdb4hpc execute a list of commands with --batch=...
        #@ # --- or attach to a job with > gdb4hpc: attach $tst <jobid>.0
        #@ # --- or launch a job from login node with > gdb4hpc: launch ...
        #@ # ------------------------------------------------------------------
        #@ # this line is mandatory (cray case #224617):
        #@ maint set sync on
        #@ # this line is needed in C++ to avoid:
        #@ #   "Debugger error: Missing PMI_Init symbol"
        #@ maint set unsafe on
        #@ {tool_launch_str}
        #@ #
        #@ break 51
        #@ continue
        #@ list
        #@ whatis cubeSide
        #@ print cubeSide
        #@ # run
        #@ # info sources
        #@ break include/sph/findNeighborsSfc.hpp:84
        #@ info breakpoints
        #@ viewset
        #@ continue
        #@ list
        #@ bt
        #@ whatis sum
        #@ print sum
        #@ # TODO: check stderr
        #@ # kill
        #@ # print domain.clist[1]
        #@ continue
        #@ continue
        #@ continue
        #@ quit
        #@ """
        self.prerun_cmds += [
            f'#{{{{{{ ---- gdb commands to execute ({self.gdb_in}) ----',
            f'echo -e \'{gdb4hpc_in}\' |sed "s-#@--" > {self.gdb_in}',
            f'# ---- gdb commands to execute ({self.gdb_in}) ---- #}}}}}}',
        ]
        # }}}
    # }}}

    # {{{ set_launcher
    @rfm.run_before('run')
    def set_launcher(self):
        # The job launcher has to be changed because
        # the tool can be called without srun
        self.job.launcher = getlauncher('local')()
    # }}}
    # }}}
# }}}
