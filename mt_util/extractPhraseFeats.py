#!/usr/bin/env python

"""
Extracts features from a Moses Phrase table

Author : Gaurav Kumar (Johns Hopkins University)
"""

import gzip
import argparse
import math

parser = argparse.ArgumentParser("Extracts features from a Moses phrase table")
parser.add_argument("-p", "--phrase-table", dest="phraseTable", help="The location of the phrase table")
parser.add_argument("-o", "--out-feats", dest="outFeats", help="The location of the output file for the features")
opts = parser.parse_args()

if opts.phraseTable is None or opts.outFeats is None:
  parser.print_help()
  sys.exit(1)

phraseTable = gzip.open(opts.phraseTable)
outFeats = codecs.open(opts.outFeats, "w+", encoding="utf8")

outFeatsList = []
totalSourcePhraseCounts = 0

def processPhrase(phrase, details):
  '''
  Features : 
  1. Length
  2. Phrase unigram probability
  3. Length normalized phrase unigram probability
  4. Phrase translation Entropy
  5. Lexical translation Entropy
  '''
  # Target, Source, Joint
  counts = details[0][2].strip().split()
  lenFeat = len(phrase)
  unnormalizedPhraseUnigram = math.log(counts[1])
  totalSourcePhraseCounts += counts[1]
  unnormalizedphraseUnigramLen = 1./lenFeat * phraseUnigram
  # Phrase table probabilities are in real space
  phraseEntropy = 0.
  lexEntropy = 0.
  for item in details:
    scores = item[0].strip().split()
    phraseEntropy += -1. * phraseEntropy * math.log(float(scores[2]))
    lexEntropy += -1. * phraseEntropy * math.log(float(scores[3]))
  outFeats.append([phrase, lenFeat, unnormalizedPhraseUnigram, unnormalizedphraseUnigramLen, phraseEntropy, lexEntropy])


def normalizeCountFeats():
  for feats in outFeatsList:
    feats[2] = feats[2] - math.log(totalSourcePhraseCounts)
    feats[3] = feats[3] - 1./feats[1] * math.log(totalSourcePhraseCounts)


def writeFeats():
  for feats in outFeatsList:
    strFeats = [str(x) for x in feats]
    outFeats.write("\t".join(strFeats) + "\n")


# Get the source side phrases from the phrase table
currentSourcePhrase = ""
currentPhraseDetails = []
for line in phraseTable:
  # Split phrase pair
  phraseInfo = line.split("|||")
  sourcePhrase = phraseInfo[0].strip()
  if sourcePhrase == currentSourcePhrase:
    # Store details
    currentPhraseDetails.append(phraseInfo[2:])
  else:
    # First process the previous phrase
    if phrase != "":
      processPhrase(currentSourcePhrase, currentPhraseDetails)
    # Reset variables
    currentSourcePhrase = sourcePhrase
    currentPhraseDetails = [phraseInfo[2:]]

normalizeCountFeats()
writeFeats()

phraseTable.close()
outFeats.close()
