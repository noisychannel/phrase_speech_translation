#!/usr/bin/env bash

p=${input}
w=${wmt}
outputDir=${output_dir}
syms=${sym}
asrScale=${a_scale}


echo $p
echo $w
echo $outputDir
echo $syms
echo $asrScale

# FST prune behaves erratically with beam width 0
# 100 shortest paths, hardcoded here

# Concats final result with an empty FST to remove multiple final states

bname=${p##*/}
fstprint $p | awk -v s=$asrScale '{if (NF == 5) {$5 = $5*s}; print $_}' | fstcompile --arc_type=log \
  | fstcompose - $w | fstprint \
  | fstcompile | fstshortestpath --nshortest=299 | fstrmepsilon \
  | fstminimize | fstconcat - $outputDir/dummy.fst > $outputDir/latFinal/$bname

fstprintpaths $syms $outputDir/latFinal/$bname 2 >> $outputDir/nbest/$bname.nbest
