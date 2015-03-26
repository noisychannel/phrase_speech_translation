#!/usr/bin/env bash

p=${input}
w=${wmt}
outputDir=${output_dir}
syms=${sym}

echo $p
echo $w
echo $outputDir
echo $syms

# FST prune behaves erratically with beam width 0
# 100 shortest paths, hardcoded here

bname=${p##*/}
fstcompose $p $w | fstprint \
  | fstcompile | fstshortestpath --nshortest=100 | fstrmepsilon \
  | fstminimize > $outputDir/latFinal/$bname

  fstprintpaths $syms $outputDir/latFinal/$bname 2 \
  >> $outputDir/nbest/$bname.nbest
