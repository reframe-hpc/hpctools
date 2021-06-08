# Copyrigh 2019-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.launchers import LauncherWrapper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
import sphexa.hooks as hooks


# {{{ class Papi_Check
@rfm.simple_test
class SphExa_Papi_Check(rfm.RegressionTest, hooks.setup_pe, hooks.setup_code):
    steps = parameter([0])
    compute_node = parameter([1])
    np_per_c = parameter([1e4])

    def __init__(self):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = [
            'PrgEnv-gnu', 'PrgEnv-intel', 'PrgEnv-pgi', 'PrgEnv-cray',
            'PrgEnv-aocc', 'cpeAMD', 'cpeCray', 'cpeGNU', 'cpeIntel']
        self.valid_systems = [
            'dom:mc', 'dom:gpu', 'daint:mc', 'daint:gpu',
            'eiger:mc', 'pilatus:mc'
        ]
        self.modules = ['papi']
        self.tool = 'papi_version'
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'cpu', 'craype'}
        # }}}

        # {{{ run
        self.testname = 'sedov'
        self.time_limit = '10m'
        self.executable = './mpi+omp'
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.prebuild_cmds += [
            # 'module list', 'srun --version',
            f'{self.tool} &> {self.version_rpt}',
            f'which {self.tool} &> {self.which_rpt}',
        ]
        # }}}

    # {{{ hooks
    @rfm.run_before('sanity')
    def set_sanity(self):
        reference_hwinfo = {
            # bwl: Intel(R) Xeon(R) CPU E5-2695 v4 @ 2.10GHz (vendor 1)
            'dom:mc': 36,
            'daint:mc': 36,
            # hwl: Intel(R) Xeon(R) CPU E5-2690 v3 @ 2.60GHz (vendor 1)
            'dom:gpu': 12,
            'daint:gpu': 12,
            # AMD EPYC 7742 64-Core Processor (vendor 2)
            'eiger:mc': 128,
            'pilatus:mc': 128,
        }
        cp = self.current_partition.fullname
        regex = r' physical_cores\s+\|\s*(?P<cores>\d+)'
        phy_cores = sn.extractsingle(regex, self.stdout, 'cores', int)
        self.sanity_patterns = sn.all([
            # check the tool output:
            sn.assert_found(r'PAPI Version: \S+', self.version_rpt),
            # check the code output:
            sn.assert_eq(phy_cores, reference_hwinfo[cp]),
        ])


    def papi_patch_src(self, patchfile):
        # {{{ # f-string expression part cannot include '#' or a backslash
        sed_str = """
diff -Naur include.ori/utils.hpp include/utils.hpp
--- include.ori/utils.hpp	2021-06-08 14:19:35.414636000 +0200
+++ include/utils.hpp	2021-06-08 15:27:02.159354000 +0200
@@ -3,12 +3,75 @@
 namespace sphexa
 {

+#ifdef USE_MPI
+void papiInfo()
+{
+    // * https://bitbucket.org/icl/papi/src/master/LICENSE.txt
+    // * papi.git/src/examples/PAPI_hw_info.c (modified by jgphpc)
+    const PAPI_hw_info_t *hwinfo = NULL;
+    int retval;
+    if((retval = PAPI_library_init(PAPI_VER_CURRENT)) != PAPI_VER_CURRENT )
+    {
+        printf("Library initialization error! \\n");
+        exit(1);
+    }
+
+    /* Get hardware info*/
+    if ((hwinfo = PAPI_get_hardware_info()) == NULL)
+    {
+        printf("PAPI_get_hardware_info error! \\n");
+        exit(1);
+    }
+    int sockets_per_cnode = hwinfo->sockets; // 2
+    int numa_regions_per_cnode = hwinfo->nnodes; // 8
+    int numa_regions_per_socket = numa_regions_per_cnode / hwinfo->sockets;
+    int smt_threads_per_core = hwinfo->threads; // 2
+    int physical_cores_per_socket = hwinfo->cores; // 64
+    int physical_cores_per_cnode = physical_cores_per_socket * \\
+    sockets_per_cnode; // 128
+    int physical_cores_per_numa_region = physical_cores_per_cnode / \\
+    numa_regions_per_cnode; // 16
+    int logical_cores_per_socket = physical_cores_per_socket * \\
+    smt_threads_per_core;
+    int logical_cores_per_numa_region = hwinfo->ncpu ; // 32
+    int logical_cores = hwinfo->totalcpus;
+    //
+    printf("# --- %s (vendor %d)\\n", hwinfo->model_string, hwinfo->vendor);
+    printf("# --------------- cnode socket numa    physical logical\\n");
+    printf("# ---------------              region  core     core\\n");
+    //
+    printf("# cnode           |  1| |   -| |   -|  |  -|    |  -|\\n");
+    //
+    printf("# sockets         |%3d| |   1| |   -|  |  -|    |  -|\\n", \\
+            sockets_per_cnode);
+    //
+    printf("# numa_node|reg   |%3d| | %3d| |   1|  |  -|    |  -|\\n", \\
+            numa_regions_per_cnode, \\
+            numa_regions_per_socket);
+    //
+    printf("# physical_cores  |%3d| | %3d| | %3d|  |  1|    |  -|\\n", \\
+            physical_cores_per_cnode, \\
+            physical_cores_per_socket, \\
+            physical_cores_per_numa_region);
+    //
+    printf("# logical_cores   |%3d| | %3d| | %3d|  |%3d|    |  1|\\n", \\
+            logical_cores, \\
+            logical_cores_per_socket, \\
+            logical_cores_per_numa_region, \\
+            smt_threads_per_core);
+    printf("# -------------------------------------------------- \\n");
+}
+#endif
+
 int initAndGetRankId()
 {
     int rank = 0;
 #ifdef USE_MPI
     MPI_Init(NULL, NULL);
     MPI_Comm_rank(MPI_COMM_WORLD, &rank);
+    if (rank == 0) {
+        papiInfo();
+    }
 #endif
     return rank;
 }
"""
        # }}}
        try:
            f = open(patchfile, "w")
            f.write(sed_str)
            f.close()
            return patchfile
        except Exception as e:
            sys.stderr.write(f'papi_patch_src failed!: {patchfile} {e}')
            return None

    @rfm.run_before('compile')
    def papi_patch_header(self):
        sed_papi_h = (r'"s@USE_MPI@USE_MPI\n#include <papi.h>\n'
                      r'#include <stdlib.h>@"')  # include/sphexa.hpp
        patchfile = os.path.join(self.stagedir, 'papi.patch')
        res = self.papi_patch_src(patchfile)
        self.prebuild_cmds += [
            f'sed -i {sed_papi_h} include/sphexa.hpp',
            f'patch -p0 -i {patchfile}',
        ]
    # }}}
