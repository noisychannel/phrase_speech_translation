#!/usr/bin/env bash
# Author : Gaurav Kumar, Johns Hopkins University 
# Creates OpenFST lattices from Kaldi lattices
# This script needs to be run from one level above this directory

# Derived from the Kaldi recipe for Fisher Spanish (KALDI_TRUNK/egs/fisher_callhome_spanish/s5/local)

if [ $# -lt 5 ]; then
  echo "Usage : asr_util/kaldi2FST.sh [KALDI_ROOT] [LatticeDir] [DecodeDir] [AcousticScale] [SYMTABLE]"
  echo "Enter the latdir (where the lattices will be put), the decode dir containing lattices, the acoustic scale and the symbol table"
  exit 1
fi

prunebeam=2
maxProcesses=5

KALDI_ROOT=$1
latdir=$2
decode_dir=$3
acoustic_scale=$4
symtable=$5
#latdir="latjosh-2-callhome"
#decode_dir=exp/tri5a/decode_$partition
#acoustic_scale=0.077

if [ ! -d $KALDI_ROOT ]
then
  echo "Invalid Kaldi Root ($KALDI_ROOT) specified"
  exit 1;
fi

stage=4

if [ -d $decode_dir ]
then
  # TODO:Add scaling factor for weights, how?
  rawLatDir="lattices-raw"
  compiledLatDir="lattices-bin"
  preplfLatDir="lattices-pushed"

  mkdir -p $latdir
  mkdir -p $latdir/$rawLatDir
  mkdir -p $latdir/$compiledLatDir
  mkdir -p $latdir/$preplfLatDir

  runningProcesses=0
  for l in $decode_dir/lat.*.gz
  do	
    (
    # Extract file name and unzip the file first
    bname=${l##*/}
    bname="$latdir/${bname%.gz}"
    gunzip -c $l > "$bname.bin"

    if [ $stage -le 1 ]; then

      # Now copy into ark format
      $KALDI_ROOT/src/latbin/lattice-copy ark:$bname.bin ark,t:- > "$bname.raw"

      # Prune lattices
      $KALDI_ROOT/src/latbin/lattice-prune --acoustic-scale=$acoustic_scale --beam=$prunebeam ark:"$bname.raw" ark:"$bname.pruned"

      # Convert to an openfst compatible format
      $KALDI_ROOT/src/latbin/lattice-to-fst --lm-scale=1.0 --acoustic-scale=$acoustic_scale ark:$bname.raw ark,t:$bname.ark.fst	

    fi

    if [ $stage -le 1 ]; then
      fileName=""
      fileLine=0

      while read line; do
        if [ $fileLine = 0 ]; then
          fileName="$line"
          fileLine=1
          continue
        fi
        if [ -z "$line" ]; then
          fileLine=0
          continue
        fi
        # Replace laugh, unk, oov, noise with eps
        #echo "$line" | awk '{if ($3 == 2035 || $3 == 2038 || $3 == 2039 || $3 == 2040) {$3 = 0; $4 = 0} print}' >> "$latdir/$rawLatDir/$fileName.lat"
        #echo "$line" | awk -F'\t' -v OFS='\t' '{if (NF > 2 && $3 <= 5) {$3 = 0; $4 = 0} print}' >> "$latdir/$rawLatDir/$fileName.lat"
        #(gkumar) : This script is no longer responsible for removing special words.
        #           This should be handled via some form of postprocessing.
        echo "$line" >> "$latdir/$rawLatDir/$fileName.lat"
      done < $bname.ark.fst
      echo "Done isolating lattices"
    fi
    ) &	
    runningProcesses=$((runningProcesses+1))
    echo "#### Processes running = " $runningProcesses " ####"
    if [ $runningProcesses -eq $maxProcesses ]; then
      echo "#### Waiting for slot ####"
      wait
      runningProcesses=0
      echo "#### Done waiting ####"
    fi
  done
  wait
  rm $latdir/*.bin
  rm $latdir/*.pruned


  if [ $stage -le 2 ]; then
    #Compile lattices
    runningProcesses=0
    for l in $latdir/$rawLatDir/*.lat
    do
      (
      # Arc type needs to be log
      bname=${l##*/}
      # Pruning above doesn't work, and you can't prune when in log mode, so we have this
      cat $latdir/$rawLatDir/$bname \
        | fstcompile | fstprune --weight=$prunebeam | fstprint \
        | fstcompile --arc_type=log - $latdir/$compiledLatDir/$bname
      ) &
      runningProcesses=$((runningProcesses+1))
      echo "#### Processes running = " $runningProcesses " ####"
      if [ $runningProcesses -eq $maxProcesses ]; then
        echo "#### Waiting for slot ####"
        wait
        runningProcesses=0
        echo "#### Done waiting ####"
      fi
    done
    wait
    echo "Done compiling lattices."
  fi

  if [ $stage -le 3 ]; then
    # Create a dummy FST with one state and no arcs first
	  cat > sos.txt <<EOF
1 2 <s> <s>
2
EOF
	  cat > eos.txt <<EOF
1 2 </s> </s>
2 
EOF
	for prefix in sos eos; do
      cat $prefix.txt | fstcompile --isymbols=$symtable --osymbols=$symtable --arc_type=log > $prefix.fst
	done

    runningProcesses=0
    for l in $latdir/$compiledLatDir/*.lat
    do
      (
      bname=${l##*/}

      cat $latdir/$compiledLatDir/$bname \
		  | fstrmepsilon \
		  | fstdeterminize | fstminimize \
		  | fstpush --push_weights --remove_total_weight \
		  | fstconcat sos.fst - \
		  | fstconcat - eos.fst \
		  | fstrmepsilon \
		  > $latdir/$preplfLatDir/$bname
      ) &
      runningProcesses=$((runningProcesses+1))
      echo "#### Processes running = " $runningProcesses " ####"
      if [ $runningProcesses -eq $maxProcesses ]; then
        echo "#### Waiting for slot ####"
        wait
        runningProcesses=0
        echo "#### Done waiting ####"
      fi
    done
    wait
    # Let's take a moment to thank the dummy FST for playing its
    # part in this process. However, it has to go now. 
    rm $latdir/$preplfLatDir/dummy.fst
    echo "Done performing fst push (initial state)"
  fi

  # Produce the PLFs
  if [ $stage -le 4 ]; then
    mkdir -p $latdir/plf
    for l in $latdir/$preplfLatDir/*.lat
    do
      (
      bname=${l##*/}
      plfname=$(basename $bname .lat).plf
      cat $latdir/$preplfLatDir/$bname \
        | fsttopsort \
        | fstprint --isymbols=$symtable --osymbols=$symtable \
        | $(dirname $0)/txt2plf.pl \
        > $latdir/plf/$plfname
      ) &
      runningProcesses=$((runningProcesses+1))
      echo "#### Processes running = " $runningProcesses " ####"
      if [ $runningProcesses -eq $maxProcesses ]; then
        echo "#### Waiting for slot ####"
        wait
        runningProcesses=0
        echo "#### Done waiting ####"
      fi
    done
    wait
    echo "Done building PLFs"
    outFileName=`basename $latdir`
    for i in $latdir/plf/*.plf; do con=`cat $i`; echo -e "`basename ${i}`\t${con}"; done > $latdir/${outFileName}.plf
    echo "Done consolidating PLFs"
  fi
else
  echo "Complete training and decoding first"
fi
