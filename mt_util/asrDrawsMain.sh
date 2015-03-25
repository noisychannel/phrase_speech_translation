#!/usr/bin/env bash

# The directory that contains the word lattices
inputDir=$1
weight=$2
# The phrase segmentation transducer
segmentationTransducer=$3
# The directory where the phrase lattice will be put
syms=$4
outputDir=$5
pruneBeam=$6

numJobs=200

if [ $# -ne 6 ]; then
  echo "USAGE : ./createPhraseLattice.sh [INPUT-DIR] [WEIGHTED-DIR] [SEG-TRANSDUCER] [SYMS] [OUTPUT-DIR] [BEAM]"
  exit 1
fi

rm -rf $outputDir/*

mkdir -p $outputDir/log
mkdir -p $outputDir/lat
mkdir -p $outputDir/1best

rm -f $outputDir/1best/log/*
rm -f $outputDir/1best/1best/*

fstarcsort $segmentationTransducer $outputDir/S.sort.fst

for l in `ls -v $inputDir/*.lat`
do
  # Check for job limit
  while [ `qstat | grep -c createSing` -ge $numJobs ]; do
    sleep 5
  done

  bname=${l##*/}
  qsub -l 'arch=*64*' -cwd -j y -o $outputDir/log/$bname.log \
    -v input=$l,input_weighted=$weight/$bname,output_dir=$outputDir,sym=$syms,beam=$pruneBeam mt_util/asrDrawsPhraseLattice.sh
done

# Wait for jobs to finish
while [ `qstat | grep -c asrDrawsPh` -ne 0 ]; do
  sleep 5
done

echo "Done creating phrase lattices"
