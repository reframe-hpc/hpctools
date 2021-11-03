import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class np_max_test(rfm.RunOnlyRegressionTest):
    omp_threads = parameter([12])
    # mpi_rks = parameter([1, 2])
    np_per_c = parameter([
        1.8e6,
        2.0e6, 2.2e6, 2.4e6, 2.6e6, 2.8e6,
        3.0e6, 3.2e6, 3.4e6, 3.6e6, 3.8e6,
        4.0e6, 4.2e6, 4.4e6, 4.6e6, 4.8e6,
        5.0e6, 5.2e6, 5.4e6, 5.6e6, 5.8e6,
        6.0e6, 6.2e6, 6.4e6, 6.6e6,  # oom: 6.8e6,
    ])
    mpi_rks = parameter([1])
    # np_per_c = parameter([1e6])
    steps = variable(str, value='0')

    valid_systems = ['*']
    valid_prog_environs = ['*']
    modules = ['cdt-cuda/21.05', 'cudatoolkit/11.2.0_3.39-2.1__gf93aa1c']
    sourcesdir = None
    prerun_cmds = ['module list']
    postrun_cmds = ['sleep 5']  # give jobreport a chance

    # Number of cores for each system
    cores = variable(dict, value={
        'daint:gpu': 12,
    })

    @run_before('run')
    def set_cubeside(self):
        phys_core_per_node = self.cores.get(self.current_partition.fullname, 1)
        # total_np = (phys_core_per_node * self.np_per_c)
        total_np = (phys_core_per_node * self.mpi_rks * self.np_per_c)
        self.cubeside = int(pow(total_np, 1 / 3))
        self.executable = \
            '$SCRATCH/SPH-EXA_mini-app.git/JG/src/sedov/sedov-cuda'
        self.executable_opts += [f"-n {self.cubeside}", f"-s {self.steps}"]

    @run_before('run')
    def set_num_threads(self):
        # num_threads = self.cores.get(self.current_partition.fullname, 1)
        # self.num_cpus_per_task = num_threads
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = self.omp_threads
        self.variables = {
            'OMP_NUM_THREADS': str(self.omp_threads),
            # 'OMP_PLACES': 'cores'
        }

    @sanity_function
    def check_execution(self):
        regex = r'Total execution time of \d+ iterations of \S+'
        return sn.assert_found(regex, self.stdout)

    @performance_function('')
    def nsteps(self):
        regex = r'# Total execution time of (\d+) iterations of \S+:'
        return sn.extractsingle(regex, self.stdout, 1, int)

    @performance_function('')
    def n_cubeside(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        n_particles = sn.extractsingle(regex, self.stdout, 1, int)
        return int(pow(sn.evaluate(n_particles), 1/3))

    @performance_function('')
    def np_per_cnode(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        n_particles = sn.extractsingle(regex, self.stdout, 1, int)
        return int(sn.evaluate(n_particles) / self.mpi_rks)

    @performance_function('')
    def nparticles(self):
        regex = r'Domain synchronized, nLocalParticles (\d+)'
        return sn.extractsingle(regex, self.stdout, 1, int)
        # n_particles = \
        # sn.evaluate(sn.extractsingle(regex, self.stdout, 1, int))
        # return f'{n_particles:.1E}'
        # the value extracted for performance variable
        # 'daint:gpu:nparticles' is not a number: 1.2E+07
        # return np.format_float_scientific(n_particles, precision=2,
        #                                   exp_digits=1)

    @performance_function('s')
    def elapsed(self):
        regex = r'# Total execution time of \d+ iterations of \S+: (\S+)s'
        return sn.extractsingle(regex, self.stdout, 1, float)

    @performance_function('MiB')
    def max_gpu_memory(self):
        #    Node name       Usage      Max mem Execution time
        # ------------ ----------- ------------ --------------
        #     nid06681        38 %     2749 MiB       00:00:06
        regex = r'^\s+nid\S+\s+\d+\s+%\s+(\d+)\s+MiB.*:'
        return sn.max(sn.extractall(regex, self.stdout, 1, int))
