#!/bin/bash
CPUPROFILE=`hostname`.$SLURM_PROCID "$@"
