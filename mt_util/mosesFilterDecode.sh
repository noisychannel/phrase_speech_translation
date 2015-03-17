#!/usr/bin/env bash

dir=$1
input=$2
tuned_ini=$3
model=$4

if [ $# -ne 4 ]; then
  echo "USAGE: ./mosesFilterDecode [outputDir] [input] [tuned_ini] [model]"
  exit 1
fi

external_bin_dir=/export/a04/gkumar/code/mosesdecoder/tools

. ~/.bashrc

eval_dir=$dir/evaluation
mkdir -p $eval_dir
cd $dir

touch $eval_dir/test.moses.table.ini.1

cp $input $eval_dir/test.input.tok.1

# Filter
$MOSES/scripts/training/train-model.perl \
  -mgiza -mgiza-cpus 8 -sort-buffer-size 10G -sort-compress gzip \
  -sort-parallel 8 -cores 8 -dont-zip -first-step 9 \
  -external-bin-dir $external_bin_dir \
  -f ar -e en -alignment grow-diag-final-and -max-phrase-length 5 \
  -reordering msd-bidirectional-fe -score-options '--GoodTuring' \
  -parallel -phrase-translation-table $model/phrase-table.1 \
  -reordering-table $model/reordering-table.1 \
  -config $eval_dir/test.moses.table.ini.1 \
  -lm 0:3:$eval_dir/test.moses.table.ini.1:8

$MOSES/scripts/training/filter-model-given-input.pl \
  $eval_dir/test.filtered.1 \
  $eval_dir/test.moses.table.ini.1 \
  $eval_dir/test.input.tok.1 \
  -Binarizer "$MOSES/bin/processPhraseTable"

rm $eval_dir/test.moses.table.ini.1

# Apply filter
$MOSES/scripts/ems/support/substitute-filtered-tables-and-weights.perl \
  $eval_dir/test.filtered.1/moses.ini \
  $model/moses.ini.1 \
  $tuned_ini \
  $eval_dir/test.filtered.ini.1


#Decode
$MOSES/scripts/generic/moses-parallel.pl \
  -decoder $MOSES/bin/moses \
  -config $eval_dir/test.filtered.ini.1 \
  -i $eval_dir/test.input.tok.1 \
  -jobs 24 \
  -queue-parameters '-q *@[b]* -pe smp 6' 1>$eval_dir/test.output

echo 'finished at '`date`
touch $eval_dir/DECODE.done
