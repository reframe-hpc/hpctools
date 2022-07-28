import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps


# gpu_unittests = [
#     'domain/test/unit_cuda/component_units_cuda'
# ]
# mpi_unittests = [
#     # 'integration_mpi/exchange_focus',
#     # 'integration_mpi/box_mpi',
#     # 'integration_mpi/focus_tree',
#     # 'integration_mpi/exchange_halos',
#     # 'integration_mpi/exchange_domain',
#     # 'integration_mpi/globaloctree',
#     # 'integration_mpi/treedomain',
#     'domain/test/integration_mpi/domain_2ranks',
#     # 'integration_mpi/domain_nranks',
# ]
# serial_unittests = [
#     # 'collision_reference/collisions_a2a_test',
#     # 'coord_samples/coordinate_test',
#     'domain/test/unit/component_units',
#     # 'unit/component_units_omp'
# ]

# TODO: MUST RUN WITH RFM_TRAP_JOB_ERRORS=1 ~/R -c reframe_unittest.py -n ci -r
_unittests = [
    # RFM_TRAP_JOB_ERRORS
    # "lsx",
    # "ls",
    "/usr/local/sbin/coord_samples/coordinate_test",
]

unittests = [
    "/usr/local/sbin/coord_samples/coordinate_test",
    "/usr/local/sbin/hydro/kernel_tests_std",
    "/usr/local/sbin/hydro/kernel_tests_ve",
    "/usr/local/sbin/integration_mpi/box_mpi",
    "/usr/local/sbin/integration_mpi/domain_2ranks",
    "/usr/local/sbin/integration_mpi/domain_nranks",
    "/usr/local/sbin/integration_mpi/exchange_domain",
    "/usr/local/sbin/integration_mpi/exchange_focus",
    "/usr/local/sbin/integration_mpi/exchange_general",
    "/usr/local/sbin/integration_mpi/exchange_halos",
    "/usr/local/sbin/integration_mpi/exchange_halos_gpu",
    "/usr/local/sbin/integration_mpi/exchange_keys",
    "/usr/local/sbin/integration_mpi/focus_transfer",
    "/usr/local/sbin/integration_mpi/focus_tree",
    "/usr/local/sbin/integration_mpi/globaloctree",
    "/usr/local/sbin/integration_mpi/treedomain",
    "/usr/local/sbin/performance/cudaNeighborsTest",
    "/usr/local/sbin/performance/hilbert_perf",
    "/usr/local/sbin/performance/hilbert_perf_gpu",
    "/usr/local/sbin/performance/octree_perf",
    "/usr/local/sbin/performance/octree_perf_gpu",
    "/usr/local/sbin/performance/peers_perf",
    "/usr/local/sbin/performance/scan_perf",
    "/usr/local/sbin/ryoanji/cpu_unit_tests/ryoanji_cpu_unit_tests",
    "/usr/local/sbin/ryoanji/global_upsweep_cpu",
    "/usr/local/sbin/ryoanji/global_upsweep_gpu",
    # "/usr/local/sbin/ryoanji/ryoanji_demo/ryoanji_demo",
    "/usr/local/sbin/ryoanji/unit_tests/ryoanji_unit_tests",
    "/usr/local/sbin/unit/component_units",
    "/usr/local/sbin/unit/component_units_omp",
    "/usr/local/sbin/unit_cuda/component_units_cuda",
]

unittests_params = {
    'lsx': "1",
    'ls': "1",
    "/usr/local/sbin/coord_samples/coordinate_test": "1",
    "/usr/local/sbin/hydro/kernel_tests_std": "1",
    "/usr/local/sbin/hydro/kernel_tests_ve": "1",
    "/usr/local/sbin/integration_mpi/box_mpi": "5",
    "/usr/local/sbin/integration_mpi/domain_2ranks": "2",
    "/usr/local/sbin/integration_mpi/domain_nranks": "5",
    "/usr/local/sbin/integration_mpi/exchange_domain": "5",
    "/usr/local/sbin/integration_mpi/exchange_focus": "2",
    "/usr/local/sbin/integration_mpi/exchange_general": "5",
    "/usr/local/sbin/integration_mpi/exchange_halos": "2",
    "/usr/local/sbin/integration_mpi/exchange_halos_gpu": "2",
    "/usr/local/sbin/integration_mpi/exchange_keys": "5",
    "/usr/local/sbin/integration_mpi/focus_transfer": "2",
    "/usr/local/sbin/integration_mpi/focus_tree": "5",
    "/usr/local/sbin/integration_mpi/globaloctree": "2",
    "/usr/local/sbin/integration_mpi/treedomain": "5",
    "/usr/local/sbin/performance/cudaNeighborsTest": "g",
    "/usr/local/sbin/performance/hilbert_perf": "1",
    "/usr/local/sbin/performance/hilbert_perf_gpu": "g",
    "/usr/local/sbin/performance/octree_perf": "1",
    "/usr/local/sbin/performance/octree_perf_gpu": "g",
    "/usr/local/sbin/performance/peers_perf": "1",
    "/usr/local/sbin/performance/scan_perf": "1",
    "/usr/local/sbin/ryoanji/cpu_unit_tests/ryoanji_cpu_unit_tests": "1",
    "/usr/local/sbin/ryoanji/global_upsweep_cpu": "5",
    "/usr/local/sbin/ryoanji/global_upsweep_gpu": "g",
    "/usr/local/sbin/ryoanji/ryoanji_demo/ryoanji_demo": "?",
    "/usr/local/sbin/ryoanji/unit_tests/ryoanji_unit_tests": "g",
    "/usr/local/sbin/unit/component_units": "1",
    "/usr/local/sbin/unit/component_units_omp": "1",
    "/usr/local/sbin/unit_cuda/component_units_cuda": "g",
}


#{{{ 2022/08: ci unittests
@rfm.simple_test
class ci_unittests(rfm.RunOnlyRegressionTest):
    # descr = 'run unittests'
    # ART=docker://art.cscs.ch/contbuild/testing/jg/sph-exa_install
    #  $ART:cuda_release_plus_gpud
    #  $ART:cuda_debug_plus_gpud
    #  $ART:cuda_release-gpud
    #  $ART:cuda_debug-gpud
    valid_systems = ['dom:gpu']
    valid_prog_environs = ['builtin']
    image = variable(str,
                     value='art.cscs.ch/contbuild/testing/jg/sph-exa_install')
    # NOTE: MUST RUN sarus/1.4.2:
    # mll sarus/1.4.2 # do not use 1.5 to pull images
    # sarus pull --login art.cscs.ch/contbuild/testing/jg/sph-exa_install:xx
    build_type = parameter(['cuda_debug-gpud', 'cuda_release-gpud',
                            'cuda_debug_plus_gpud', 'cuda_release_plus_gpud'])
    unittest = parameter(unittests)
    sourcesdir = None
    num_tasks = 1
    # num_tasks_per_node = 1
    modules = ['sarus']

    @run_before('run')
    def set_sarus(self):
        mpiflag = ''
        if unittests_params[self.unittest] in ["2", "5"]:
            mpiflag = '--mpi'
            self.num_tasks = int(unittests_params[self.unittest])

        if 'exchange_halos_gpu' in self.unittest:
            mpiflag = '--mpi'
            self.num_tasks_per_node = 1

        self.job.launcher.options = [
            'sarus', 'run', mpiflag,
            f'{self.image}:{self.build_type}',
        ]
        self.executable = self.unittest

    #{{{ sanity
    @sanity_function
    def assert_sanity(self):
        skip = [
            '/usr/local/sbin/performance/peers_perf',
            '/usr/local/sbin/performance/octree_perf_gpu',
            '/usr/local/sbin/performance/octree_perf',
            '/usr/local/sbin/performance/hilbert_perf_gpu',
            '/usr/local/sbin/performance/hilbert_perf',
            '/usr/local/sbin/performance/cudaNeighborsTest',
        ]
        if self.unittest in skip:
            return sn.all([sn.assert_not_found(r'error', self.stdout)])
        else:
            return sn.all([
                sn.assert_found(r'PASS', self.stdout),
                ])
    #}}}
#}}}


#{{{ 2022/08: cpu tests
@rfm.simple_test
class ci_cputests(rfm.RunOnlyRegressionTest):
    # ms sarus/1.4.2 # do not use 1.5 to pull images
    # sarus pull --login art.cscs.ch/contbuild/testing/jg/ \
    #                    sph-exa_install:cuda_debug-gpud
    # descr = 'run unittests'
    valid_systems = ['dom:gpu']
    valid_prog_environs = ['builtin']
    image = variable(str,
                     value='art.cscs.ch/contbuild/testing/jg/sph-exa_install')
    build_type = parameter(['cuda_debug-gpud', 'cuda_release-gpud'])
    unittest = parameter(['sedov', 'sedov --ve', 'noh'])
    sourcesdir = None
    num_tasks = 1
    # num_tasks_per_node = 1
    modules = ['sarus']

    @run_before('run')
    def set_sarus(self):
        mpiflag = '--mpi'
        hdf5path = '/usr/local/HDF_Group/HDF5/1.13.0/lib'
        self.job.launcher.options = [
            'sarus', 'run', mpiflag,
            f'{self.image}:{self.build_type}',
            'bash', '-c',
            f'"LD_LIBRARY_PATH={hdf5path}:$LD_LIBRARY_PATH ',  # note the space
            # 'MPICH_RDMA_ENABLED_CUDA=1 ',
            # 'LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcuda.so ',
            '/usr/local/bin/sphexa', '--init',
        ]
        self.executable = self.unittest
        self.executable_opts = ['-s', '1', '-n', '50', '"']
        #self.variables = {
        #    'LD_LIBRARY_PATH': ''
        #}

    #{{{ sanity
    @sanity_function
    def assert_sanity(self):
        regex1 = r'Total execution time of \d+ iterations of \S+ up to t ='
        return sn.all([
            sn.assert_found(regex1, self.stdout),
        ])
    #}}}
#}}}

    #{{{ 2022/08: gpu tests
    @rfm.simple_test
    class ci_gputests(rfm.RunOnlyRegressionTest):
        # ms sarus/1.4.2 # do not use 1.5 to pull images
        # sarus pull --login art.cscs.ch/contbuild/testing/jg/ \
        #                    sph-exa_install:cuda_debug-gpud
        # descr = 'run unittests'
        valid_systems = ['dom:gpu']
        valid_prog_environs = ['builtin']
        jfrog = 'art.cscs.ch/contbuild/testing/jg'
        image = variable(str, value=f'{jfrog}/sph-exa_install')
        # build_type = parameter(['cuda_debug-gpud'])
        build_type = parameter(['cuda_debug-gpud', 'cuda_release-gpud',
                                'cuda_debug_plus_gpud',
                                'cuda_release_plus_gpud'])
        unittest = parameter(['sedov', 'noh', 'evrard'])
        sourcesdir = None
        num_tasks = 1
        # num_tasks_per_node = 1
        modules = ['sarus']

        @run_before('run')
        def set_sarus(self):
            mpiflag = '--mpi'
            hdf5path = '/usr/local/HDF_Group/HDF5/1.13.0/lib'
            mountflag = ('--mount=type=bind,source="$PWD",'
                         'destination="/scratch"')
            self.job.launcher.options = [
                'sarus', 'run', mpiflag, mountflag,
                f'{self.image}:{self.build_type}',
                'bash', '-c',
                f'"LD_LIBRARY_PATH={hdf5path}:$LD_LIBRARY_PATH ',
                # note the space
                'MPICH_RDMA_ENABLED_CUDA=1 ',
                'LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcuda.so ',
                '/usr/local/bin/sphexa-cuda', '--init',  # NOTE: -cuda
            ]
            self.executable = self.unittest
            opts = {
                # 'sedov': '-s 200 -n 50 -w 200 --quiet;',
                'sedov': '-s 200 -n 50 -w 200 --outDir /scratch/ ',
                'noh': '-s 200 -n 50 -w 200 --outDir /scratch/ ',
                'evrard': ('--glass /usr/local/games/glass.h5 -s 10 -n 50 '
                           '-w 10 --outDir /scratch/ '),  # NOTE: no "
            }
            compare_executable = ';ln -fs /usr/local/bin/sedov_solution .;'
            compare = {
                'sedov': ('python3 /usr/local/bin/compare_solutions.py -s 200 '
                          '/scratch/dump_sedov.h5part > /scratch/sedov.rpt "'),
                'noh': ('python3 /usr/local/bin/compare_noh.py -s 200 '
                        '/scratch/dump_noh.h5part > /scratch/noh.rpt "'),
                'evrard': ('echo -e \\"Density L1 error 0.0\\nPressure L1 '
                           'error 0.0\\nVelocity L1 error 0.0\\n\\" > '
                           '/scratch/evrard.rpt "')
            }
            self.executable_opts = [
                opts[self.unittest],
                compare_executable,
                compare[self.unittest]
            ]
            self.postrun_cmds = [
                'cat *.rpt',
                '# "https://reframe-hpc.readthedocs.io/en/stable/manpage.html?'
                'highlight=RFM_TRAP_JOB_ERRORS',
            ]

        @performance_function('')
        def extract_L1(self, metric='Density'):
            if metric not in ('Density', 'Pressure', 'Velocity', 'Energy'):
                raise ValueError(f'illegal value (L1 metric={metric!r})')

            return sn.extractsingle(rf'{metric} L1 error (\S+)$',
                                    f'{self.unittest}.rpt', 1, float)

        @run_before('performance')
        def set_perf_variables(self):
            self.perf_variables = {
                'Density': self.extract_L1('Density'),
                'Pressure': self.extract_L1('Pressure'),
                'Velocity': self.extract_L1('Velocity'),
                # 'Energy': self.extract_L1('Energy'),
            }

        @run_before('performance')
        def set_reference(self):
            reference_d = {
                'sedov': {
                    'Density':  (0.138, -0.01, 0.01, ''),
                    'Pressure':  (0.902, -0.01, 0.01, ''),
                    'Velocity':  (0.915, -0.01, 0.01, ''),
                    # 'Energy':  (0., -0.05, 0.05, ''),
                },
                'noh': {
                    'Density':  (0.955, -0.01, 0.01, ''),
                    'Pressure':  (0.388, -0.01, 0.01, ''),
                    'Velocity':  (0.0384, -0.05, 0.05, ''),
                    # 'Energy':  (0.029, -0.05, 0.05, ''),
                },
                'evrard': {
                    'Density':  (0.0, -0.01, 0.01, ''),
                    'Pressure':  (0.0, -0.01, 0.01, ''),
                    'Velocity':  (0.0, -0.05, 0.05, ''),
                    # 'Energy':  (0.029, -0.05, 0.05, ''),
                },
            }
            self.reference = {'*': reference_d[self.unittest]}

        #{{{ sanity
        @sanity_function
        def assert_sanity(self):
            regex1 = r'Total execution time of \d+ iterations of \S+ up to t ='
            return sn.all([
                sn.assert_found(regex1, self.stdout),
            ])
        #}}}
    #}}}
