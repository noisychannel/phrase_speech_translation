#!/usr/bin/env bash

l=${input}
s=${seg}
outputDir=${output_dir}
syms=${sym}

echo $l
echo $s
echo $outputDir
echo $syms

bname=${l##*/}
fstcompose $l $s | fstrmepsilon \
  | fstminimize > $outputDir/lat/$bname
