#!/usr/bin/env bash

l=${input}
outputDir=${output_dir}
syms=${sym}

echo $l
echo $outputDir
echo $syms

bname=${l##*/}
fstcompose $l $outputDir/S.sort.fst \
  | fstproject | fstprint \
  | fstcompile | fstprune --weight=0 | fstrmepsilon \
  | fstminimize | fstdeterminize \
  | /export/a04/gkumar/code/custom/phrase_speech_translation/util/fstprintstring - $syms \
  >> $outputDir/1best/$bname.1best
