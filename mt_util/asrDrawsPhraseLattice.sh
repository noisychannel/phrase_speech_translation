#!/usr/bin/env bash

l=${input}
lw=${input_weighted}
outputDir=${output_dir}
syms=${sym}

echo $l
echo $outputDir
echo $syms

bname=${l##*/}
fstcompose $l $outputDir/S.sort.fst \
  | fstproject | fstprint | fstcompile | fstprune --weight=0 | fstprint \
  | awk '{if (NF == 5) {$5 = ""}; print $_}' | sed 's: *$::g' \
  | fstcompile --arc_type=log | fstarcsort \
  | fstcompose $lw - | fstprint | fstcompile | fstprune --weight=0 | fstrmepsilon \
  | fstminimize | fstdeterminize \
  | /export/a04/gkumar/code/custom/phrase_speech_translation/util/fstprintstring - $syms \
  >> $outputDir/1best/$bname.1best
