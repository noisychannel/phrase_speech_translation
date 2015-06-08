#!/bin/bash

# ASR config
KALDI_DIR=/export/a04/gkumar/code/kaldi-new
ASR_DATA_DIR=/export/a04/gkumar/code/custom/phrase_speech_translation/data/asr
ASR_MODEL_DIR=/export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri6a_dnn
ASR_SYM_TABLE=/export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt
AC_SCALE=0.067
# Dataset (Fisher config)
FISHER_SPLITS=/export/a04/gkumar/corpora/fishcall/jack-splits/split-matt
FISHER_TIME=/export/a04/gkumar/corpora/fishcall/fisher/tim
# MT config
MT_EXP_DIR=/export/a04/gkumar/experiments/is2015
MT_DATA_DIR=/export/a04/gkumar/code/custom/phrase_speech_translation/data/mt
# TUNING config
EXP_DIR=/export/a04/gkumar/code/custom/phrase_speech_translation/exp
LOG_DIR=/export/a04/gkumar/code/custom/phrase_speech_translation/log

asr:
	# Get the lattices from Kaldi for each dataset that has been decoded
	# dev, dev2 and test : Fisher
	# Acoustic scale set to 1/W, where W led to the best WER
	# --- The symbols for laugh, noise and OOV , <unk> are hardcoded in the Kaldi2FST script. You should replace them (2035, 2038, 2039, 2040 in the default recipe)
	# since they get replaced with eplison upon conversion
	# --- Pruned with a beam width of 13.0
	for part in dev dev2 test; do \
		asr_util/kaldi2FST.sh $(KALDI_DIR) $(ASR_DATA_DIR)/$$part/lattices $(ASR_MODEL_DIR)/decode_$$part $(AC_SCALE); \
	done
	# Get nbest files
	for part in dev dev2 test; do \
		asr_util/kaldi2NBest.sh $(KALDI_DIR) $(ASR_DATA_DIR)/$$part/nbest $(ASR_MODEL_DIR)/decode_$$part $(AC_SCALE) $(ASR_SYM_TABLE); \
	done
	# Merge 1best files based on timing information
	for part in dev dev2 test; do \
		asr_util/merge1Best.py -i $(ASR_MODEL_DIR)/decode_$$part/scoring/15.tra -s $(ASR_SYM_TABLE) -c $(FISHER_SPLITS)/$$part \
			-o $(ASR_DATA_DIR)/$$part/1best -t $(FISHER_TIME); \
	done
	# Get the nbest files based on timing information
	# awk '{s+=$1} END {print s}' asr.ncount
	# to verify if the counts match the nbest hyps
	for part in dev dev2 test; do \
		asr_util/mergeNBest.py -i $(ASR_DATA_DIR)/$$part/nbest/all.nbest -c $(FISHER_SPLITS)/$$part -o $(ASR_DATA_DIR)/$$part/nbest -t $(FISHER_TIME); \
	done
	# Clean the 1-best files
	# Clean the n-best files
	for part in dev dev2 test; do \
		asr_util/cleanASROutput.sh $(ASR_DATA_DIR)/$$part/1best/asr.1best > $(ASR_DATA_DIR)/$$part/1best/asr.1best.clean; \
		asr_util/cleanASROutput.sh $(ASR_DATA_DIR)/dev/nbest/asr.nbest > $(ASR_DATA_DIR)/dev/nbest/asr.nbest.clean; \
	done
	# Generate reference for the n-best files
	# Make sure that the reference exists
	for part in dev dev2 test; do \
		for refID in 0 1 2 3; do \
			asr_util/replicateReference.py -c $(ASR_DATA_DIR)/$$part/nbest/asr.ncount \
				-r $(ASR_DATA_DIR)/$$part/ref/fisher_$$part.tok.lc.en.$$refID -o $(ASR_DATA_DIR)/$$part/nbest/nbest.en.$$refID; \
		done \
	done
	# Merge lattices
	for part in dev dev2 test; do \
		asr_util/mergeLattices.py -l $(ASR_DATA_DIR)/$$part/lattices/lattices-pushed \
			-s $(ASR_SYM_TABLE) -c $(FISHER_SPLITS)/$$part -o $(ASR_DATA_DIR)/$$part/mergedLat -t $(FISHER_TIME); \
	done
	# Remove weights from lattices (needed for some experiments)
	for part in dev dev2 test; do \
		asr_util/removeLatWeights.sh $(ASR_DATA_DIR)/$$part/mergedLat/finalLat $(ASR_DATA_DIR)/$$part/mergedLat/noWeightLat; \
	done


plf:
	# (OPTIONAL)
	# Merge lattices based on timing information available
	# Convert to PLF
	for part in dev dev2 test; do \
		asr_util/mainPLF.py -l $(ASR_DATA_DIR)/$$part/lattices/lattices-pushed \
		-s $(ASR_SYM_TABLE) -c $(FISHER_SPLITS)/$$part -o $(ASR_DATA_DIR)/$$part/plf -t $(FISHER_TIME); \
	done


mt:
	###############
	# MT Steps
	###############
	# Decode n-best list
	# EXP IDs : 8 : dev, 6 : dev2, 7 : test
	nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/8 \
		$(ASR_DATA_DIR)/dev/nbest/asr.nbest.clean $(MT_EXP_DIR)/5/moses.tuned.ini \
		$(MT_EXP_DIR)/5/model
	nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/6 \
		$(ASR_DATA_DIR)/dev2/nbest/asr.nbest.clean $(MT_EXP_DIR)/5/moses.tuned.ini \
		$(MT_EXP_DIR)/5/model
	nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/7 \
		$(ASR_DATA_DIR)/test/nbest/asr.nbest.clean $(MT_EXP_DIR)/5/moses.tuned.ini \
		$(MT_EXP_DIR)/5/model
	# Create a phrase table that does not use smoothing
	# Filter phrase table based on the dataset
	for part in dev dev2 test; do \
		mt_util/filterPhraseTable.sh $(MT_DATA_DIR)/table_$$part \
			$(ASR_DATA_DIR)/$$part/nbest/asr.nbest.clean \
			$(MT_EXP_DIR)/4/tuning/moses.tuned.ini.1 \
			$(MT_EXP_DIR)/4/model; \
	done
	# Extract features from the phrase table, use filtered phrase tables
	for part in dev dev2 test; do \
		time mt_util/extractPhraseFeats.py -p $(MT_DATA_DIR)/table_$$part/evaluation/test.filtered.1/phrase-table.0-0.1.1.gz -o $(MT_DATA_DIR)/phrase_feats.$$part; \
	done
	# Convert the feat file to an FST, requires a weight file
	# Compile the segmentation transducer
	for part in dev dev2 test; do \
		time mt_util/phrase2FST.py \
			-p $(MT_DATA_DIR)/phrase_feats.$$part \
			-f $(EXP_DIR)/1_$$part/S.$$part.fst.txt \
			-s $(EXP_DIR)/1_$$part/syms.$$part.txt \
			-e $(ASR_SYM_TABLE) -w $(EXP_DIR)/1_$$part/weight.init; \
		fstcompile --arc_type=log $(EXP_DIR)/1_$$part/S.$$part.fst.txt $(EXP_DIR)/1_$$part/S.$$part.fst; \
	done


# After running experiments decode using 
# nohup mt_util/tune.sh data/asr/dev2/mergedLat/finalLat/ exp/new-mert.4.decode.dev2 data/mt/phrase_feats.tune.dev2 /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt log > decode.dev2.log &
# nohup mt_util/tune.sh data/asr/test/mergedLat/finalLat/ exp/new-mert.4.decode.test data/mt/phrase_feats.tune.test /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt log > decode.test.log &
#
#

#len-feat:
	############# LENGTH BASED FEATURES #################
	## Create phrase lattices
	#for part in dev dev2 test; do \
		#nohup mt_util/createPhraseLattice.sh $(ASR_DATA_DIR)/$$part/mergedLat/noWeightLat/ \
			#$(EXP_DIR)/1_$$part/S.$$part.fst $(ASR_SYM_TABLE) $(EXP_DIR)/1_$$part/res > $(LOG_DIR)/pl.$$part.1.log &; \
	#done
	#wait;
	## Extract the 1-best lat files 
	#for part in dev dev2 test; do \
		#mt_util/get1Best.py -i $(EXP_DIR)/1_$$part/res/1best -a $(ASR_DATA_DIR)/$$part/1best/asr.1best.clean -o $(EXP_DIR)/1_$$part/res/1best/$$part.lat.1best; \
	#done
	## Decode the results
	#nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/13 \
		#$(EXP_DIR)/1_dev2/res/1best/dev2.lat.1best \
		#$(MT_EXP_DIR)/5/tuning/moses.tuned.ini.1 \
		#$(MT_EXP_DIR)/5/model > $(LOGDIR)/decode.lenfeat.dev2.out &
	#nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/14 \
		#$(EXP_DIR)/1_test/res/1best/test.lat.1best \
		#$(MT_EXP_DIR)/5/tuning/moses.tuned.ini.1 \
		#$(MT_EXP_DIR)/5/model > $(LOGDIR)/decode.lenfeat.test.out &
	#wait;

#asr-draws:
	############# ASR DRAWS #################
	## Create phrase lattices
	#for part in dev2 test; do \
		#nohup mt_util/asrDrawsMain.sh $(ASR_DATA_DIR)/$$part/mergedLat/noWeightLat/ $(ASR_DATA_DIR)/$$part/mergedLat/finalLat \
			#$(EXP_DIR)/1_$$part/S.$$part.fst $(ASR_SYM_TABLE) \
			#$(EXP_DIR)/2_$$part/res > $(LOGDIR)/pl.$$part.2.log &;\
	#done
	#wait;
	## Extract the 1-best lat files 
	#for part in dev2 test; do \
		#mt_util/get1Best.py -i $(EXP_DIR)/2_$$part/res/1best -a $(ASR_DATA_DIR)/$$part/1best/asr.1best.clean -o $(EXP_DIR)/2_$$part/res/1best/$$part.lat.1best;\
	#done
	## Decode the results
	#nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/15 \
		#$(EXP_DIR)/2_dev2/res/1best/dev2.lat.1best \
		#$(MT_EXP_DIR)/5/tuning/moses.tuned.ini.1 \
		#$(MT_EXP_DIR)/5/model > $(LOGDIR)/decode.asrdraws.dev2.out &
	#nohup mt_util/mosesFilterDecode.sh $(MT_EXP_DIR)/16 \
		#$(EXP_DIR)/2_test/res/1best/test.lat.1best \
		#$(MT_EXP_DIR)/5/tuning/moses.tuned.ini.1 \
		#$(MT_EXP_DIR)/5/model > $(LOGDIR)/decode.asrdraws.test.out &
	#wait;


#other-exp:
	######### Experiment 3,4,5,6 ##############
	##!/usr/bin/env bash
	######### Experiment 3 : 0 1 0 0 0 ##############
	#exp=3
	#mt1=17
	#mt2=18
	#time mt_util/phrase2FST.py \
		#-p data/mt/phrase_feats.dev2 \
		#-f exp/${exp}_dev2/S.dev2.fst.txt \
		#-s exp/${exp}_dev2/syms.dev2.txt \
		#-e /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt \
		#-w exp/${exp}_dev2/weights.init
	#time mt_util/phrase2FST.py \
		#-p data/mt/phrase_feats.test \
		#-f exp/${exp}_test/S.test.fst.txt \
		#-s exp/${exp}_test/syms.test.txt \
		#-e /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt \
		#-w exp/${exp}_test/weights.init
	## Compile the segmentation transducer
	#fstcompile --arc_type=log exp/${exp}_dev2/S.dev2.fst.txt exp/${exp}_dev2/S.dev2.fst
	#fstcompile --arc_type=log exp/${exp}_test/ S.test.fst.txt exp/${exp}_test/S.test.fst
	## Create phrase lattices
	#mt_util/createPhraseLattice.sh data/asr/dev2/mergedLat/noWeightLat/ \
		#exp/${exp}_dev2/S.dev2.fst /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt \
		#exp/${exp}_dev2/res
	#mt_util/createPhraseLattice.sh data/asr/test/mergedLat/noWeightLat/ \
		#exp/${exp}_test/S.test.fst /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt \
		#exp/${exp}_test/res
	## Extract the 1-best lat files 
	#mt_util/get1Best.py -i exp/${exp}_dev2/res/1best -a data/asr/dev2/1best/asr.1best.clean -o exp/${exp}_dev2/res/1best/dev2.lat.1best
	#mt_util/get1Best.py -i exp/${exp}_test/res/1best -a data/asr/test/1best/asr.1best.clean -o exp/${exp}_test/res/1best/test.lat.1best
	#(
	#mt_util/mosesFilterDecode.sh /export/a04/gkumar/experiments/is2015/$mt1 \
		#/export/a04/gkumar/code/custom/phrase_speech_translation/exp/${exp}_dev2/res/1best/dev2.lat.1best \
		#/export/a04/gkumar/experiments/is2015/5/tuning/moses.tuned.ini.1 \
		#/export/a04/gkumar/experiments/is2015/5/model
	#) &
	#(
	#mt_util/mosesFilterDecode.sh /export/a04/gkumar/experiments/is2015/$mt2 \
		#/export/a04/gkumar/code/custom/phrase_speech_translation/exp/${exp}_test/res/1best/test.lat.1best \
		#/export/a04/gkumar/experiments/is2015/5/tuning/moses.tuned.ini.1 \
		#/export/a04/gkumar/experiments/is2015/5/model
	#) &
	#wait
	#echo "Done."
	###############
	## Interface steps
	## ############
	## To get sentence level BLEU
	#/export/a04/gkumar/code/mosesdecoder/bin/sentence-bleu refs... < cand
	#################
	## Tuning
	################
	#nohup mt_util/tune.sh data/asr/dev/mergedLat/finalLat/ exp/tune data/mt/phrase_feats.tune.dev /export/a04/gkumar/code/kaldi-new/egs/fisher_callhome_spanish/s5/exp/tri5a/graph/words.txt log > tune_pre.log &
	#mt_util/decoder.py -p exp/tune/lat/ -c config.dummy -f data/mt/phrase_feats.tune.dev -o exp/tune/ -s exp/tune/pre/syms.txt
