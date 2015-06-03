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
  | fstcompile | fstprune --weight=0.0001 | fstproject | fstrmepsilon \
  | fstminimize > $outputDir/latFinal/$bname

mkdir -p $outputDir/1best

/export/a04/gkumar/code/custom/phrase_speech_translation/util/fstprintstring $outputDir/latFinal/$bname $syms >> $outputDir/1best/$bname.1best
