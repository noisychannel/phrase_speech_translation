#!/usr/bin/env bash

# The directory that contains the word lattices
inputDir=$1
# The directory where the output lattices will be put
outputDir=$2

if [ $# -ne 2 ]; then
  echo "USAGE : ./removeLatWeights.sh [INPUT-DIR] [OUTPUT-DIR]"
  exit 1
fi

mkdir -p $outputDir

for l in $inputDir/*.lat
do
  bname=${l##*/}
  fstprint $l | awk -F "\t" '{if (NF == 5){$5 = ""}; print $_}' \
    | sed 's: *$::g' | fstcompile --arc_type=log > $outputDir/$bname.lat
done
