#!/usr/bin/env python

"""
An FST based featurized decoder for phrase based speech translation

Author : Gaurav Kumar (Johns Hopkins University)
"""

import argparse
import codecs
import os
import sys

parser = argparse.ArgumentParser("Extracts features from a Moses phrase table")
parser.add_argument("-p", "--phraselat-dir", dest="phraseLatDir", help="The location of the phrase lattices that contain the ASR weights")
parser.add_argument("-c", "--config", dest="config", help="The decoder config file, contains weights only")
parser.add_argument("-f", "-feats", dest="phraseFeats", help="The file containing the phrase features")
parser.add_argument("-o", "--output-dir", dest="outputDir", help="The output directory")
parser.add_argument("-s", "--syms", dest="symFile", help="The symbol table")
parser.add_argument("-a", "--asr", dest="asrBest", help="The ASR one best output")
parser.add_argument("-n", "--nbest_source", dest="nBestSource", help="The nbest file for tuning")
parser.add_argument("-u", "--nbest_count", dest="nBestCounts", help="The count of nbest entries")
parser.add_argument("-t", "--nbest_target", dest="nBestTarget", help="The translated n-best file")
parser.add_argument("-k", "--known_oovs", dest="knownOOVs", help="A list of known-OOV symbols")
opts = parser.parse_args()

if opts.phraseLatDir is None or opts.config is None:
  parser.print_help()
  sys.exit(1)

# 1. Read the feats file, create W_mt, take inspiration from phrase2FST
# 2. Keep, the phrase features in memory

phraseFeats = codecs.open(opts.phraseFeats, encoding="utf8")
FSTFile = open(opts.outputDir + "/W_mt.fst.txt", "w+")
weightsFile = open(opts.config)

# Read and store known-OOVs if they exist
knownOOVs = []
if opts.knownOOVs is not None:
    with open(opts.knownOOVs) as f:
        for l in f:
            knownOOVs.append(l.strip())

vocabulary = {}
# Read external symbol file first (if available)
if opts.symFile is not None:
  symFile = codecs.open(opts.symFile, encoding="utf8")
  for line in symFile:
    lineDetails = line.strip().split()
    # Expected format : symbol id
    vocabulary[lineDetails[0]] = int(lineDetails[1])
  symFile.close()
else:
  parser.print_help()
  sys.exit(1)

# Write final state to the FST
FSTFile.write("0\n")
# Write the closure arc
FSTFile.write("1 0 0 0\n")

def getVocabID(word):
  """
  Returns the vocabulary ID of the word argument
  If the word is not in the vocabulary, it is added
  """
  return str(vocabulary[word])

weights = []
# Read weights : one per line
for line in weightsFile:
  weights.append(float(line.strip().split()[1]))

assert len(weights) == 6
# 0-3 : Phrase features
# 4 : OOV feature
# The last weight is the ASR weight which is fixed to 1.0

# Don't penalize the ASR system for producing known OOVs
for sym in knownOOVs:
    FSTFile.write("0 1 " + sym + " 0 0\n")

sourcePhrases = {}
# Get the source side phrases from the phrase table
for line in phraseFeats:
  # Split phrase pair
  phraseInfo = line.split("\t")
  sourcePhrase = phraseInfo[0].strip()
  feats = phraseInfo[1:]
  feats = [float(x) for x in feats]
  # Add a non-OOV feature
  feats.append(0.0)
  # Add a non-tunable dummy ASR feature
  feats.append(0.0)
  assert len(feats) == len(weights)
  cost = sum([float(feats[i]) * weights[i] for i in range(len(weights))])
  FSTFile.write("0 1 " + getVocabID("_".join(sourcePhrase.split())) + " " + getVocabID("_".join(sourcePhrase.split())) + " " + str(cost) + "\n")
  sourcePhrases["_".join(sourcePhrase.split())] = feats

# The second feature approximates the unigram feature
# for an instance that only occurs once
sourcePhrases["OOV"] = [1., 14.00, 0.0, 0.0, 1.0, 0.0]
# Write the OOV arcs
FSTFile.write("0 1 999999 999999 " + str(sum([float(sourcePhrases["OOV"][i]) * weights[i] for i in range(len(weights))])) + "\n")

FSTFile.close()
phraseFeats.close()
weightsFile.close()

# 3. Call a helper file that does the following : Composition with P \forall L, shortestpath (n?), 
# !!! How do you print n shortest paths : FST randgen outputs different files
# Project input for the n-best output
# Project output to look up the phrase features

os.system("mt_util/decoder_util/decodeMultipleSentences.sh " + opts.phraseLatDir + " " + opts.outputDir + " " + opts.outputDir + "/W_mt.fst.txt " + opts.symFile)
asrBest = codecs.open(opts.asrBest, encoding="utf8")

# Read the n-best file and store
nBestTrans = {}
nBestCounts = open(opts.nBestCounts)
nBestSource = codecs.open(opts.nBestSource, encoding="utf8")
nBestTarget = codecs.open(opts.nBestTarget, encoding="utf8")
for lineNo, count in enumerate(nBestCounts):
  actualLineNo = lineNo + 1
  nBestTrans[actualLineNo] = {}
  for _ in range(int(count)):
    nBestTrans[actualLineNo][nBestSource.readline().strip()] = nBestTarget.readline().strip()

output = codecs.open(opts.outputDir + "/nbest.result", "w+", encoding="utf8")
for lineNo, line in enumerate(asrBest):
  actualLineNo = lineNo + 1
  line = line.strip()

  if line == "":
    line = "NO_TRANSLATION"
    lineTrans = "NO_TRANSLATION"
  else:
    lineTrans = nBestTrans[actualLineNo][line] if line in nBestTrans[actualLineNo] else "NO_TRANSLATION"

  if os.path.exists(opts.outputDir + "/nbest/" + str(actualLineNo) + ".lat.nbest"):
    if os.stat(opts.outputDir + "/nbest/" + str(actualLineNo) + ".lat.nbest").st_size == 0:
      output.write(str(lineNo) + " ||| " + lineTrans + " ||| " + " ".join(["100.0" for _ in range(len(weights))]) + "\n")
      continue

    f = codecs.open(opts.outputDir + "/nbest/" + str(actualLineNo) + ".lat.nbest", encoding="utf8")
    for hyp in f:
      if hyp.strip() == "|||":
        output.write(str(lineNo) + " ||| " + lineTrans + " ||| " + " ".join(["100.0" for _ in range(len(weights))]) + "\n")
        continue

      hypComp = hyp.strip().split("|||")
      inputHyp = hypComp[0].strip()
      phraseComp = hypComp[1].strip().split()
      latScore = float(hypComp[2].strip())
      scores = [0.0 for _ in range(len(weights))]
      for phrase in phraseComp:
        scores = [scores[i] + sourcePhrases[phrase.strip()][i] for i in range(len(scores))]
      # Replace the final score with the actual ASR score
      asrScore = latScore - sum([scores[i] * weights[i] for i in range(len(weights))])
      scores[-1] = asrScore / weights[-1]

      if not inputHyp or inputHyp is None:
        inputHyp = line
        inputTrans = lineTrans
        scores = ["100.0" for _ in range(len(weights))]
      else:
        inputTrans = nBestTrans[actualLineNo][inputHyp] if inputHyp in nBestTrans[actualLineNo] else "NO_TRANSLATION"

      output.write(str(lineNo) + " ||| " + inputTrans + " ||| " + " ".join([str(x) for x in scores]) + "\n")

  else:
    output.write(str(lineNo) + " ||| " + lineTrans + " ||| " + " ".join(["100.0" for _ in range(len(weights))]) + "\n")

output.close()
asrBest.close()
