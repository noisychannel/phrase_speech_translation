#!/usr/bin/env python

import sys
import os
import argparse
from scipy.optimize import minimize

parser = argparse.ArgumentParser("Tunes phrase lattice features")
parser.add_argument("-o", "--out_dir", dest="outDir", help="The location of the output directory")
parser.add_argument("-a", "--asr_best", dest="asrBest", help="The 1best file for tuning")
parser.add_argument("-n", "--nbest", dest="nBest", help="The nbest file for tuning")
parser.add_argument("-c", "--nbest_count", dest="nBestCounts", help="The count of nbest entries")
parser.add_argument("-s", "--nbest_scores", dest="nBestScoresFile", help="The BLEU+1 scores for the nbest file")
parser.add_argument("-e", "--symtable", dest="symtable", help="The Symbol table for the segmentation transducer")
parser.add_argument("-l", "--lat_dir", dest="latDir", help="The location word lattices")
opts = parser.parse_args()

callID=0

if opts.outDir is None:
  parser.print_help()
  sys.exit(1)

os.system("mkdir -p " + opts.outDir)

# First read the nbest file and store the scores
nBestScores = {}
nBestCounts = open(opts.nBestCounts)
nBest = open(opts.nBest)
nBestScoresFile = open(opts.nBestScoresFile)
for lineNo, count in enumerate(nBestCounts):
  nBestScores[lineNo] = {}
  for _ in range(int(count)):
    nBestScores[lineNo][nBest.readline()] = float(nBestScoresFile.readline())


def costFunction(weights):
  global callID
  callID += 1
  os.system("mkdir -p " + opts.outDir + "/" + str(callID))
  weightFile = open(opts.outDir + "/" + str(callID) + "/weights." + str(callID), "w+")
  # get the weights, write to file
  for weight in weights:
    weightFile.write(str(weight) + "\n")
  weightFile.close()

  # recreate S
  os.system("mt_util/phrase2FST.py -p data/mt/phrase_feats -f " + opts.outDir + "/" + str(callID) + "/S.fst.txt " +
              "-s " + opts.outDir + "/" + str(callID) + "/syms.txt " +
              "-e " + opts.symtable + " " +
              "-w " + opts.outDir + "/" + str(callID) + "/weights." + str(callID))

  # Compile S
  os.system("fstcompile --arc_type=log " + opts.outDir + "/" + str(callID) + "/S.fst.txt " + opts.outDir + "/" + str(callID) + "/S.fst")

  # recreate P
  os.system("mt_util/createPhraseLattice.sh " + opts.latDir + " " +
              opts.outDir + "/" + str(callID) + "/S.fst " + opts.symtable + " " +
              opts.outDir + "/" + str(callID) + "/res >> log/tuning.p.log &")

  # Get 1-best
  os.system("mt_util/get1Best.py -i " + opts.outDir + "/" + str(callID) + "/res " +
    "-a " + opts.asrBest + " -o " + opts.outDir + "/" + str(callID) + "/lat.1best")

  # Calculate score with respect to the n-best file
  scores = []
  oneBest = open(opts.outDir + "/" + str(callID) + "/lat.1best")
  for lineNo, line in enumerate(oneBest):
    if line in nBestScores[lineNo]:
      scores.append(nBestScores[lineNo][line])

  # Return average cost
  return 1. - sum(scores) / float(len(scores))

x0 = [0.3, -0.1, -0.5, 1.3, 1.]
res = minimize(costFunction, x0, method='Powell', tol=1e-6, options={'disp': True})
