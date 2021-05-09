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
import sphexa.sanity as sphs
import sphexa.sanity_mpip as sphsmpip


# {{{ class SphExa_mpiP_Check
@rfm.simple_test
class SphExa_mpiP_Check(rfm.RegressionTest, hooks.setup_pe,
                        hooks.setup_code):
    # {{{
    '''
    This class runs the test code with mpiP (mpi+openmp):
    http://llnl.github.io/mpiP
    '''
    # }}}
    steps = parameter([4])
    compute_node = parameter([2])
    # compute_node = parameter([100, 200, 300, 400, 500])
    np_per_c = parameter([1e4])
    mpip_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['mpiP']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.tool = 'pprof'
        self.which_rpt = 'which.rpt'
        self.prebuild_cmds = [
            # f'which {self.tool} &> {self.which_rpt}',
            # f'which $EBROOTPPROF/bin/{self.tool} >> {self.which_rpt}',
        ]
        # }}}

        # {{{ run
        # self.variables = {'MPIP': '"-c"',}
        # -c: concise version of report
        # -d: suppress callsite details
        # -p: report histogram of point-to-point MPI calls
        # -y: report histogram of collective MPI calls
        #
        # libpath = '$EBROOTMPIP/lib'
        # self.variables['LD_LIBRARY_PATH'] = f'{libpath}:$LD_LIBRARY_PATH'
        self.rpt_file = 'mpip.rpt'
        self.postrun_cmds += [
            f'# -------------------------------------------------------------',
            f'# -------------------------------------------------------------',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool report:
            # sn.assert_found('PDF document', self.rpt_file_doc),
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('performance')
    def set_tool_perf_patterns(self):
        self.perf_patterns.update({
            'mpip_avg_mpi_time': sphsmpip.mpip_perf_patterns(self, 1),
            'mpip_avg_app_time': sphsmpip.mpip_perf_patterns(self, 2),
            '%mpip_avg_mpi_time_max': sphsmpip.mpip_perf_patterns(self, 5),
            '%mpip_avg_mpi_time': sphsmpip.mpip_perf_patterns(self, 3),
            '%mpip_avg_mpi_time_min': sphsmpip.mpip_perf_patterns(self, 6),
            '%mpip_avg_non_mpi_time': sphsmpip.mpip_perf_patterns(self, 4),
        })

    @rfm.run_before('performance')
    def set_tool_perf_reference(self):
        myzero_s = (0, None, None, 's')
        myzero_p = (0, None, None, '%')
        self.reference['*:mpip_avg_mpi_time'] = myzero_s
        self.reference['*:mpip_avg_app_time'] = myzero_s
        self.reference['*:%mpip_avg_mpi_time_max'] = myzero_p
        self.reference['*:%mpip_avg_mpi_time'] = myzero_p
        self.reference['*:%mpip_avg_mpi_time_min'] = myzero_p
        self.reference['*:%mpip_avg_non_mpi_time'] = myzero_p
    # }}}

# }}}
