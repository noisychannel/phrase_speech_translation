#!/bin/bash

#$ -cwd
#$ -S /bin/bash
#$ -M gkumar6@jhu.edu
#$ -m eas
#$ -l num_proc=1,h_vmem=5g,mem_free=5g,h_rt=72:00:00
#$ -V
#$ -j y -o log/k2f_dev.log

asr_util/kaldi2FST.sh /export/a04/gkumar/code/kaldi-new data/asr/dev/lattices \
  /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri6a_dnn/decode_dev 0.067