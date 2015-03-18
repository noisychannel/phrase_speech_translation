#!/usr/bin/env bash

# The directory that contains the word lattices
inputDir=$1
# The phrase segmentation transducer
segmentationTransducer=$2
# The directory where the phrase lattice will be put
syms=$3
outputDir=$4

#numJobs=100

if [ $# -ne 4 ]; then
  echo "USAGE : ./createPhraseLattice.sh [INPUT-DIR] [SEG-TRANSDUCER] [SYMS] [OUTPUT-DIR]"
  exit 1
fi

rm -rf $outputDir/*

mkdir -p $outputDir/log
mkdir -p $outputDir/1best

rm -f $outputDir/1best/log/*
rm -f $outputDir/1best/1best/*

fstarcsort $segmentationTransducer $outputDir/S.sort.fst

for l in `ls -v $inputDir/*.lat`
do
  # Check for job limit
  #while [ `qstat | grep -c createSing` -ge $numJobs ]; do
    #sleep 5
  #done

  bname=${l##*/}
  qsub -l 'arch=*64*' -cwd -j y -o $outputDir/log/$bname.log -v input=$l,output_dir=$outputDir,sym=$syms mt_util/createSinglePhraseLattice.sh
done

# Wait for jobs to finish
while [ `qstat | grep -c createSing` -ne 0 ]; do
  sleep 5
done

echo "Done creating phrase lattices"
