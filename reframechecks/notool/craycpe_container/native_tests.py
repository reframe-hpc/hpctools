# {{{ MIT License
#
# Copyright (c) 2021 CSCS, ETH Zurich
#               2021 University of Basel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# @author: jgphpc }}}
import os

import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps
from reframe.core.launchers import LauncherWrapper

# ----------------------------------------------------------------------------
# Run with: https://git.scicore.unibas.ch/j.piccinali/mirror_test.git/.gitlab/
# ~/P -c native_tests.py -p cpeGNU -r
# ----------------------------------------------------------------------------
# {{{ container images names: clang13,12,11/gnu10,9/nvhpc219+cuda114
# source_readonlydir = r'${SPHEXA_TOPDIR}'
# os.environ["SPHEXA_TOPDIR"] = os.path.join(image_path, source_readonlydir)
# image_path_storage = '/storage/shared/projects/sph-exa/sph-exa2'
# image_path_storage = '/apps/common/UES/sandbox/jgp/SPH'
# image_path_storage = '/scratch/e1000/piccinal'
image_path_storage = '/project/csstaff/piccinal/CRAYPE_CONTAINER'
# image_path = r'${SPHEXA_TOPDIR}'
image_path = '/apps/common/UES/sandbox/jgp/SPH/SPH-EXA_mini-app.git/'
source_dir = 'SPH-EXA_mini-app.git'
source_readonlydir = 'src' # image_path  # os.path.join(image_path, source_dir)
cmake_txt_in = os.path.join(source_readonlydir, source_dir, 'domain', 'test', 'CMakeLists.txt.in')
googletest_dir = 'googletest.git'
googletest_readonlydir = os.path.join(source_readonlydir, googletest_dir)
# googletest_readonlydir = os.path.join(image_path_storage, googletest_dir)
sarus_image = 'load/cray/hpe_cpe:1.4.1'
singularity_image = ['hpe_cpe_1.4.1.sif', 'debian11_clang13_mpich341.def.sif']
# debian11_clang13_mpich341.def.sif
# }}}
# {{{ test names:
path_mpi_unittests = 'builddir/domain/test/integration_mpi'
mpi_unittests_2ranks = {
    # 'domain_2ranks': path_mpi_unittests,
    # 'exchange_focus': path_mpi_unittests,
    # 'exchange_halos': path_mpi_unittests,
    # 'globaloctree': path_mpi_unittests,
}
mpi_unittests = {
    # 'treedomain': path_mpi_unittests,
    # 'focus_tree': path_mpi_unittests,
    # 'box_mpi': path_mpi_unittests,
    # 'exchange_keys': path_mpi_unittests,
    # 'exchange_domain': path_mpi_unittests,
    # 'domain_nranks': path_mpi_unittests,
}
path_perf_unittests = 'builddir/domain/test/performance'
perf_unittests = {
    # 'hilbert_perf': path_perf_unittests,
    # 'peers_perf': path_perf_unittests,
    # 'octree_perf': path_perf_unittests,
    # --- 'scan_perf': path_perf_unittests,
}
path_cpu_tests = 'builddir/src'
cpu_tests = {
    'sedov': f'{path_cpu_tests}/sedov',
    # --- 'evrard': f'{path_cpu_tests}/evrard',
}
gpu_tests = {
    # 'sedov-cuda': f'{path_cpu_tests}/sedov',
    # 'component_units_cuda': 'builddir/domain/test/unit_cuda',
}
all_tests = {
    **mpi_unittests_2ranks,
    **mpi_unittests,
    **perf_unittests,
    **cpu_tests,
    **gpu_tests}
all_tests_name = list(all_tests.keys())
# {{{ serial_unittests = [
#     # 'collision_reference/collisions_a2a_test',
#     # 'coord_samples/coordinate_test',
#     'domain/test/unit/component_units',
#     # 'unit/component_units_omp'
# builddir/domain/test/coord_samples/coordinate_test
# builddir/domain/test/unit/component_units
# builddir/domain/test/unit/component_units_omp
# ] }}}
# }}}
# cpu_archs = ['haswell']
cpu_archs = ['znver2']
# cpu_archs = ['broadwell', 'cascadelake']


# {{{ Build
@rfm.simple_test
class Build(rfm.CompileOnlyRegressionTest):
    '''Build the unittests and tests before running them'''
    # target_cpu_arch = parameter(['broadwell', 'cascadelake'])
    target_cpu_arch = parameter(cpu_archs)
    target_compiler = parameter(['clang', 'gcc'])

    # valid_systems = ['dmi:login', 'pilatus:login']
    valid_systems = ['pilatus:mc']
    valid_prog_environs = ['gnu+openmpi', 'cpeGNU', 'cpeCray']
    # valid_systems = ['pilatus:login']
    # valid_prog_environs = ['cpeGNU']
    build_system = 'CMake'
    # build_system.nvcc = None
    # {{{ fix for cmakelist:
    # postbuild_cmds = [
    #     'echo "echo x" > domain/test/integration_mpi/domain_2ranks',
    #     'chmod u+x domain/test/integration_mpi/domain_2ranks'
    # ]
    # }}}
    maintainers = ['JG']
    tags = {'gitlab'}
    modules = ['CMake']

    @run_after('init')
    def set_valid_prog_environs(self):
        if self.target_compiler == 'clang':
            self.valid_prog_environs = ['cpeCray']
        elif self.target_compiler == 'gcc':
            self.valid_prog_environs = ['cpeGNU']

    @run_before('compile')
    def set_cmake_options(self):
        self.prebuild_cmds = [
            # cmds running before cd builddir:
            'module list',  # 'which mpicxx', 'mpicxx --version',
            # f'cp -a {source_readonlydir} .',
            # f'cp -a {googletest_readonlydir} .',
            # ---
            '# {{{ sed',
            f'# --- setup path to googletest.git:',
            f'sed -i \'s@GIT_REPOSITORY@URL "{os.path.join(self.stagedir, googletest_readonlydir)}"\\n#@\' '
            f'{cmake_txt_in}',
            # ---
            f'sed -i \'s@GIT_TAG@#@\' {cmake_txt_in}',
            f'# --- {cmake_txt_in}:',
            f'cat {cmake_txt_in}',
            f'# --- turn off googletest with: echo > {cmake_txt_in}',
            f'# --- remove evrard test until fixed:',
            f'sed -i \'s@(add_subdirectory(evrard))@# @\' '
            f'{source_readonlydir}/{source_dir}/src/CMakeLists.txt',
            f'# --- remove -march=native:',
            f'sed -i \'s@set(CMAKE_CXX_FLAGS_RELEASE@# @\' '
            f'{source_readonlydir}/{source_dir}/CMakeLists.txt',
            f'# ---',
            'sed -i \'s@\(check_language(CUDA)\)@# \\1@\' '
            f'{source_readonlydir}/{source_dir}/CMakeLists.txt',
            '# }}}',
        ]
        self.build_system.builddir = 'builddir'
        # --- g++ --help=target |grep "valid arguments for -march= option"
        target_cpu_arch = f'-O2 -march={self.target_cpu_arch} -DNDEBUG'
        self.build_system.config_opts = [
            # '-DCMAKE_CXX_COMPILER=mpicxx',
            # '-DCMAKE_VERBOSE_MAKEFILE=TRUE',
            '-DCMAKE_BUILD_TYPE=Release',
            '-DBUILD_TESTING=ON',
            '-UCMAKE_CUDA_COMPILER',
            f'-DCMAKE_CXX_FLAGS_RELEASE="{target_cpu_arch}"',
            f'-S ../{source_readonlydir}/{source_dir}', '2>&1 #',
        ]
        self.build_system.max_concurrency = 10
        # TODO: self.current_partition.processor.num_cpus_per_socket
        # self.build_system.make_opts = [f'help']
        self.build_system.make_opts = [f'help {" ".join(all_tests_name)}']
        # self.build_system.make_opts = ['help all']  # ['help sedov']

    # {{{ sanity
    @sanity_function
    def sanity_check(self):
        # -- The CXX compiler identification is GNU 9.3.0
        # -- Found MPI: TRUE (found version "3.1")
        # -- Found OpenMP: TRUE (found version "4.5")
        # -- The CUDA compiler identification is NVIDIA 11.4.100
        regex1 = r'The CXX compiler identification is'
        regex2 = r'Found MPI: TRUE'
        regex3 = r'Found OpenMP: TRUE'
        regex4 = r'The CUDA compiler identification is|No CUDA support'
        return sn.all([
            sn.assert_found(regex1, self.stdout),
            sn.assert_found(regex2, self.stdout),
            sn.assert_found(regex3, self.stdout),
            sn.assert_found(regex4, self.stdout),
        ])
    # }}}
# }}}


# # {{{ Run
# @rfm.simple_test
# class Run(rfm.RunOnlyRegressionTest):
#     target_cpu_arch = parameter(cpu_archs)
#     test_executable = parameter(all_tests_name)
#     mpi_ranks = parameter([2])
#     np_per_c = parameter([8e4])
#     # mpi_ranks = parameter([1, 2])
#     # np_per_c = parameter([8e4, 1e5])
#     steps = variable(int, value=1)
# 
#     valid_prog_environs = ['gnu+openmpi', 'cpeGNU', 'cpeCray']
#     valid_systems = ['*']
#     # valid_systems = ['pilatus:mc']
# 
#     @run_after('init')
#     def set_valid_systems(self):
#         if self.target_cpu_arch == 'broadwell':
#             self.valid_systems = ['dmi:xeon']
#         elif self.target_cpu_arch == 'cascadelake':
#             self.valid_systems = ['dmi:a100']
#         elif self.target_cpu_arch == 'znver2':
#             self.valid_systems = ['pilatus:mc']
#         else:
#             print(f'unknown self.target_cpu_arch={self.target_cpu_arch}...')
# 
#     @run_after('init')
#     def set_dependencies(self):
#         # NOTE: deps will be ignored if --skip-system-check
#         dep_name = f'Build_{self.target_cpu_arch}'
#         self.depends_on(dep_name, how=udeps.fully)
# 
#     @require_deps
#     def set_executable(self):
#         self.descr = f'Running test'
#         dep_name = f'Build_{self.target_cpu_arch}'
#         stagedir = self.getdep(
#             dep_name, environ='cpeCray', part='login').stagedir
#             # dep_name, environ=self.current_environ.name, part='login').stagedir
#             # dep_name, environ='gnu+openmpi', part='login').stagedir
#         myexe_args = []
#         self.executable = os.path.join(
#             stagedir, all_tests[self.test_executable], self.test_executable)
#         # {{{ corner cases:
#         if self.test_executable in perf_unittests:
#             self.num_tasks = 1  # these tests are OpenMP threaded
#             # self.num_cpus_per_task = 10
# 
#         if self.test_executable in mpi_unittests_2ranks:
#             self.num_tasks = 2
# 
#         if self.test_executable in mpi_unittests:
#             self.num_tasks = 10
#             # TODO: self.num_tasks = \
#             # self.current_partition.processor.num_cpus_per_socket
# 
#         if 'cuda' in self.test_executable:
#             self.num_tasks = 1
#             # self.container_platform.with_cuda = True
# 
#         if 'sedov' in self.test_executable:
#             self.num_tasks = self.mpi_ranks
#             total_np = self.num_tasks * self.np_per_c
#             self.cubeside = int(pow(total_np, 1 / 3))
#             myexe_args = ['-s', f'{self.steps}', '-n', f'{self.cubeside}']
# 
#         self.executable_opts = myexe_args
#         # --- skip executables built with cuda & non gpu partition:
#         assert_1 = 'cuda' in self.test_executable
#         assert_2 = self.current_partition.name == 'xeon'
#         self.skip_if(
#             assert_1 and assert_2,
#             f'exe={self.test_executable} & part={self.current_partition.name}')
#         # }}}
# 
#     # {{{ sanity:
#     @sanity_function
#     def sanity_check(self):
#         regex_tests = {
#             'box_mpi': r'PASSED.*3 tests',
#             'domain_2ranks': r'PASSED.*6 tests.',
#             'domain_nranks': r'PASSED.*3 tests.',
#             'exchange_domain': r'PASSED.*2 tests.',
#             'exchange_focus': r'PASSED.*2 tests.',
#             'exchange_halos': r'PASSED.*1 test.',
#             'exchange_keys': r'PASSED.*1 test.',
#             'focus_tree': r'PASSED.*1 test.',
#             'globaloctree': r'PASSED.*1 test.',
#             'treedomain': r'PASSED.*1 test.',
#             #
#             'sedov': r'Total execution time of \d+ iterations',
#             'sedov-cuda': r'Total execution time of \d+ iterations',
#             #
#             'hilbert_perf': r'hilbert keys: \S+ s on CPU',
#             'octree_perf': r'octree halo discovery: \S+',
#             'peers_perf': r'find peers: \S+',
#             'scan_perf': r'parallel benchmark bandwidth: \S+ MB/s',
#         }
#         exe = self.test_executable  # .split("/")[-1]
#         return sn.assert_found(regex_tests[exe], self.stdout)
#     # }}}
# 
#     # {{{ elapsed_time:
#     ## @run_after('run')
#     @performance_function('')
#     def cubeside(self):
#         return self.cubeside
# 
#     @performance_function('s')
#     def elapsed_time(self):
#         regex = r'Total execution time of \d+ iterations of \S+: (\S+)s'
#         return sn.extractsingle(regex, self.stdout, 1, float)
# 
# #     @performance_function('')
# #     def steps(self):
# #         return int(self.steps)
#     # }}}
# # }}}


# {{{ set_mount_points
def set_mount_points():
    mount_points = [
        ('$PWD/src/valid/CPE-licfile.dat', '/opt/cray/pe/craype/2.7.9/AutoPass/Lic/CPE-licfile.dat'),
        ('$PWD/src/data', '/opt/cray/pe/craype/2.7.9/AutoPass/data'),
    ]
    return mount_points
# }}}


# {{{ set_prerun
def set_prerun(target_compiler):
    cpe_dict = {'clang': 'cpe-cray cce', 'gcc': 'cpe-gnu gcc/10.2.0'}
    pe_prerun = (
        # --- cat /root/.bashenv:
        # source /usr/local/Modules/init/bash
        # module load cpe-cray cce craype craype-x86-skylake craype-network-ofi cray-mpich cray-libsci
        'module purge; unset MODULEPATH; source /usr/local/Modules/init/bash; '
        'MODULEPATH=/opt/cray/pe/perftools/default/modulefiles:/usr/local/Modules/modulefiles:/opt/cray/pe/cpe-prgenv/7.0.0/modules:/opt/cray/pe/modulefiles:/opt/cray/pe/craype-targets/1.4.0/modulefiles:/opt/modulefiles:/opt/cray/modulefiles; '
        f'module load {cpe_dict[target_compiler]} craype craype-x86-rome '
        'craype-network-ofi cray-mpich cray-libsci xpmem; '
        # FIXME: xpmem
        'module rm xpmem; '
        'export PKG_CONFIG_PATH=/opt/cray/pe/dsmml/default/dsmml/lib/pkgconfig:$PKG_CONFIG_PATH; '
        'CC --version; '
        # export LD_LIBRARY_PATH=$GCC_PATH/snos/lib64:`pkg-config --variable=prefix libfabric`/lib64:$LD_LIBRARY_PATH;
    )
    return pe_prerun
 # }}}


# {{{ BuildContainer
@rfm.simple_test
class BuildContainer(rfm.RunOnlyRegressionTest):
    '''Build the unittests and tests before running them'''
    # target_cpu_arch = parameter(['broadwell', 'cascadelake'])
    target_cpu_arch = parameter(cpu_archs)
    target_compiler = parameter(['clang', 'gcc'])
    # platform = parameter(['Sarus', 'Singularity'])
    # --- if Singularity fails to build, use Sarus for building:
    # platform = parameter(['Sarus'])
    # image = parameter(['load/cray/hpe_cpe:1.4.1'])
    # --- else:
    platform = parameter(['Singularity'])
    image = parameter(singularity_image)

    valid_systems = ['pilatus:mc']
    valid_prog_environs = ['cpeGNU', 'cpeCray']
    # valid_prog_environs = ['builtin']
    # build_system = 'CMake'
    # build_system.nvcc = None
    # {{{ fix for cmakelist:
    prerun_cmds = [
        # cmds running before cd builddir:
        'module rm singularity',
        # ----
        # FATAL:   container creation failed: hook function for tag layer returns
        # error: failed to create /opt/cray/pe/craype/2.7.9/AutoPass directory:
        # mkdir /opt/cray/pe/craype/2.7.9/AutoPass: permission denied
        # ----
        'module list',  # 'which mpicxx', 'mpicxx --version',
        # f'cp -a {source_readonlydir} .',
        # f'cp -a {googletest_readonlydir} .',
        # ---
#         '# {{{ sed',
#         f'# --- setup path to googletest.git:',
#         f'sed -i \'s@GIT_REPOSITORY@URL "{googletest_readonlydir}"\\n#@\' '
#         f'{cmake_txt_in}',
#         # ---
#         f'sed -i \'s@GIT_TAG@#@\' {cmake_txt_in}',
#         f'# --- {cmake_txt_in}:',
#         f'cat {cmake_txt_in}',
#         f'# --- turn off googletest with: echo > {cmake_txt_in}',
#         f'# --- remove evrard test until fixed:',
#         f'sed -i \'s@(add_subdirectory(evrard))@# @\' '
#         f'{source_dir}/src/CMakeLists.txt',
#         f'# --- remove -march=native:',
#         f'sed -i \'s@set(CMAKE_CXX_FLAGS_RELEASE@# @\' '
#         f'{source_dir}/CMakeLists.txt',
#         f'# ---',
#         'sed -i \'s@\(check_language(CUDA)\)@# \\1@\' '
#         f'{source_dir}/CMakeLists.txt',
#         '# }}}',
    ]
    # postbuild_cmds = [
    #     'echo "echo x" > domain/test/integration_mpi/domain_2ranks',
    #     'chmod u+x domain/test/integration_mpi/domain_2ranks'
    # ]
    # }}}
    maintainers = ['JG']
    tags = {'gitlab'}

    # {{{ skip
    @run_before('run')
    def set_skip(self):
        # skip "clang & cpeGNU":
        assert_1 = self.target_compiler == 'clang'
        assert_2 = self.current_environ.name == 'cpeGNU'
        self.skip_if(
            assert_1 and assert_2,
            f'target_compiler={self.target_compiler} & environ={self.current_environ.name}')
        # skip "clang & cpeGNU":
        assert_1 = self.target_compiler == 'gcc'
        assert_2 = self.current_environ.name == 'cpeCray'
        self.skip_if(
            assert_1 and assert_2,
            f'target_compiler={self.target_compiler} & environ={self.current_environ.name}')
    # }}}

    @run_before('run')
    def set_container_variables(self):
        # > sarus images
        # REPOSITORY          TAG          DIGEST
        # load/cray/hpe_cpe   1.4.1        019e2ece3d56
        self.descr = f'Run building script with {self.platform}'
        image_prefix = 'docker://' if self.platform == 'Singularity' else ''
        self.container_platform = self.platform
        # sarus: self.container_platform.image = f'{self.image}'
        self.container_platform.image = os.path.join(image_path_storage, self.image)
        # self.container_platform.image = os.path.join(image_path, self.image)
        # container_path = '/usr/local/games/sph'
        self.container_platform.mount_points = [
            # /rfm_workdir
            # ('/etc/libibverbs.d', '/etc/libibverbs.d'),
            ('/var/spool/slurmd', '/var/spool/slurmd'),
            ('/var/lib/hugetlbfs', '/var/lib/hugetlbfs'),
            ('/dev/infiniband', '/dev/infiniband'),
            # ('$PWD/src', '/usr/local/games/')
            # + /rfm_workdir
            # (source_topdir, f'{container_path}/'),
            # ('${SPHEXA_TOPDIR}', f'{container_path}/'),
            # ('/path/to/host/dir1', '/path/to/container/mount_point1'),
            # -S <path-to-source> = Explicitly specify a source directory.
            # -B <path-to-build>  = Explicitly specify a build directory.
        ]
        # self.container_platform.with_mpi = True
        pe_prerun = ''
        if 'hpe' in self.image:
            # cpe_dict = {'clang': 'cpe-cray cce', 'gcc': 'cpe-gnu gcc/10.2.0'}
#             self.container_platform.mount_points.append(
#                 ('$PWD/src/valid/CPE-licfile.dat', '/opt/cray/pe/craype/2.7.9/AutoPass/Lic/CPE-licfile.dat'),
#             )
#             self.container_platform.mount_points.append(
#                 ('$PWD/src/data', '/opt/cray/pe/craype/2.7.9/AutoPass/data'),
#             )
            self.container_platform.mount_points.extend(set_mount_points())
            pe_prerun = set_prerun(self.target_compiler)

        self.container_platform.command = (
            f'bash -c "{pe_prerun} /rfm_workdir/src/0.sh {" ".join(all_tests_name)}"'
            # "bash -c 'cat /etc/os-release | tee /rfm_workdir/release.txt'"
        )
# {{{
#     @run_before('compile')
#     def set_cmake_options(self):
#         self.build_system.builddir = 'builddir'
#         # --- g++ --help=target |grep "valid arguments for -march= option"
#         target_cpu_arch = f'-O2 -march={self.target_cpu_arch} -DNDEBUG'
#         self.build_system.config_opts = [
#             # '-DCMAKE_CXX_COMPILER=mpicxx',
#             # '-DCMAKE_VERBOSE_MAKEFILE=TRUE',
#             '-DCMAKE_BUILD_TYPE=Release',
#             '-DBUILD_TESTING=ON',
#             '-UCMAKE_CUDA_COMPILER',
#             f'-DCMAKE_CXX_FLAGS_RELEASE="{target_cpu_arch}"',
#             f'-S ../{source_dir}', '2>&1 #',
#         ]
#         self.build_system.max_concurrency = 21
#         # TODO: self.current_partition.processor.num_cpus_per_socket
#         # self.build_system.make_opts = [f'help']
#         self.build_system.make_opts = [f'help {" ".join(all_tests_name)}']
#         # self.build_system.make_opts = ['help all']  # ['help sedov']
# }}}

    # {{{ sanity
    @sanity_function
    def sanity_check(self):
        # -- The CXX compiler identification is GNU 9.3.0
        # -- Found MPI: TRUE (found version "3.1")
        # -- Found OpenMP: TRUE (found version "4.5")
        # -- The CUDA compiler identification is NVIDIA 11.4.100
        regex1 = r'The CXX compiler identification is'
        regex2 = r'Found MPI: TRUE'
        regex3 = r'Found OpenMP: TRUE'
        regex4 = r'The CUDA compiler identification is|No CUDA support'
        return sn.all([
            sn.assert_found(regex1, self.stdout),
            sn.assert_found(regex2, self.stdout),
            sn.assert_found(regex3, self.stdout),
            sn.assert_found(regex4, self.stdout),
        ])
    # }}}
# }}}


# {{{ RunContainer
@rfm.simple_test
class RunContainer(rfm.RunOnlyRegressionTest):
    target_cpu_arch = parameter(cpu_archs)
    target_compiler = parameter(['clang', 'gcc'])
    platform = parameter(['Singularity'])
    image = parameter(singularity_image)
    # image = parameter(['hpe_cpe_1.4.1.sif'])
    # image = parameter(['load/cray/hpe_cpe:1.4.1'])
    test_executable = parameter(all_tests_name)
    # mpi_ranks = parameter([1, 2, 4, 8, 16, 32, 64, 96])
    mpi_ranks = parameter([1, 2, 4, 8, 16, 32])
    openmp_threads = parameter([64])
    np_per_c = parameter([1e5])
    # np_per_c = parameter([6e4, 8e4])
    # mpi_ranks = parameter([1, 2])
    # np_per_c = parameter([8e4, 1e5])
    steps = variable(int, value=9)

    sourcesdir = None
    # valid_prog_environs = ['builtin']
    valid_systems = ['pilatus:mc']
    valid_prog_environs = ['cpeGNU', 'cpeCray']
    # valid_systems = ['*']
# {{{ old
#     prerun_cmds = [
#         'ls -l $GCC_PATH/snos/lib64',
#         'echo GCC_PATH=$GCC_PATH',
#         'export LD_LIBRARY_PATH=$GCC_PATH/snos/lib64:`pkg-config --variable=prefix libfabric`/lib64:$LD_LIBRARY_PATH',
#     ]
#     variables = {
#         'LD_LIBRARY_PATH': '`echo $GCC_PATH`/snos/lib64:`pkg-config --variable=prefix libfabric`/lib64:$LD_LIBRARY_PATH',
#         # export LD_LIBRARY_PATH=/opt/cray/libfabric/1.11.0.3.59/lib64:$LD_LIBRARY_PATH
#         # export LD_LIBRARY_PATH=$GCC_PATH/snos/lib64:$LD_LIBRARY_PATH
#         # export LD_LIBRARY_PATH=/opt/gcc/10.2.0/snos/lib64:$LD_LIBRARY_PATH
#     }

#     @run_after('init')
#     def set_valid_systems(self):
#         if self.target_cpu_arch == 'broadwell':
#             self.valid_systems = ['dmi:xeon']
#         elif self.target_cpu_arch == 'cascadelake':
#             self.valid_systems = ['dmi:a100']
#         elif self.target_cpu_arch == 'znver2':
#             self.valid_systems = ['pilatus:mc']
#         else:
#             print(f'unknown self.target_cpu_arch={self.target_cpu_arch}...')
# }}}
    maintainers = ['JG']

    @run_before('setup')
    def set_valid_prog_environs(self):
        if self.target_compiler == 'clang':
            self.pe = 'cpeCray'
        elif self.target_compiler == 'gcc':
            self.pe = 'cpeGNU'

        self.valid_prog_environs = [self.pe]

    @run_before('run')
    def set_container_variables(self):
        # > sarus images
        # REPOSITORY          TAG          DIGEST
        # load/cray/hpe_cpe   1.4.1        019e2ece3d56
        self.descr = f'Run job script with {self.platform}'
        image_prefix = 'docker://' if self.platform == 'Singularity' else ''
        self.container_platform = self.platform
        self.container_platform.image = os.path.join(image_path_storage, self.image)
        # self.container_platform.image = f'{self.image}'
        self.container_platform.mount_points = [
            # /rfm_workdir
            # ('/etc/libibverbs.d', '/etc/libibverbs.d'),
            ('/var/spool/slurmd', '/var/spool/slurmd'),
            ('/var/lib/hugetlbfs', '/var/lib/hugetlbfs'),
            ('/dev/infiniband', '/dev/infiniband'),
        ]
        # self.container_platform.mount_points = [
            # sarus only: ('/var/spool/slurmd', '/var/spool/slurmd'),
            # sarus only: ('/var/lib/hugetlbfs', '/var/lib/hugetlbfs'),
            # sarus only: ('/dev/infiniband', '/dev/infiniband'),
            # build onlly: ('$PWD/src/valid/CPE-licfile.dat', '/opt/cray/pe/craype/2.7.9/AutoPass/Lic/CPE-licfile.dat'),
            # + $PWD:/rfm_workdir
        # ]
        # self.container_platform.with_mpi = True
    # {{{ deps
    @run_after('init')
    def set_dependencies(self):
        # NOTE: deps will be ignored if --skip-system-check
        # --- If Singularity fails, build with Sarus:
        # convert_image_name = sarus_image.replace(":", "_").replace(".", "_").replace("/", "_")
        # dep_name = f'BuildContainer_{self.target_cpu_arch}_Sarus_{convert_image_name}'
        # --- build with Singularity:
        convert_image_name = self.image.replace(":", "_").replace(".", "_").replace("/", "_")
        dep_name = f'BuildContainer_{self.target_cpu_arch}_{self.target_compiler}_{self.platform}_{convert_image_name}'
# BuildContainer_znver2_clang/gcc_Singularity_hpe_cpe_1_4_1_sif
# BuildContainer_znver2_clang/gcc_Singularity_debian11_clang13_mpich341_def_sif
# Build_znver2_clang/gcc
        # dep_name = f'BuildContainer_{self.target_cpu_arch}_{self.platform}_{convert_image_name}'
        self.depends_on(dep_name)
        # self.depends_on(dep_name, how=udeps.fully)
        # BuildContainer_znver2_Sarus_load_cray_hpe_cpe_1_4_1
        #
        dep_name_native = f'Build_{self.target_cpu_arch}_{self.target_compiler}'
        self.depends_on(dep_name_native)
        # self.depends_on(dep_name_native, how=udeps.fully)

    @require_deps
    def set_executable(self):
        self.descr = f'Running test'
        # --- If Singularity fails, build with Sarus:
        # dep_name = f'BuildContainer_{self.target_cpu_arch}_Sarus_{convert_image_name}'
        # convert_image_name = sarus_image.replace(":", "_").replace(".", "_").replace("/", "_")
        # --- build with Singularity:
        convert_image_name = self.image.replace(":", "_").replace(".", "_").replace("/", "_")
        dep_name = f'BuildContainer_{self.target_cpu_arch}_{self.target_compiler}_{self.platform}_{convert_image_name}'
        # dep_name = f'BuildContainer_{self.target_cpu_arch}_{self.platform}_{convert_image_name}'
        # stagedir = self.getdep(dep_name, environ='builtin', part='mc').stagedir
        # stagedir = self.getdep(dep_name, environ='cpeGNU', part='mc').stagedir
        stagedir = self.getdep(dep_name, environ=self.pe, part='mc').stagedir
        self.executable_container = os.path.join(
            stagedir, all_tests[self.test_executable], self.test_executable)
        #
        dep_name_native = f'Build_{self.target_cpu_arch}_{self.target_compiler}'
        # stagedir_native = self.getdep(dep_name_native, environ='cpeGNU', part='login').stagedir
        # stagedir_native = self.getdep(dep_name_native, environ='cpeGNU', part='mc').stagedir
        stagedir_native = self.getdep(dep_name_native, environ=self.pe, part='mc').stagedir
        self.executable_native = os.path.join(
            stagedir_native, all_tests[self.test_executable], self.test_executable)
        self.licensefile = os.path.join(
            stagedir_native, 'src/valid/CPE-licfile.dat'
        )
    # }}}

    # {{{ runtime arguments:
    @run_before('run')
    def set_container_command(self):
        self.prerun_cmds = [
            '# -------------------------------------------------------------',
            'module rm singularity',
            f'cp {self.executable_container} container.exe',
            f'cp {self.executable_native} native.exe',
            'mkdir -p src/valid src/data',
            f'cp {self.licensefile} src/valid/',
        ]
        myexe_args = []
        # {{{ corner cases:
        if self.test_executable in perf_unittests:
            self.num_tasks = 1  # these tests are OpenMP threaded
            # self.num_cpus_per_task = 10

        if self.test_executable in mpi_unittests_2ranks:
            self.num_tasks = 2

        if self.test_executable in mpi_unittests:
            self.num_tasks = 10
            # TODO: self.num_tasks = \
            # self.current_partition.processor.num_cpus_per_socket

        if 'cuda' in self.test_executable:
            self.num_tasks = 1
            # self.container_platform.with_cuda = True

        if 'sedov' in self.test_executable:
            self.num_tasks = self.mpi_ranks
            self.num_tasks_per_node = 1
            total_np = self.num_tasks * self.np_per_c * self.openmp_threads
            self.cubeside = int(pow(total_np, 1 / 3))
            myexe_args = ['-s', f'{self.steps}', '-n', f'{self.cubeside}']
        else:
            self.cubeside = 0

        self.executable_opts = myexe_args
        # --- skip executables built with cuda & non gpu partition:
        assert_1 = 'cuda' in self.test_executable
        assert_2 = self.current_partition.name == 'xeon'
        self.skip_if(
            assert_1 and assert_2,
            f'exe={self.test_executable} & part={self.current_partition.name}')
        # {{{ FIXME: not needed here: skipped due to skipped dependencies
#         # skip "clang & cpeGNU":
#         assert_1 = self.target_compiler == 'clang'
#         assert_2 = self.current_environ.name == 'cpeGNU'
#         self.skip_if(
#             assert_1 and assert_2,
#             f'target_compiler={self.target_compiler} & environ={self.current_environ.name}')
#         # skip "clang & cpeGNU":
#         assert_1 = self.target_compiler == 'gcc'
#         assert_2 = self.current_environ.name == 'cpeCray'
#         self.skip_if(
#             assert_1 and assert_2,
#             f'target_compiler={self.target_compiler} & environ={self.current_environ.name}')
        # }}}
        # }}}
        self.prerun_cmds += [
            '# -------------------------------------------------------------',
            f'export OMP_NUM_THREADS={self.openmp_threads}',
            # f'srun ./native.exe {myexe_args_str} &> rpt.native',
            # 'echo "Total execution time of 10 iterations of xx: 1.0s" > rpt.native',
            # 'echo "Total execution time of 10 iterations of xx: 2.0s" > rpt.container',
            # f'{self.job.launcher} ./native.exe {myexe_args}',
            '# -------------------------------------------------------------',
        ]
        myexe_args_str = " ".join(myexe_args)
        pe_prerun = ''
        if 'hpe' in self.image:
            self.prerun_cmds += [
                f'srun ./native.exe {myexe_args_str} &> rpt.native',
            ]
            self.container_platform.mount_points.extend(set_mount_points())
            pe_prerun = set_prerun(self.target_compiler)
        elif 'debian' in self.image:
            self.job.launcher.options = ['--mpi=pmi2']
            # launch job with: srun --mpi=pmi2 ...
            # FIXME: try with cray-mpich-abi

        self.container_platform.command = (
            f"bash -c '{pe_prerun} OMP_NUM_THREADS={self.openmp_threads} ./container.exe {myexe_args_str}'"
            # f"bash -c '{self.prerun} /rfm_workdir/container.exe'"
            # f'/rfm_workdir/src/0.sh {" ".join(all_tests_name)}'
            # "bash -c 'cat /etc/os-release | tee /rfm_workdir/release.txt'"
        )
        # self.job.launcher.options += [tool_scriptname]
    # }}}

    # {{{ sanity:
    @sanity_function
    def sanity_check(self):
        regex_tests = {
            'box_mpi': r'PASSED.*3 tests',
            'domain_2ranks': r'PASSED.*6 tests.',
            'domain_nranks': r'PASSED.*3 tests.',
            'exchange_domain': r'PASSED.*2 tests.',
            'exchange_focus': r'PASSED.*2 tests.',
            'exchange_halos': r'PASSED.*1 test.',
            'exchange_keys': r'PASSED.*1 test.',
            'focus_tree': r'PASSED.*1 test.',
            'globaloctree': r'PASSED.*1 test.',
            'treedomain': r'PASSED.*1 test.',
            #
            'sedov': r'Total execution time of \d+ iterations',
            'sedov-cuda': r'Total execution time of \d+ iterations',
            #
            'hilbert_perf': r'hilbert keys: \S+ s on CPU',
            'octree_perf': r'octree halo discovery: \S+',
            'peers_perf': r'find peers: \S+',
            'scan_perf': r'parallel benchmark bandwidth: \S+ MB/s',
        }
        exe = self.test_executable  # .split("/")[-1]
        return sn.assert_found(regex_tests[exe], self.stdout)
    # }}}

    # {{{ elapsed_time:
    ## @run_after('run')
    @performance_function('')
    def cubeside(self):
        return self.cubeside

    @performance_function('s')
    def elapsed_time_container(self):
        regex = r'Total execution time of \d+ iterations of \S+: (\S+)s'
        # rpt = os.path.join(self.stagedir, 'rpt.container')
        return sn.extractsingle(regex, self.stdout, 1, float)

    @performance_function('s')
    def elapsed_time_native(self):
        if 'hpe' in self.image:
            regex = r'Total execution time of \d+ iterations of \S+: (\S+)s'
            rpt = os.path.join(self.stagedir, 'rpt.native')
            return sn.extractsingle(regex, rpt, 1, float)
        else:
            return 0

    @performance_function('')
    def elapsed_steps(self):
        regex = r'Total execution time of (\d+) iterations of'
        # rpt = os.path.join(self.stagedir, 'rpt.container')
        return sn.extractsingle(regex, self.stdout, 1, int)
    # }}}
# }}}
