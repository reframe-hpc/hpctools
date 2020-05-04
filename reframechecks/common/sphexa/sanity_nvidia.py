# Copyright 2019-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# HPCTools Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.fields import ScopedDict

# {{{ sanity_function: nsys
@sn.sanity_function
def nsys_version(obj):
    '''Checks tool's version:

    .. code-block::

      > nsys --version
      NVIDIA Nsight Systems version 2020.1.1.65-085319d
      returns: True or False
    '''
    reference_tool_version = {
        'daint': '2020.2.1.71',
        'dom': '2020.2.1.71',
        # 'daint': '2020.1.1.65',
        # 'dom': '2020.1.1.65',
    }
    regex = r'^NVIDIA Nsight Systems version (?P<toolversion>\S+)-'
    version = sn.extractsingle(regex, obj.version_rpt, 'toolversion')
    TorF = sn.assert_eq(version,
                        reference_tool_version[obj.current_system.name])
    return TorF


# {{{ H2D, D2H
# ----------------------------------------------------------------------------
@sn.sanity_function
def nsys_report_HtoD_pct(self):
    '''Reports ``[CUDA memcpy HtoD]`` Time(%) measured by the tool and averaged
    over compute nodes

    .. code-block::

      > job.stdout
      # CUDA Memory Operation Statistics (nanoseconds)
      #
      # Time(%)      Total Time  Operations         Average  ...
      # -------  --------------  ----------  --------------  ...
      #    99.1       154400354         296        521622.8  ...
      #    ****
      #
      #             Minimum         Maximum  Name
      #      --------------  --------------  -------------------
      #                 896         8496291  [CUDA memcpy HtoD]
    '''
    regex = (r'^\s+(?P<pctg_nsec>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+'
             r'\[CUDA memcpy HtoD\]\s+$')
    result = sn.round(sn.avg(sn.extractall(regex, self.stdout, 'pctg_nsec',
                                           float)), 1)
    return result


@sn.sanity_function
def nsys_report_DtoH_pct(self):
    '''Reports ``[CUDA memcpy DtoH]`` Time(%) measured by the tool and averaged
    over compute nodes

    .. code-block::

      > job.stdout
      # CUDA Memory Operation Statistics (nanoseconds)
      #
      # Time(%)      Total Time  Operations         Average  ...
      # -------  --------------  ----------  --------------  ...
      #     0.9         1385579          84         16495.0  ...
      #    ****
      #
      #             Minimum         Maximum  Name
      #      --------------  --------------  -------------------
      #                6144           21312  [CUDA memcpy DtoH]
    '''
    regex = (r'^\s+(?P<pctg_nsec>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+'
             r'\[CUDA memcpy DtoH\]\s+$')
    result = sn.round(sn.avg(sn.extractall(regex, self.stdout, 'pctg_nsec',
                                           float)), 1)
    return result


# ----------------------------------------------------------------------------
@sn.sanity_function
def nsys_report_HtoD_KiB(self):
    '''Reports ``[CUDA memcpy HtoD]`` Memory Operation (KiB) measured by the
    tool and averaged over compute nodes

    .. code-block::

      > job.stdout
      # CUDA Memory Operation Statistics (KiB)
      #
      #             Total      Operations            Average            Minimum
      # -----------------  --------------  -----------------  -----------------
      #         1530313.0             296             5170.0              0.055
      #         *********
      #           16500.0              84              196.4             62.500
      # ...
      #            Maximum  Name
      #  -----------------  -------------------
      #            81250.0  [CUDA memcpy HtoD]
      #              250.0  [CUDA memcpy DtoH]
    '''
    regex = (r'^\s+(?P<KiB>\d+.\d+)\s+\d+\s+\S+\s+\S+\s+\S+\s+'
             r'\[CUDA memcpy HtoD\]\s+$')
    result = sn.round(sn.avg(sn.extractall(regex, self.stdout, 'KiB',
                                           float)), 1)
    return result


@sn.sanity_function
def nsys_report_DtoH_KiB(self):
    '''Reports ``[CUDA memcpy DtoH]`` Memory Operation (KiB) measured by the
    tool and averaged over compute nodes

    .. code-block::

      > job.stdout
      # CUDA Memory Operation Statistics (KiB)
      #
      #             Total      Operations            Average            Minimum
      # -----------------  --------------  -----------------  -----------------
      #         1530313.0             296             5170.0              0.055
      #           16500.0              84              196.4             62.500
      #           *******
      # ...
      #            Maximum  Name
      #  -----------------  -------------------
      #            81250.0  [CUDA memcpy HtoD]
      #              250.0  [CUDA memcpy DtoH]
    '''
    regex = (r'^\s+(?P<KiB>\d+.\d+)\s+\d+\s+\S+\s+\S+\s+\S+\s+'
             r'\[CUDA memcpy DtoH\]\s+$')
    result = sn.round(sn.avg(sn.extractall(
        regex, self.stdout, 'KiB', float)), 1)
    return result
# }}}


# {{{ top functions
# ----------------------------------------------------------------------------
@sn.sanity_function
def nsys_report_momentumEnergy_pct(self):
    '''Reports ``CUDA Kernel`` Time (%) for MomentumAndEnergyIAD measured by
    the tool and averaged over compute nodes

    .. code-block::

      > job.stdout
      # CUDA Kernel Statistics (nanoseconds)
      #
      # Time(%)      Total Time   Instances         Average         Minimum
      # -------  --------------  ----------  --------------  --------------
      #    49.7        69968829           6      11661471.5        11507063
      #    ****
      #    26.4        37101887           6       6183647.8         6047175
      #    24.0        33719758          24       1404989.9         1371531
      # ...
      #         Maximum  Name
      #  --------------  ------------------
      #        11827539  computeMomentumAndEnergyIAD
      #         6678078  computeIAD
      #         1459594  density
      '''
    regex = (r'^\s+(?P<pctg>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+'
             r'computeMomentumAndEnergyIAD\s+$')
    result = sn.round(sn.avg(sn.extractall(
        regex, self.stdout, 'pctg', float)), 1)
    return result


@sn.sanity_function
def nsys_report_computeIAD_pct(self):
    '''Reports ``CUDA Kernel`` Time (%) for computeIAD measured by
    the tool and averaged over compute nodes

    .. code-block::

      > job.stdout
      # CUDA Kernel Statistics (nanoseconds)
      #
      # Time(%)      Total Time   Instances         Average         Minimum
      # -------  --------------  ----------  --------------  --------------
      #    49.7        69968829           6      11661471.5        11507063
      #    26.4        37101887           6       6183647.8         6047175
      #    ****
      #    24.0        33719758          24       1404989.9         1371531
      # ...
      #         Maximum  Name
      #  --------------  ------------------
      #        11827539  computeMomentumAndEnergyIAD
      #         6678078  computeIAD
      #         1459594  density
      '''
    regex = (r'^\s+(?P<pctg>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+'
             r'computeIAD\s+$')
    result = sn.round(sn.avg(sn.extractall(
        regex, self.stdout, 'pctg', float)), 1)
    return result


# ----------------------------------------------------------------------------
@sn.sanity_function
def nsys_report_cudaMemcpy_pct(self):
    '''Reports ``CUDA API`` Time (%) for cudaMemcpy measured by the tool and
    averaged over compute nodes

    .. code-block::

      > job.stdout

      # CUDA API Statistics (nanoseconds)
      #
      # Time(%)      Total Time       Calls         Average         Minimum
      # -------  --------------  ----------  --------------  --------------
      #    44.9       309427138         378        818590.3            9709
      #    ****
      #    40.6       279978449           2     139989224.5           24173
      #     9.5        65562201         308        212864.3             738
      #     4.9        33820196         306        110523.5            2812
      #     0.1          704223          36         19561.8            9305
      # ....
      #         Maximum  Name
      #  --------------  ------------------
      #        11665852  cudaMemcpy
      #       279954276  cudaMemcpyToSymbol
      #         3382747  cudaFree
      #          591094  cudaMalloc
      #           34042  cudaLaunch
    '''
    regex = r'^\s+(?P<pctg>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+cudaMemcpy\s+$'
    result = sn.round(sn.avg(sn.extractall(
        regex, self.stdout, 'pctg', float)), 1)
    return result
# }}}


@sn.sanity_function
def nsys_perf_patterns(obj):
    '''Dictionary of default nsys_perf_patterns for the tool
    '''
    res_d = {
        '%cudaMemcpy': nsys_report_cudaMemcpy_pct(obj),
        '%CUDA_memcpy_HtoD_time': nsys_report_HtoD_pct(obj),
        '%CUDA_memcpy_DtoH_time': nsys_report_DtoH_pct(obj),
        'CUDA_memcpy_HtoD_KiB': nsys_report_HtoD_KiB(obj),
        'CUDA_memcpy_DtoH_KiB': nsys_report_DtoH_KiB(obj),
        '%computeMomentumAndEnergyIAD': nsys_report_momentumEnergy_pct(obj),
        '%computeIAD': nsys_report_computeIAD_pct(obj),
    }
    return res_d

# TODO: ^\s+(?P<pctg_nsec>\d+)\s+total events collected.$
# }}}
