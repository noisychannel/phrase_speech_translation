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
opts = parser.parse_args()

if opts.phraseLatDir is None or opts.config is None:
  parser.print_help()
  sys.exit(1)

# 1. Read the feats file, create W_mt, take inspiration from phrase2FST
# 2. Keep, the phrase features in memory

phraseFeats = codecs.open(opts.phraseFeats, encoding="utf8")
FSTFile = open(opts.outputDir + "/W_mt.fst.txt", "w+")
weightsFile = open(opts.config)

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
# Write the OOV arc
#FSTFile.write("0 1 999999 999999 13.0\n")
FSTFile.write("0 1 999999 999999 0.0\n")

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

sourcePhrases = {}
# Get the source side phrases from the phrase table
for line in phraseFeats:
  # Split phrase pair
  phraseInfo = line.split("\t")
  sourcePhrase = phraseInfo[0].strip()
  feats = phraseInfo[1:]
  feats = [float(x) for x in feats]
  cost = sum([float(feats[i]) * weights[i] for i in range(len(weights))])
  FSTFile.write("0 1 " + getVocabID("_".join(sourcePhrase.split())) + " " + getVocabID("_".join(sourcePhrase.split())) + " " + str(cost) + "\n")
  sourcePhrases["_".join(sourcePhrase.split())] = feats

sourcePhrases["OOV"] = [1., 2.0, 0.0, 0.0]

FSTFile.close()
phraseFeats.close()
weightsFile.close()

# 3. Call a helper file that does the following : Composition with P \forall L, shortestpath (n?), 
# !!! How do you print n shortest paths : FST randgen outputs different files
# Project input for the n-best output
# Project output to look up the phrase features

os.system("mt_util/decoder_util/decodeMultipleSentences.sh " + opts.phraseLatDir + " " + opts.outputDir + " " + opts.outputDir + "/W_mt.fst.txt " + opts.symFile)
print opts.asrBest
asrBest = codecs.open(opts.asrBest, encoding="utf8")

output = codecs.open(opts.outputDir + "/nbest.result", "w+", encoding="utf8")
for lineNo, line in enumerate(asrBest):
  line = line.strip()
  if line == "":
    line = "NO_TRANSLATION"
  actualLineNo = lineNo + 1

  if os.path.exists(opts.outputDir + "/nbest/" + str(actualLineNo) + ".lat.nbest"):
    if os.stat(opts.outputDir + "/nbest/" + str(actualLineNo) + ".lat.nbest").st_size == 0:
      output.write(str(lineNo) + " ||| " + line + " ||| " + " ".join(["100.0" for _ in range(len(weights))]) + "\n")
      continue

    f = codecs.open(opts.outputDir + "/nbest/" + str(actualLineNo) + ".lat.nbest", encoding="utf8")
    for hyp in f:
      if hyp.strip() == "|||":
        output.write(str(lineNo) + " ||| " + line + " ||| " + " ".join(["100.0" for _ in range(len(weights))]) + "\n")
        continue

      hypComp = hyp.strip().split("|||")
      inputHyp = hypComp[0].strip()
      phraseComp = hypComp[1].strip().split()
      scores = [0.0 for _ in range(len(weights))]
      for phrase in phraseComp:
        scores = [scores[i] + sourcePhrases[phrase.strip()][i] for i in range(len(scores))]
      if not inputHyp or inputHyp is None:
        inputHyp = line
        scores = ["100.0" for _ in range(len(weights))]
      output.write(str(lineNo) + " ||| " + inputHyp + " ||| " + " ".join([str(x) for x in scores]) + "\n")

  else:
    output.write(str(lineNo) + " ||| " + line + " ||| " + " ".join(["100.0" for _ in range(len(weights))]) + "\n")

output.close()
asrBest.close()
