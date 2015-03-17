#!/usr/bin/env bash

dir=$1
input=$2
tuned_ini=$3

if [ $# -ne 3 ]; then
  echo "USAGE: ./mosesFilterDecode [outputDir] [input] [tuned_ini]"
  exit 1
fi

. ~/.bashrc

eval_dir=$dir/evaluation
mkdir -p $eval_dir
cd $dir

#Decode
$MOSES/scripts/generic/moses-parallel.pl \
  -decoder $MOSES/bin/moses \
  -config $3 \
  -i $2 \
  -jobs 12 \
  -queue-parameters '-q *@[b]* -pe smp 6' 1>$eval_dir/test.output

echo 'finished at '`date`
touch $eval_dir/DECODE.done
