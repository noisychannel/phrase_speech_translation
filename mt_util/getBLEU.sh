#!/usr/bin/env bash

input=$1
reference=$2

sed -i "s:^ *::g" $input
sed -i "s: *$::g" $input

$MOSES/scripts/generic/multi-bleu.perl $reference < $input
