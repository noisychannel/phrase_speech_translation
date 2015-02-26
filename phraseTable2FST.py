#!/usr/bin/env python

import gzip
import collections
import argparse
import sys

parser = argparse.ArgumentParser("Converts a Moses Phrase table to an FST")
parser.add_argument("-p", "--phrase_table", dest="phraseTable", help="The location of the phrase table")
parser.add_argument("-f", "--fst", dest="FSTFile", help="The location to write out the output FST")
parser.add_argument("-s", "--syms", dest="symFile", help="The location to write out the output symbols")
opts = parser.parse_args()

if opts.phraseTable is None or opts.FSTFile is None or opts.symFile is None:
  parser.print_help()
  sys.exit(1)

phraseTable = gzip.open(opts.phraseTable)
FSTFile = open(opts.FSTFile, "w+")
symFile = open(opts.symFile, "w+")
# Write final state and the epsilon symbol
FSTFile.write("0\n")
symFile.write("<eps> 0\n")

sourcePhrases = set()
vocabulary = {"<eps>":0}
vocabID = 1
stateID = 1

def getVocabID(word):
  global vocabID, symFile
  if word not in vocabulary:
    vocabulary[word] = vocabID
    symFile.write(word + " " + str(vocabID) + "\n")
    vocabID = vocabID + 1
  return str(vocabulary[word])

for line in phraseTable:
  # Split phrase pair
  phraseInfo = line.split("|||")
  sourcePhrase = phraseInfo[0].strip()
  sourcePhrases.add(sourcePhrase)

for phrase in sourcePhrases:
  phraseComp = phrase.split()
  if len(phraseComp) == 1:
    # Single word phrase
    FSTFile.write("0 0 " + getVocabID(phraseComp[0]) + " " + getVocabID(phraseComp[0]) + "\n")
    pass
  else:
    path = []
    currentState = 0
    nextState = stateID
    for item in phraseComp:
      FSTFile.write(str(currentState) + " " + str(nextState) + " " + getVocabID(item) + " 0\n")
      currentState = nextState
      nextState = nextState + 1
    stateID = nextState
    FSTFile.write(str(currentState) + " 0 0 " + getVocabID("_".join(phraseComp)) + "\n")

symFile.close()
FSTFile.close()
phraseTable.close()
