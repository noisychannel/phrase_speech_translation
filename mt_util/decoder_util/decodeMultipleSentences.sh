#!/usr/bin/env bash

# Location of weighted ASR lattices
latDir=$1

# Output directory
outDir=$2

# Location of feature file only get the source side
wmt=$3

# Syms
syms=$4

# Maximum number of jobs to run on the queue
numJobs=200
stage=0

if [ $# -ne 4 ]; then
  echo "USAGE : decoder_util/decodeMultipleSentences.sh [LAT-DIR] [OUT-DIR] [W-MT] [SYM-FILE]"
  exit 1
fi

fstcompile --arc_type=log $wmt | fstarcsort > $outDir/W_close.fst

mkdir -p $outDir/decode_log
mkdir -p $outDir/nbest
mkdir -p $outDir/latFinal

wmt_close=$outDir/W_close.fst

# Now compose S with L_{ASR}
for p in `ls -v $latDir/*.lat`
do
  # Check for job limit
  #while [ `qstat | grep -c decodeSing` -ge $numJobs ]; do
    #sleep 5
  #done

  bname=${p##*/}
  qsub -l 'arch=*64*' -cwd -j y -o $outDir/decode_log/$bname.log -v input=$p,wmt=$wmt_close,output_dir=$outDir,sym=$syms mt_util/decoder_util/decodeSingleSentenceOneBest.sh
done

# Wait for jobs to finish
while [ `qstat | grep -c decodeSing` -ne 0 ]; do
  sleep 5
done

echo "Done decoding"
