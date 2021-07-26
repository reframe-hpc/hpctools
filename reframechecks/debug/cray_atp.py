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
# TODO: from reframe.core.backends import getlauncher


# {{{ class SphExa_Atp_Check
@rfm.simple_test
class SphExa_Atp_Check(rfm.RegressionTest, hooks.setup_pe, hooks.setup_code):
    # {{{
    '''
    This class runs the test code with Cray atp
    '''
    # }}}
    steps = parameter([2])  # will crash rank1 at step0
    compute_node = parameter([2])
    np_per_c = parameter([1e3])
    debug_flags = variable(bool, value=True)

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'cpeGNU'
            # 'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            # 'PrgEnv-aocc', 'cpeGNU', 'cpeIntel', 'cpeCray', 'cpeAMD',
        ]
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.tool = 'atp'
        self.modules = [self.tool, 'cray-stat']  # cray-cti
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype', 'debugging'}
        # }}}

        # {{{ compile
        self.testname = 'sedov'
        self.sourcepath = f'{self.testname}.cpp'
        # atp requires full path:
        self.executable = './mpi+omp'
        cs = self.current_system.name
        re_slm_1 = 'libAtpSigHandler.so'
        re_slm_2 = 'libAtpDispatch.so'
        re_epr_ini1 = '^slurm = True'
        re_epr_cfg1 = '.debug., .ps., None, False'
        re_epr_cfg2 = '.eproxy., .eproxy., None, True'
        re_hosts_1 = 'login'
        re_ver_1 = 'STAT_VERSION1=$'
        re_ver_2 = 'STAT_VERSION2=$'
        re_ver_3 = 'ATP_VERSION1=$'
        re_ver_4 = 'ATP_VERSION2=$'
        re_ver_5 = 'ATP_HOME=$'
        re_which_1 = 'not found'
        re_stderr_1 = 'forcing job termination|Force Terminated (job|Step)'
        re_stderr_2 = 'Producing core dumps for rank'
        re_stderr_3 = 'View application merged backtrace tree with: stat-view'
        re_dot_1 = 'MPI_Allreduce|MPID_Abort|PMPI_Abort'
        re_dot_2 = 'sphexa::sph::|cstone::'
        re_core_1 = 'core file x86-64'
        # TODO: grep sphexa::sph atpMergedBT_line.dot -> perf_patterns
        #   94 [pos="0,0", label="sphexa::sph::neighborsSum(...
        ldd_rpt = 'ldd.rpt'
        cfg_rpt = 'cfg.rpt'
        version_rpt = 'version.rpt'
        which_rpt = 'which.rpt'
        slurm_cfg_file = '/etc/opt/slurm/plugstack.conf'
        cfg_file_path = '/opt/cray/elogin/eproxy'
        eproxy_ini_cfg_file = f'{cfg_file_path}/etc/eproxy.ini'
        eproxy_cfg_file = f'{cfg_file_path}/default/bin/eproxy_config.py'
        hosts_cfg_file = '/etc/hosts'
        apt_dot_file = 'atpMergedBT_line.dot'
        # TODO: regex_rk0 = 'core.atp.*.0.0.*'
        # {{{ Needed when reporting a support case:
        if cs not in {'pilatus', 'eiger'}:
            self.prebuild_cmds += [
                # --- check slurm_cfg
                #     (optional /opt/cray/pe/atp/libAtpDispatch.so)
                f'grep "{re_slm_2}" {slurm_cfg_file} > {cfg_rpt}',
                # --- check ini_cfg_file (slurm = True)
                f'grep "{re_epr_ini1}" {eproxy_ini_cfg_file} >> {cfg_rpt}',
                # --- check eproxy_cfg_file (['debug', 'ps', None, False])
                f'grep "{re_epr_cfg1}" {eproxy_cfg_file} >> {cfg_rpt}',
                # --- check eproxy_cfg_file (['eproxy', 'eproxy', None, True])
                f'grep "{re_epr_cfg2}" {eproxy_cfg_file} >> {cfg_rpt}',
                # --- check STAT_MOM_NODE in /etc/hosts (daintgw01|domgw03)
                f'grep "{re_hosts_1}" {hosts_cfg_file} >> {cfg_rpt}',
                # --- chech stat version
                f'echo STAT_VERSION1=$STAT_VERSION > {version_rpt}',
                f'echo STAT_VERSION2=`STATbin --version` >> {version_rpt}',
            ]
        else:
            self.prebuild_cmds += [
                # --- chech stat version
                f'echo STAT_VERSION1=$STAT_LEVEL > {version_rpt}',
                f'echo STAT_VERSION2=`STATbin --version` >> {version_rpt}',
            ]
        # }}}

        self.prebuild_cmds += [
            # TODO: open cray case
            f'export PKG_CONFIG_PATH=$ATP_INSTALL_DIR/lib/pkgconfig:'
            f'$PKG_CONFIG_PATH',
            # --- check atp version and path
            f'echo ATP_VERSION1=$ATP_VERSION >> {version_rpt}',
            f'echo ATP_VERSION2='
            f'`pkg-config --modversion libAtpSigHandler` >> {version_rpt}',
            f'echo ATP_HOME=$ATP_HOME >> {version_rpt}',
            f'pkg-config --variable=exec_prefix libAtpSigHandler &>{which_rpt}'
        ]
        self.postbuild_cmds += [
            # --- check exe (/opt/cray/pe/atp/3.8.1/lib/libAtpSigHandler.so.1)
            f'ldd {self.executable}* |grep "{re_slm_1}" &> {ldd_rpt}',
        ]
        # }}}

        # {{{ run
        self.time_limit = '10m'
        self.variables['ATP_ENABLED'] = '1'
        self.postrun_cmds += [
            f'ldd {self.executable}* |grep atp',
            'file core*'
        ]
# {{{ TODO: gdb_command
# -        gdb_command = (r'-e %s '
# -                       r'--eval-command="set pagination off" '
# -                       r'--eval-command="bt" '
# -                       r'--eval-command="quit"' % self.executable)
# -        regex_not_rk0 = r'grep -m1 -v atp'
# -        self.postrun_cmds = [
# -            'echo stoptime=`date +%s`',
# -            # --- rank 0: MPI_Allreduce
# -            f'gdb -c {regex_rk0} {gdb_command} &> {self.rpt_rk0}',
# -
# -            # --- rank>2: MPI::Comm::Abort
# -#            f'ln -s `ls -1 core.* |{regex_not_rk0}` mycore',
# -#            f'gdb -c mycore {gdb_command} &> {self.rpt_rkn}',
# -            # can't do this because core filename is unknown at runtime:
# -            # 'gdb -c core.atp.*.%s.* -e %s' % (self.core, self.executable),
# -
# -            '# stat-view atpMergedBT_line.dot'
# }}}
        # }}}

        # {{{ sanity
        # TODO: self.sanity_patterns += ... ?
        if cs in {'pilatus', 'eiger'}:
            self.sanity_patterns = sn.all([
                # check the job output:
                sn.assert_found(r'UpdateSmoothingLength: \S+s', self.stdout),
                # check the tool output:
                sn.assert_found(re_slm_1, ldd_rpt),
                #
                sn.assert_not_found(re_ver_1, version_rpt),
                sn.assert_not_found(re_ver_2, version_rpt),
                sn.assert_not_found(re_ver_3, version_rpt),
                sn.assert_not_found(re_ver_4, version_rpt),
                sn.assert_not_found(re_ver_5, version_rpt),
                sn.assert_not_found(re_which_1, which_rpt),
                #
                sn.assert_found(re_stderr_1, self.stderr),
                sn.assert_found(re_stderr_2, self.stderr),
                sn.assert_found(re_stderr_3, self.stderr),
                #
                sn.assert_found(re_dot_1, apt_dot_file),
                # sn.assert_found(re_dot_2, apt_dot_file),
                sn.assert_found(re_core_1, self.stdout),
            ])
        else:
            self.sanity_patterns = sn.all([
                # check the job output:
                sn.assert_found(r'UpdateSmoothingLength: \S+s', self.stdout),
                # check the tool output:
                sn.assert_found(re_slm_1, ldd_rpt),
                sn.assert_found(re_slm_2, cfg_rpt),
                sn.assert_found(re_epr_ini1, cfg_rpt),
                sn.assert_found(re_epr_cfg1, cfg_rpt),
                sn.assert_found(re_epr_cfg2, cfg_rpt),
                sn.assert_found(re_hosts_1, cfg_rpt),
                #
                sn.assert_not_found(re_ver_1, version_rpt),
                sn.assert_not_found(re_ver_2, version_rpt),
                sn.assert_not_found(re_ver_3, version_rpt),
                sn.assert_not_found(re_ver_4, version_rpt),
                sn.assert_not_found(re_ver_5, version_rpt),
                sn.assert_not_found(re_which_1, which_rpt),
                #
                sn.assert_found(re_stderr_1, self.stderr),
                sn.assert_found(re_stderr_2, self.stderr),
                sn.assert_found(re_stderr_3, self.stderr),
                #
                sn.assert_found(re_dot_1, apt_dot_file),
                # sn.assert_found(re_dot_2, apt_dot_file),
                sn.assert_found(re_core_1, self.stdout),
            ])
        # }}}

        # {{{ performance
        # see common/sphexa/hooks.py
        # }}}

    # {{{ hooks
    # {{{ set_crash
    @run_before('compile')
    def set_crash(self):
        # line81: MPI_Allreduce(...)
        source_file = 'include/sph/totalEnergy.hpp'
        insert_abort = (
            r'"/MPI_Allreduce(MPI_IN_PLACE, &einttmp, 1, MPI_DOUBLE, MPI_SUM, '
            r'MPI_COMM_WORLD);/a'
            r'int mpirank; MPI_Comm_rank(MPI_COMM_WORLD, &mpirank);'
            # r'std::cout << \"#cscs: \" << mpirank << std::endl;'
            r'if (mpirank == 1 && d.iteration == 0) '
            r'{ MPI_Abort(MPI_COMM_WORLD, 0); }"'
        )
        self.prebuild_cmds += [
            # --- make the code crash:
            f'sed -i {insert_abort} {source_file}',
        ]
    # }}}

    # {{{ get_core_filename
# todo    @run_before('sanity')
# todo    def get_core_filename(self):
# todo        '''
# todo        Retrieving core filenames for postprocessing with gdb:
# todo        .. code-block:: none
# todo           Forcing core dumps of ranks 21, 0
# todo           core.atp.1010894.0.8826
# todo           core.atp.1010894.21.8847
# todo        '''
# todo        # Each core file is named core.atp.apid.rank on dom ok but eiger:
# todo        #   core.atp.717.0.0.155799
# todo        #   core.atp.717.0.1.155800
# todo        #            jid.?.rk.pid?
# todo        self.core = sn.extractsingle(
# todo            # Producing core dumps for ranks 1
# todo            r'^Forcing core dumps of ranks (?P<corefile>\d+),',
# todo            self.stdout, 'corefile', str)
    # }}}
    # }}}
# }}}
