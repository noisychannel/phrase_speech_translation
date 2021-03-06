#!/usr/bin/env bash

l=${input}
lw=${input_weighted}
outputDir=${output_dir}
syms=${sym}
# Prune beam behaves erratically with 0 beam width
pruneBeam=`echo "$beam + 0.001" | bc`

echo $l
echo $outputDir
echo $syms

bname=${l##*/}
fstcompose $l $outputDir/S.sort.fst \
  | fstproject | fstprint | fstcompile | fstprune --weight=$pruneBeam | fstprint \
  | awk '{if (NF == 5) {$5 = ""}; print $_}' | sed 's: *$::g' \
  | fstcompile --arc_type=log | fstarcsort \
  | fstcompose $lw - | fstprint | fstcompile | fstprune --weight=0.001 | fstrmepsilon \
  | fstminimize | fstdeterminize \
  | /export/a04/gkumar/code/custom/phrase_speech_translation/util/fstprintstring - $syms \
  >> $outputDir/1best/$bname.1best
