#!/usr/bin/env bash

# Location of weighted ASR lattices
latDir=$1

# Tuning directory
tuneDir=$2/decoder

# Location of feature file only get the source side
featFile=$3

symsFile=$4

tuneTemplate=$5

# Maximum number of jobs to run on the queue
numJobs=200
stage=0

if [ $# -ne 5 ]; then
  echo "USAGE : ./tune.sh [LAT-DIR] [TUNE-DIR] [FEAT-FILE] [SYMSFILE] [TUNE-TEMPLATE]"
  exit 1
fi

if [ $stage -le 0 ]; then

  rm -rf $tuneDir/*

  mkdir -p $tuneDir/lat
  mkdir -p $tuneDir/pre/log

  # Create a dummy weights file
  printf "0.0\n0.0\n0.0\n0.0" > $tuneDir/pre/weights.txt

  # The dev set is hardcoded for tuning here
  time mt_util/phrase2FST.py \
    -p $featFile \
    -f $tuneDir/pre/S.fst.txt \
    -s $tuneDir/pre/syms.txt \
    -e $symsFile \
    -w $tuneDir/pre/weights.txt

  # Create S (Unweighted)
  fstcompile --arc_type=log $tuneDir/pre/S.fst.txt | fstarcsort > $tuneDir/pre/S.fst

  # Create OOV file
  comm -23 <(sort $symsFile) <(sort $tuneDir/pre/syms.txt.mt)  | awk -v a=999999 '{print $2 " " a}' > $tuneDir/pre/oov.txt
  oov=$tuneDir/pre/oov.txt

  seg=$tuneDir/pre/S.fst
  syms=$tuneDir/pre/syms.txt

  # Now compose S with L_{ASR}
  for l in `ls -v $latDir/*.lat`
  do
    # Check for job limit
    while [ `qstat | grep -c createP_AS` -ge $numJobs ]; do
      sleep 5
    done

    bname=${l##*/}
    qsub -l 'arch=*64*' -cwd -j y -o $tuneDir/pre/log/$bname.log -v input=$l,seg=$seg,output_dir=$tuneDir,sym=$syms,oov=$oov mt_util/tune_util/createP_ASR.sh
  done

  # Wait for jobs to finish
  while [ `qstat | grep -c createP_AS` -ne 0 ]; do
    sleep 5
  done

  echo "Done creating phrase lattices"
fi

# Remove old files and copy template

# Tune
cd $2
java -cp zmert.jar ZMERT -maxMem 5000 ZMERT_cfg.txt
