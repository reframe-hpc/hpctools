#!/usr/bin/env python3
import json
import os
# import pandas as pd

from amd_plot_roofline_hierarchical_jg import roofline
# cloned from:
# https://github.com/Techercise/AMD-Instruction-Roofline-using-rocProf-Metrics
# -> blob/main/amd_postprocess_instruction.py
# -----------------------------------------------------------------------------
# https://github.com/Techercise/AMD-Instruction-Roofline-using-rocProf-Metrics
# https://arxiv.org/pdf/2110.08221.pdf
# -> Matthew Leinhauser <mattl@udel.edu>
# -> Sunita Chandrasekaran <schandra@udel.edu>
# "Metrics and Design of an Instruction Roofline Model for AMD GPUs"
# FP64_Gflops/s:
# P100=4761 (sm60, 56sms*64c/sm*1.33GHz, 16GB),
# V100=7833 (sm70, 80sms*64c/sm*1.53GHz, 16GB),
# A100=9746 (sm80, 108sms*64c/sm*1.41GHz),
# Mi100=11500
# -----------------------------------------------------------------------------


# {{{ read_json_data
def read_json_data(infile, kernel):
    f = open(infile)
    d = json.load(f)
    f.close()
    dd = d['runs'][0]['testcases']
    labels = []
    fetchsize = []
    sq_insts_valu = []
    writesize = []
    sq_insts_salu = []
    ns = []
    for job_n in range(len(dd)):
        # print(f'job_n={job_n}')
        for metric_job_n in range(len(dd[job_n]['perfvars'])):
            json_metric_name = dd[job_n]["perfvars"][metric_job_n]["name"]
            json_metric_value = dd[job_n]["perfvars"][metric_job_n]["value"]
            if json_metric_name == 'n_cubeside':
                labels.append(f'-n{json_metric_value}')
            elif json_metric_name == f'{kernel}_FetchSize':
                fetchsize.append(json_metric_value)
            elif json_metric_name == f'{kernel}_SQ_INSTS_VALU':
                sq_insts_valu.append(json_metric_value)
            elif json_metric_name == f'{kernel}_WriteSize':
                writesize.append(json_metric_value)
            elif json_metric_name == f'{kernel}_SQ_INSTS_SALU':
                sq_insts_salu.append(json_metric_value)
            elif json_metric_name == f'{kernel}_ns':
                ns.append(json_metric_value)
    # print(labels)
    # print(fetchsize)
    # print(sq_insts_valu)
    # print(writesize)
    # print(sq_insts_salu)
    # print(ns)
    return (labels, fetchsize, sq_insts_valu, writesize, sq_insts_salu, ns)
# }}}


# {{{ compute roofs, Intensity and GIPS:
# 1ns=10^-9s / 1us=10^-6s
def calc_Instructions(sq_insts_valu, sq_insts_salu):
    """
    dfmetric['Instructions'] = \
    (dfmetric['SQ_INSTS_VALU'] * 4) + dfmetric['SQ_INSTS_SALU']
    """
    # TODO: return [sq_insts_salu[ii] + sq_insts_valu[ii] * 4 for ...]
    res = []
    for ii in range(len(sq_insts_valu)):
        res.append(sq_insts_salu[ii] + sq_insts_valu[ii] * 4)

    return res


def calc_Time(ns):
    """
    dfmetric['Time'] = dfmetric['time'] * pow(10, -6) # = from usec to sec
    nsec * 10^-9 = sec # = from nsec to sec
    """
    return [ii * pow(10, -9) for ii in ns]


def calc_Instructions_Intensity(inst, fetchsize, writesize, time):
    """
    dfmetric['Instruction Intensity HBM'] = \
    (dfmetric['Instructions'] / 64) /
    ((dfmetric['Fetch_Size'] + dfmetric['Write_Size']) * dfmetric['Time'])
    """
    res = []
    for ii in range(len(inst)):
        res.append((inst[ii] / 64) /
                   ((fetchsize[ii] + writesize[ii]) * time[ii]))

    return res


def calc_GIPS(inst, time):
    """
    dfmetric['GIPS'] = (dfmetric['Instructions'] / 64) /
    (pow(10, 9) * dfmetric['Time'])
    """
    res = []
    wavefront = 64
    for ii in range(len(inst)):
        res.append((inst[ii] / wavefront) / (pow(10, 9) * time[ii]))

    return res
# }}}


# {{{ plot:
def plot_roofline(jsonfile, gips, Instruction_Intensity_HBM, labels, flag,
                  kernel):
    l2_ai = [0 for z in gips]
    l1_ai = [0 for z in gips]
    roofline(jsonfile, gips, Instruction_Intensity_HBM, l2_ai, l1_ai, labels,
             flag, kernel)

# }}}


if __name__ == '__main__':
    jsonfile = 'res_amd_mi100/reframe.json'
    # jsonfile = 'eff.json'
    kernels = [
        'computeMomentumAndEnergyIAD',
        'findNeighborsKernel',
        'computeIAD',
        'density',
    ]
    kernel = kernels[0]
    # kernel = kernels[1]
    # kernel = kernels[2]
    # kernel = kernels[3]

    lumi = True  # False
    if lumi:
        # {{{ lumi:
        for kernel in kernels:
            labels, fetchsize, sq_insts_valu, writesize, sq_insts_salu, ns =
            read_json_data(jsonfile, kernel)
            time = calc_Time(ns)
            # print(f'ns={ns}')
            # print(f'time={time}')
            inst = calc_Instructions(sq_insts_valu, sq_insts_salu)
            Instruction_Intensity_HBM =
            calc_Instructions_Intensity(inst, fetchsize, writesize, time)
            gips = calc_GIPS(inst, time)
            flag = 'HBM'
            print(f'# kernel={kernel}')
            # print(ns)
            # print(time)
            # print(inst)
            print(f'# jsonfile={jsonfile}')
            print(f'Instruction_Intensity_HBM={Instruction_Intensity_HBM}')
            print(f'gips={gips}')
            print(f'labels={labels}')
            print(f'flag={flag}')
            plot_roofline(jsonfile, gips, Instruction_Intensity_HBM, labels,
                          flag, kernel)
            os.rename('generic_mi100_roofline.png',
                      f'{kernel}_mi100_roofline.png')
        # }}}

    debug = False
    if debug:
        # {{{ debug:
        # {{{ xls ok:fig7 TWEAC_simulations/mi100_tweac_cc_inst_output.csv
        # -> gips=[4.993347263108402]
        # -> Instruction_Intensity_HBM=[0.40753481867458635]
        # metrics,SQ_INSTS_SALU,inst,7430073024
        # metrics,SQ_INSTS_VALU,inst,17764624449
        # metrics,FetchSize,bytes,11460394000
        # metrics,WriteSize,bytes,792172000
        # metrics,time,us,245603.571 <----- us ?
        sq_insts_salu = [7430073024]
        sq_insts_valu = [17764624449]
        fetchsize = [11460394000]
        writesize = [792172000]
        ns = [245603.571]
        # }}}
        # {{{ ok:fig6 LWFA_simulations/mi100_lw_cc_inst_output.csv
        # Instruction_Intensity_HBM=[1.862501575963134]
        # gips=[2.855576241257221]
        sq_insts_salu = [30791040]
        sq_insts_valu = [104751360]
        fetchsize = [1124711000]
        writesize = [408483000]
        ns = [2461.174]
        # }}}
        # {{{ ?: LWFA_simulations/mi100_lw_pp_inst_output.csv
        # Instruction_Intensity_HBM=[2.520477925887229]
        # gips=[4.709127371397627]
        # sq_insts_salu = [28203840]
        # sq_insts_valu = [309335040]
        # fetchsize = [1229821000]
        # writesize  = [638526000]
        # ns = [4199.106]
        # }}}
        time = calc_Time(ns)
        inst = calc_Instructions(sq_insts_valu, sq_insts_salu)
        gips = calc_GIPS(inst, time)
        Instruction_Intensity_HBM =
        calc_Instructions_Intensity(inst, fetchsize, writesize, time)
        labels = ['x']
        flag = 'HBM'
        print(f'Instruction_Intensity_HBM={Instruction_Intensity_HBM}')
        print(f'gips={gips}')
        # }}}
