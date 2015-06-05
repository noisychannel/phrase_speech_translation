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

# Concats final result with an empty FST to remove multiple final states

bname=${p##*/}
fstcompose $p $w | fstprint \
  | fstcompile | fstshortestpath --nshortest=99 | fstrmepsilon \
  | fstminimize | fstconcat - $outputDir/dummy.fst > $outputDir/latFinal/$bname

fstprintpaths $syms $outputDir/latFinal/$bname 2 >> $outputDir/nbest/$bname.nbest
