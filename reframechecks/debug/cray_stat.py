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


# {{{ class SphExa_STAT_Check
@rfm.simple_test
class SphExa_STAT_Check(rfm.RegressionTest, hooks.setup_pe, hooks.setup_code):
    # {{{
    '''
    This class runs the test code with Cray stat
    '''
    # }}}
    steps = parameter([2])  # will hang rank0 at step0
    compute_node = parameter([1])
    np_per_c = parameter([1e3])
    debug_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'cpeGNU'
        ]
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.tool = 'stat-cl'
        self.modules = ['cray-stat', 'cray-cti']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype', 'debugging'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.executable = 'mpi+omp'
        # re_ver_1 = 'STAT_VERSION1=$'
        # re_ver_2 = 'STAT_VERSION2=$'
        version_rpt = 'version.rpt'
        which_rpt = 'which.rpt'
        cs = self.current_system.name
        if cs not in {'pilatus', 'eiger'}:
            self.prebuild_cmds += [
                # --- chech tool version
                f'echo STAT_VERSION1=$STAT_VERSION > {version_rpt}',
                f'echo STAT_VERSION2=`STATbin --version` >> {version_rpt}',
            ]
        else:
            self.prebuild_cmds += [
                # --- chech tool version
                f'echo STAT_VERSION1=$STAT_LEVEL > {version_rpt}',
                f'echo STAT_VERSION2=`STATbin --version` >> {version_rpt}',
            ]

        self.prebuild_cmds += [
            f'STATbin -V >> {version_rpt}',
            f'which {self.tool} > {which_rpt}',
        ]

        # {{{ run
        self.time_limit = '10m'
        # }}}

        # {{{ sanity
        # TODO: regex = (
        #     r'function="(?P<fun>.*)", source="(?P<filename>.*)",'
        #     r' line=":(?P<ll>\d+)"'
        # )
        # + cuda
        # + largescale
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Starting main loop', self.stdout),
            # check the tool output:
            sn.assert_not_found('not found', which_rpt),
            sn.assert_not_found('ERROR', self.stdout),
            # <LMON FE API> (ERROR): read_lmonp_msgheader failed while
            # attempting to receive continue launch message from back end
            sn.assert_found(r'STAT started', self.stdout),
            sn.assert_found(r'Attaching to job launcher', self.stdout),
            sn.assert_found(r'launching tool daemons', self.stdout),
            sn.assert_found(r'Results written to', self.stdout),
        ])
        # }}}

        # {{{ performance
        # see common/sphexa/hooks.py
        # }}}

    # {{{ hooks
    # {{{ set_hang
    @run_before('compile')
    def set_hang(self):
        source_file = 'include/sph/totalEnergy.hpp'
        die = '60'
        sed_header = (r'"s@USE_MPI@USE_MPI\n#include <thread>@"')
        sed_hang = (
            r'"/MPI_Allreduce(MPI_IN_PLACE, &einttmp, 1, MPI_DOUBLE, MPI_SUM, '
            r'MPI_COMM_WORLD);/a'
            r'int mpirank; MPI_Comm_rank(MPI_COMM_WORLD, &mpirank);'
            r'if (mpirank == 0 && d.iteration == 0) '
            r'{std::this_thread::sleep_for(std::chrono::seconds('f'{die}));'
            r'}"'
        )
        self.prebuild_cmds += [
            f'# --- make the code hang:',
            f'sed -i {sed_header} {source_file}',
            f'sed -i {sed_hang} {source_file}',
        ]
    # }}}

    # {{{ set_tool
    @run_before('run')
    def set_tool(self):
        self.executable_opts += ['& #']
        # FIXME: will default to: '& # -n 50 -s 2'
        ssh_cmd = 'ssh -o "StrictHostKeyChecking no"'
        self.postrun_cmds = [
            # slurm only
            'nid=`SQUEUE_FORMAT=%.9B squeue --noheader -j $SLURM_JOBID`',
            f'pidsrun=`{ssh_cmd} $nid "ps -hxo pid,cmd |grep -m1 srun" `',
            'pid=${pidsrun% srun*}',
            'echo "# nid=$nid pid=$pid"',
            'sleep 1',
            f'tool=`which {self.tool}`',
            'echo "tool=$tool"',
            f'{ssh_cmd} $nid "cd {self.stagedir} ;'
            f'$tool -i -j $SLURM_JOBID $pid"',
            'wait',
            'echo done'
        ]
    # }}}
    # }}}
# }}}
