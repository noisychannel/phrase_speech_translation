#!/usr/bin/env bash

p=${input}
w=${wmt}
outputDir=${output_dir}
syms=${sym}

echo $l
echo $outputDir
echo $syms

# FST prune behaves erratically with beam width 0
# 100 shortest paths, hardcoded here

bname=${l##*/}
fstcompose $p $w \
  | fstproject | fstprint \
  | fstcompile | fstprune --nshortest=100 | fstrmepsilon \
  | fstminimize | fstdeterminize > $outputDir/lat/$bname

  fstprintpaths $outputDir/lat/$bname $syms 2 \
  >> $outputDir/nbest/$bname.nbest
