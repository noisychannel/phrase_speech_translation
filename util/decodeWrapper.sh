#!/usr/bin/env bash

cd /export/a04/gkumar/code/custom/phrase_speech_translation
expDir=exp/new-mert.4.decode.dev2
tunedExpDir=exp/new-mert.4

mt_util/decoder.py \
  -p $expDir/decoder/lat \
  -c $tunedExpDir/SDecoder_cfg.txt.ZMERT.final \
  -f data/mt/phrase_feats.tune.dev2 \
  -o $expDir/decoder/ \
  -s $expDir/decoder/pre/syms.txt \
  -a data/asr/dev2/1best/asr.1best.clean \
  -k $expDir/decoder/pre/known_oov.txt > $expDir/decoder/decoder.out

#asr_util/cleanASROutput.sh $expDir/decoder/nbest.result
cd $expDir/decoder
cp nbest.result ../nbest.out

# Create a timstamped directory and put the contents in there
arkDir=$(date -d "today" +"%Y%m%d%H%M")
mkdir $arkDir

mv decode_log $arkDir/
mv latFinal $arkDir/
mv nbest $arkDir/
mv nbest.result $arkDir/
mv W_close.fst $arkDir/
mv W_mt.fst.txt $arkDir/
mv decoder.out $arkDir/

cd ..
