# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                '../common')))  # noqa: E402
# import sphexa.sanity as sphs


@rfm.parameterized_test(*[[mpitask, cubesize, steps]
                          for mpitask in [1]
                          for cubesize in [30]
                          for steps in [0]
                          ])
class SphExaCudaGdbCheck(rfm.RegressionTest):
    # {{{
    '''
    This class runs the test code with cuda-gdb,
    3 parameters can be set for simulation:

    :arg mpitask: number of mpi tasks,
    :arg cubesize: size of the cube in the 3D square patch test,
    :arg steps: number of simulation steps.
    '''
    # }}}

    def __init__(self, mpitask, cubesize, steps):
        # {{{ pe
        self.descr = 'Tool validation'
        self.valid_prog_environs = ['PrgEnv-gnu']
        # self.valid_systems = ['daint:gpu', 'dom:gpu']
        self.valid_systems = ['*']
        self.maintainers = ['JG']
        self.tags = {'sph', 'hpctools', 'debug', 'gpu'}
# }}}

# {{{ compile
        self.testname = 'sqpatch'
        self.prebuild_cmd = ['module rm xalt']
        self.modules = ['craype-accel-nvidia60']
        self.prgenv_flags = {
            'PrgEnv-gnu': ['-std=c++14', '-g', '-O0', '-DNDEBUG'],
            # Makefile adds: '-DUSE_MPI', '-DUSE_CUDA'],
        }
        self.prgenv_gpuflags = {
            # P100 = sm_60
            'PrgEnv-gnu': ['-std=c++14', '-rdc=true', '-arch=sm_60', '-g',
                           '-G', '--expt-relaxed-constexpr']
        }
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile'
        self.sourcesdir = 'src_cuda'
        self.build_system.nvcc = 'nvcc -g -G'
        self.build_system.cxx = 'CC'
        self.build_system.max_concurrency = 2
        self.tool = 'cuda-gdb'
        self.executable = self.tool
        self.target_executable = 'mpi+omp+cuda'
# }}}

# {{{ run
        ompthread = 1
        self.cubesize = cubesize
        self.name = 'sphexa_cudagdb_{}_{:03d}mpi_{:03d}omp_{}n_{}steps'.format(
            self.testname, mpitask, ompthread, cubesize, steps)
        self.num_tasks = mpitask
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = ompthread
        self.num_tasks_per_core = 1
        self.use_multithreading = False
        self.exclusive = True
        self.time_limit = '5m'
        self.variables = {
            'CRAYPE_LINK_TYPE': 'dynamic',
            'OMP_NUM_THREADS': str(self.num_cpus_per_task),
        }
        self.tool_input = 'gdb.input'
        tool_init = 'gdbinit'
        self.executable_opts = [
            '--nh', '--init-command ./%s' % tool_init,
            '--batch-silent', '--command=./%s' % self.tool_input,
            self.target_executable]
        self.version_rpt = 'version.rpt'
        self.which_rpt = 'which.rpt'
        self.log_bkpt = 'info_breakpoint.log'
        self.log_devices = 'info_devices.log'
        self.log_kernels = 'info_kernels.log'
        self.log_threads = 'info_threads.log'
        self.log_navigate = 'info_navigate.log'
        self.log = 'info_std_vector.log'
        self.pre_run = [
            'module rm xalt',
            'mv %s %s' % (self.target_executable + '.app',
                          self.target_executable),
            'ln -fs GDB/* .',
            'sed -i -e "s@-s 0@-s %s@" -e "s@-n 15@-n %s@" %s' %
            (steps, cubesize, self.tool_input),
            '%s --version |head -n4 &> %s' % (self.tool, self.version_rpt),
            'which %s &> %s' % (self.tool, self.which_rpt),
        ]
# }}}

    # {{{ self.sanity_patterns:
    @rfm.run_before('sanity')
    def set_sanity_gpu(self):
        '''
        This method runs sanity checks on the following logs:

        - info_devices:
        .. literalinclude:: ../../reframechecks/res/cuda-gdb/info_devices.log
          :lines: 1-1

        - info_kernels:
        .. literalinclude:: ../../reframechecks/res/cuda-gdb/info_kernels.log
          :lines: 1-1

        - info_threads:
        .. literalinclude:: ../../reframechecks/res/cuda-gdb/info_threads.log
          :lines: 1-1

        - info_navigate:
        .. literalinclude:: ../../reframechecks/res/cuda-gdb/info_navigate.log
          :lines: 1-1

        - info_stl:
        .. literalinclude::
            ../../reframechecks/res/cuda-gdb/info_std_vector.log
          :lines: 1-1

        - info_clist:
        .. literalinclude:: ../../reframechecks/res/cuda-gdb/info_const_int.log
          :lines: 1-1

        '''
        self.gpu_specs = {}
        self.gpu_specs_bool = {}
        ref_gpu_specs = {}
        ref_gpu_specs['P100'] = {}
        ref_gpu_specs['V100'] = {}
        # {{{ info_devices.log:
        #   Dev PCI Bus/Dev ID Name Description SM Type SMs Warps/SM Lanes/Warp
        #    Max Regs/Lane Active SMs Mask
        # *   0   88:00.0 Tesla V100-SXM2-16GB   GV100GL-A   sm_70  80 64 ...
        #                       ^^^^                         ^^^^^  ^^ ^^
        #               32 256 0x000000000000ffffffffffffffffffff
        #               ^^
        self.rpt = os.path.join(self.stagedir, self.log_devices)
        ref_gpu_specs = {
            'V100': {
                'capability': 'sm_70',
                'sms': 80,
                'WarpsPerSM': 64,
                'LanesPerWarp': 32,  # = warpSize
                'max_threads_per_sm': 2048,
                'max_threads_per_device': 163840,
            },
            'P100': {
                'capability': 'sm_60',
                'sms': 56,
                'WarpsPerSM': 64,
                'LanesPerWarp': 32,  # = warpSize
                'max_threads_per_sm': 2048,
                'max_threads_per_device': 114688,
            },
        }
        regex = (r'Tesla (?P<gpu_name>\S+)-\S+-\S+\s+\S+\s+(?P<cap>sm_\d+)\s+'
                 r'(?P<sms>\d+)\s+(?P<WarpsPerSM>\d+)\s+(?P<LanesPerWarp>\d+)')
        # --- get gpu_name (V100 or P100):
        gpu_name = sn.evaluate(sn.extractsingle(regex, self.rpt, 'gpu_name'))
        # --- get capability (True means that extracted value matches ref):
        res = sn.extractsingle(regex, self.rpt, 'cap')
        self.gpu_specs['capability'] = res
        self.gpu_specs_bool['capability'] = \
            (res == ref_gpu_specs[gpu_name]['capability'])
        # --- get sms:
        res = sn.extractsingle(regex, self.rpt, 'sms', int)
        self.gpu_specs['sms'] = res
        self.gpu_specs_bool['sms'] = (res == ref_gpu_specs[gpu_name]['sms'])
        # --- get WarpsPerSM:
        res = sn.extractsingle(regex, self.rpt, 'WarpsPerSM', int)
        self.gpu_specs['WarpsPerSM'] = res
        self.gpu_specs_bool['WarpsPerSM'] = \
            (res == ref_gpu_specs[gpu_name]['WarpsPerSM'])
        # --- get LanesPerWarp|warpSize:
        res = sn.extractsingle(regex, self.rpt, 'LanesPerWarp', int)
        self.gpu_specs['LanesPerWarp'] = res
        self.gpu_specs_bool['LanesPerWarp'] = \
            (res == ref_gpu_specs[gpu_name]['LanesPerWarp'])
        # --- threads_per_sm <= LanesPerWarp * WarpsPerSM
        res = self.gpu_specs['LanesPerWarp'] * self.gpu_specs['WarpsPerSM']
        self.gpu_specs['max_threads_per_sm'] = res
        self.gpu_specs_bool['max_threads_per_sm'] = \
            (res == ref_gpu_specs[gpu_name]['max_threads_per_sm'])
        # --- threads_per_device <= threads_per_sm * sms
        res = self.gpu_specs['sms'] * self.gpu_specs['max_threads_per_sm']
        self.gpu_specs['max_threads_per_device'] = res
        self.gpu_specs_bool['max_threads_per_device'] = \
            (res == ref_gpu_specs[gpu_name]['max_threads_per_device'])
        # --- max_np of 1gpu = f(max_threads_per_device) where np = cube_size^3
        import math
        self.gpu_specs['max_cubesz'] = sn.defer(math.ceil(pow(sn.evaluate(res),
                                                              1/3)))
        # }}}

        # {{{ info_kernels.log:
        # Kernel Parent Dev Grid Status SMs Mask   GridDim  BlockDim Invocation
        # * 0 - 0 3 Active 0x (106,1,1) (256,1,1) ...::density<double>(n=27000,
        #                      ^^^^^^^   ^^^^^^^                         ^^^^^
        # ---------------------------------------------------------------------
        self.log = os.path.join(self.stagedir, self.log_kernels)
        regex = (r'\*.*Active \S+ \((?P<grid_x>\d+),(?P<grid_y>\d+),'
                 r'(?P<grid_z>\d+)\)\s+\((?P<block_x>\d+),(?P<block_y>\d+),'
                 r'(?P<block_z>\d+)\).*\(n=(?P<np>\d+), ')
        grid_x = sn.extractsingle(regex, self.log, 'grid_x', int)
        grid_y = sn.extractsingle(regex, self.log, 'grid_y', int)
        grid_z = sn.extractsingle(regex, self.log, 'grid_z', int)
        block_x = sn.extractsingle(regex, self.log, 'block_x', int)
        block_y = sn.extractsingle(regex, self.log, 'block_y', int)
        block_z = sn.extractsingle(regex, self.log, 'block_z', int)
        np = sn.extractsingle(regex, self.log, 'np', int)
        self.kernel_grid = grid_x * grid_y * grid_z
        self.kernel_block = block_x * block_y * block_z
        self.kernel_np = np
        import math
        self.gpu_specs['cubesz'] = \
            sn.defer(math.ceil(pow(sn.evaluate(self.kernel_np), 1/3)))

        # {{{ TODO:tuple
        # https://github.com/eth-cscs/reframe/blob/master/cscs-checks/
        # prgenv/affinity_check.py#L38
        # regex=(r'\*.*Active \S+ (?P<griddim>\(\d+,\d+,\d+\))\s+(?P<blockdim>'
        #        r'\(\d+,\d+,\d+\)).*\(n=(?P<np>\d+), ')
        # from functools import reduce
        # self.res  = reduce(lambda x, y: x*y, list(res))
        # sn.extractsingle(regex, self.stdout, 'nrgy',
        #   conv=lambda x: int(x.replace(',', '')))
        # res: ('(', '1', '0', '6', ',', '1', ',', '1', ')')
        # }}}
        # }}}

        # {{{ info_threads.log:
        # BlockIdx ThreadIdx To BlockIdx ThreadIdx Count Virtual PC Filename L
        # Kernel 0
        # * (0,0,0) (0,0,0)  (1,0,0) (63,0,0) 320 0x0... ../cudaDensity.cu 27
        #   (1,0,0) (64,0,0) (1,0,0) (95,0,0)  32 0x0... ../cudaDensity.cu 26
        #   etc...                        sum(^^^)
        # ---------------------------------------------------------------------
        self.log = os.path.join(self.stagedir, self.log_threads)
        regex = r'(\(\S+\)\s+){4}(?P<nth>\d+)\s+0x'
        self.threads_np = sn.sum(sn.extractall(regex, self.log, 'nth', int))
        # }}}

        # {{{ info_navigate.log:
        # gridDim=(106,1,1) blockDim=(256,1,1) blockIdx=(0,0,0) \
        # threadIdx=(0,0,0) warpSize=32 thid=0
        # kernel 0 grid 3 block (0,0,0) thread (0,0,0) device 0 sm 0 warp 0 ...
        # --
        # gridDim=(106,1,1) blockDim=(256,1,1) blockIdx=(105,0,0)
        # threadIdx=(255,0,0) warpSize=32 thid=27135
        # kernel 0 grid 3 block (105,0,0) thread (255,0,0) device 0 sm 43 ...
        # --
        # gridDim=(106,1,1) blockDim=(256,1,1) blockIdx=(55,0,0)
        # threadIdx=(255,0,0) warpSize=32 thid=14335
        # kernel 0 grid 3 block (55,0,0) thread (255,0,0) device 0 sm 55 ...
        # ---------------------------------------------------------------------
        self.log = os.path.join(self.stagedir, self.log_navigate)
        regex = r'^gridDim.*warpSize=\d+ thid=(?P<th>\d+)$'
        self.thids = sn.extractall(regex, self.log, 'th', int)
        # }}}

        # {{{ info_std_vector.log:
        # --- get vector length(True means that extracted value matches ref):
        self.rpt = os.path.join(self.stagedir, self.log)
        # std::vector of length 27000, capacity 27000
        regex = r'std::vector of length (?P<vec_len1>\d+),'
        res = sn.extractsingle(regex, self.rpt, 'vec_len1', int)
        self.gpu_specs['vec_len1'] = res
        self.gpu_specs_bool['vec_len1'] = (res == self.cubesize**3)
        # Vector size = 27000 (pvector)
        regex = r'^Vector size = (?P<vec_len2>\d+)$'
        res = sn.extractsingle(regex, self.rpt, 'vec_len2', int)
        self.gpu_specs['vec_len2'] = res
        self.gpu_specs_bool['vec_len2'] = (res == self.cubesize**3)
        # }}}

        # {{{ --- sanity_patterns:
        self.sanity_patterns = sn.all([
            sn.assert_true(self.gpu_specs_bool['capability']),
            sn.assert_true(self.gpu_specs_bool['sms']),
            sn.assert_true(self.gpu_specs_bool['WarpsPerSM']),
            sn.assert_true(self.gpu_specs_bool['LanesPerWarp']),
            sn.assert_true(self.gpu_specs_bool['max_threads_per_sm']),
            sn.assert_true(self.gpu_specs_bool['max_threads_per_device']),
            sn.assert_true(self.gpu_specs_bool['vec_len1']),
            sn.assert_true(self.gpu_specs_bool['vec_len2']),
            # NO: sn.assert_true(self.gpu_specs_bool),
        ])
        # }}}
    # }}}

    # {{{ self.perf_patterns:
    @rfm.run_before('performance')
    def check_gpu_perf(self):
        # print(type(self.res[0]))
        self.perf_patterns = {
            'info_kernel_nblocks': self.kernel_grid,
            'info_kernel_nthperblock': self.kernel_block,
            'info_kernel_np': self.kernel_np,
            'info_threads_np': self.threads_np,
            #
            'SMs': self.gpu_specs['sms'],
            'WarpsPerSM': self.gpu_specs['WarpsPerSM'],
            'LanesPerWarp': self.gpu_specs['LanesPerWarp'],
            'max_threads_per_sm': self.gpu_specs['max_threads_per_sm'],
            'max_threads_per_device':
                self.gpu_specs['max_threads_per_device'],
            'best_cubesize_per_device': self.gpu_specs['max_cubesz'],
            'cubesize': self.gpu_specs['cubesz'],
            #
            'vec_len': self.gpu_specs['vec_len1'],
            'threadid_of_last_sm': self.thids[2],
            'last_threadid': self.thids[1],
        }
        myzero = (0, None, None, '')
        self.reference = {
            '*': {
                'info_kernel_nblocks': myzero,
                'info_kernel_nthperblock': myzero,
                'info_kernel_np': myzero,
                'info_threads_np': myzero,
                #
                'capability': myzero,
                'SMs': myzero,
                'WarpsPerSM': myzero,
                'LanesPerWarp': myzero,
                'max_threads_per_sm': myzero,
                'max_threads_per_device': myzero,
                'best_cubesize_per_device': myzero,
                'cubesize': myzero,
                #
                'vec_len': myzero,
                'threadid_of_last_sm': myzero,
                'last_threadid': myzero,
            }
        }
    # }}}

# {{{ set_sanity hook: compiler flags
    @rfm.run_before('compile')
    def setflags(self):
        self.build_system.cxxflags = \
            self.prgenv_flags[self.current_environ.name]
        self.nvccflags = \
            self.prgenv_gpuflags[self.current_environ.name]
        self.build_system.options = [
            self.target_executable, 'SRCDIR=.', 'BUILDDIR=.',
            'BINDIR=.', 'NVCCFLAGS="%s"' % " ".join(self.nvccflags),
            'NVCCARCH=sm_70', 'CUDA_PATH=$CUDA_PATH',
            'MPICXX=%s' % self.build_system.cxx]
#         if self.current_environ.name == 'PrgEnv-cray':
#             # cce<9.1 fails to compile with -g
#             self.modules = ['cdt/20.03']
# }}}
