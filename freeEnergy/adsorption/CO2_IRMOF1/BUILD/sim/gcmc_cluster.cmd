#!/bin/bash
#SBATCH --time=900:00:00
#SBATCH --ntasks=1   # number of processor cores (i.e. tasks)
#SBATCH --nodes=1   # number of nodes
echo Running on host `hostname`
echo Time is `date`


cd RUN-DIR
echo Directory is `pwd`


# Run job with 1 processor
./GOMC_CPU_GCMC +p1 in.conf >& out_MOFNAME_ADSBNAME_FFF_bar.log
