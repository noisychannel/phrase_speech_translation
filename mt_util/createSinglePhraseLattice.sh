#!/usr/bin/env bash

l=${input}
outputDir=${output_dir}
syms=${sym}

echo $l
echo $outputDir
echo $syms

# FST prune behaves erratically with beam width 0

bname=${l##*/}
fstcompose $l $outputDir/S.sort.fst \
  | fstproject | fstprint \
  | fstcompile | fstprune --weight=0.001 | fstrmepsilon \
  | fstminimize | fstdeterminize > $outputDir/lat/$bname

  /export/a04/gkumar/code/custom/phrase_speech_translation/util/fstprintstring $outputDir/lat/$bname $syms \
  >> $outputDir/1best/$bname.1best
