#!/bin/bash
#SBATCH --time=900:00:00
#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
echo Running on host `hostname`
echo Time is `date`


cd PPPPP
echo Directory is `pwd`


# Run job
./GOMC_CPU_GCMC in.conf >& out_NNNNNN_AAAAAA_FFF_bar.dat
