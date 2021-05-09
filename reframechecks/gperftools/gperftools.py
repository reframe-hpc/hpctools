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
import sphexa.sanity_gperftools as sphsgperf


# {{{ class SphExa_Gperftools_Check
@rfm.simple_test
class SphExa_Gperftools_Check(rfm.RegressionTest, hooks.setup_pe,
                              hooks.setup_code):
    # {{{
    '''
    This class runs the test code with gperftools (mpi+openmp):
    https://gperftools.github.io/gperftools/cpuprofile.html
    '''
    # }}}
    steps = parameter([4])
    compute_node = parameter([1])
    # compute_node = parameter([100, 200, 300, 400, 500])
    np_per_c = parameter([1e4])
    gperftools_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['*']
        self.valid_systems = ['*']
        self.modules = ['gperftools']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.tool = 'pprof'
        self.which_rpt = 'which.rpt'
        self.prebuild_cmds = [
            f'which {self.tool} &> {self.which_rpt}',
            f'which $EBROOTPPROF/bin/{self.tool} >> {self.which_rpt}',
        ]
        # }}}

        # {{{ run
        self.rpt_file = 'gperftools.rpt'
        self.rpt_file_txt = f'{self.rpt_file}.txt'
        self.rpt_file_pdf = f'{self.rpt_file}.pdf'
        self.rpt_file_doc = f'{self.rpt_file}.doc'
        self.postrun_tool = '$EBROOTPPROF/bin/pprof'
        self.postrun_cmds += [
            f'# -------------------------------------------------------------',
            f'# create reports (txt and pdf)',
            # txt rpt (quotation mark will make it fail):
            f'{self.postrun_tool} --unit=ms --text --lines *.0 &> '
            f'{self.rpt_file_txt}',
            # pdf rpt:
            f'{self.postrun_tool} --pdf *.0 &> {self.rpt_file_pdf}',
            # check that pdf file is a pdf:
            f'file {self.rpt_file_pdf} &> {self.rpt_file_doc}',
            f'# -------------------------------------------------------------',
        ]
        # }}}

        # {{{ sanity
        self.sanity_patterns = sn.all([
            # check the job output:
            sn.assert_found(r'Total time for iteration\(0\)', self.stdout),
            # check the tool report:
            sn.assert_found('PDF document', self.rpt_file_doc),
        ])
        # }}}

    # {{{ hooks
    @rfm.run_before('run')
    def set_tool_options(self):
        tool_scriptname = 'gperftools_script.sh'
        tool_script = os.path.join(self.stagedir, tool_scriptname)
        with open(tool_script, 'w') as fp:
            fp.write('#!/bin/bash\n')
            fp.write('CPUPROFILE=`hostname`.$SLURM_PROCID ./"$@"\n')

        self.prerun_cmds += [f'chmod u+x {tool_scriptname}']
        self.job.launcher.options += [tool_scriptname]

    @rfm.run_before('performance')
    def set_tool_perf_patterns(self):
        self.perf_patterns.update({
            'gperftools_top_function1': sphsgperf.gp_perf_patterns(self, 1),
        })

    @rfm.run_before('performance')
    def set_tool_perf_reference(self):
        top1 = '% ' + sphsgperf.gp_perf_patterns(self, 4)
        myzero_top1_p = (0, None, None, top1)
        self.reference['*:gperftools_top_function1'] = myzero_top1_p
    # }}}

# }}}
