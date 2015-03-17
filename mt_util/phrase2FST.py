#!/usr/bin/env python

"""
Converts phrases (featurized) from a Moses phrase table to a FST in the OpenFST format
A text based FST is written out and may need to be compiled
into a binary using fstcompile
Also writes a symbol table with the vocbulary and the corresponding
symbol IDs

Author : Gaurav Kumar (Johns Hopkins University)
"""

import codecs
import collections
import argparse
import sys

parser = argparse.ArgumentParser("Converts a featurized phrase list to an FST")
parser.add_argument("-p", "--phrase_feats", dest="phraseFeats", help="The location of the phrase features")
parser.add_argument("-f", "--fst", dest="FSTFile", help="The location to write out the output FST")
parser.add_argument("-s", "--syms", dest="symFile", help="The location to write out the output symbols")
parser.add_argument("-e", "--esyms", dest="eSymFile", help="An existing symbol table to start from ")
parser.add_argument("-w", "--weights", dest="weightsFile", help="A weights file to combine the features")
opts = parser.parse_args()

if opts.phraseFeats is None or opts.FSTFile is None or opts.symFile is None:
  parser.print_help()
  sys.exit(1)

phraseFeats = codecs.open(opts.phraseFeats, encoding="utf8")
FSTFile = open(opts.FSTFile, "w+")
symFile = open(opts.symFile, "w+")
weightsFile = open(opts.weightsFile)

# Read external symbol file first (if available)
if opts.eSymFile is not None:
  eSymFile = open(opts.eSymFile)
  for line in eSymFile:
    lineDetails = line.strip().split()
    # Expected format : symbol id
    vocabulary[lineDetails[0]] = int(lineDetails[1])
    symFile.write(line + "\n")
else:
  vocabulary = {"<eps>":0}
  symFile.write("<eps> 0\n")

# Write final state to the FST
FSTFile.write("0\n")

# Record variables to increment when an item is added to the 
# vocabulary or if a new arc is added (record new state)
vocabID = len(vocabulary.keys())
stateID = 1

def getVocabID(word):
  """
  Returns the vocabulary ID of the word argument
  If the word is not in the vocabulary, it is added
  """
  global vocabID, symFile
  if word not in vocabulary:
    vocabulary[word] = vocabID
    symFile.write(word + " " + str(vocabID) + "\n")
    vocabID = vocabID + 1
  return str(vocabulary[word])

weights = []
# Read weights : one per line
for line in weightsFile:
  weights.append(float(line.strip()))

sourcePhrases = {}
# Get the source side phrases from the phrase table
for line in phraseFeats:
  # Split phrase pair
  phraseInfo = line.split("\t")
  sourcePhrase = phraseInfo[0].strip()
  feats = phraseInfo[1:]
  cost = sum([float(feats[i]) * weights[i] for i in range(len(weights))])
  sourcePhrases[sourcePhrase] = cost

# Create paths for each of the source side phrases
for phrase, cost in sourcePhrases.iteritems():
  phraseComp = phrase.split()
  if len(phraseComp) == 1:
    # Single word phrase, the path starts and ends at 0
    FSTFile.write("0 0 " + getVocabID(phraseComp[0]) + " " + getVocabID(phraseComp[0]) + " " + cost + "\n")
  else:
    # Create a path, starts at 0, ends at 0 with intermediate states
    currentState = 0
    nextState = stateID
    for item in phraseComp:
      FSTFile.write(str(currentState) + " " + str(nextState) + " " + getVocabID(item) + " 0\n")
      currentState = nextState
      nextState = nextState + 1
    stateID = nextState
    FSTFile.write(str(currentState) + " 0 0 " + getVocabID("_".join(phraseComp)) + " " + cost + "\n")

symFile.close()
eSymFile.close()
FSTFile.close()
phraseTable.close()
