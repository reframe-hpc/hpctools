#!/bin/bash

# rm -f eff.vm
# rocm-smi -d 0 --showmeminfo vram > eff.vm
# ======================= ROCm System Management Interface =======================
# ============================= Memory Usage (Bytes) =============================
# GPU[0]		: VRAM Total Memory (B): 34342961152
# GPU[0]		: VRAM Total Used Memory (B): 7028736

while [ 1 = 1 ]; do 
    rocm-smi -d 0 --showmeminfo vram |grep --color=never Used >> vm.rpt
    sleep 1
done 2>&1
