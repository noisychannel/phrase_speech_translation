#!/usr/bin/env bash

# Relabels OOVs and creates a single phrase lattice
# Typically used to create \tilde{P}_{ASR}

# NOTE : No minimiztion (or determinzation) is carried out here since it causes weights to change

l=${input}
s=${seg}
outputDir=${output_dir}
syms=${sym}
oovs=${oov}

echo $l
echo $s
echo $outputDir
echo $syms

bname=${l##*/}
fstrelabel --relabel_opairs=$oovs $l \
  | fstcompose - $s | fstrmepsilon > $outputDir/lat/$bname
  #| fstminimize > $outputDir/lat/$bname
