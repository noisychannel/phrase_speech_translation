#!/bin/bash

#$ -cwd
#$ -S /bin/bash
#$ -M gkumar6@jhu.edu
#$ -m eas
#$ -l num_proc=1,h_vmem=5g,mem_free=5g,h_rt=72:00:00
#$ -V
#$ -j y -o log/plf_dev2.log

asr_util/mainPLF.py -l data/asr/dev2/lattices/lattices-pushed \
  -s /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt \
  -c /export/a04/gkumar/corpora/fishcall/jack-splits/split-matt/dev2 \
  -o data/asr/dev2/plf \
  -t /export/a04/gkumar/corpora/fishcall/fisher/tim
