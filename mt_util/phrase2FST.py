#!/usr/bin/env python

"""
Converts phrases (featurized) from a Moses phrase table to a FST in the OpenFST format
A text based FST is written out and may need to be compiled
into a binary using fstcompile
Also writes a symbol table with the vocbulary and the corresponding
symbol IDs

Filters the phrase table to only use phrases that the ASR system can produce

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
symFile = codecs.open(opts.symFile, "w+", encoding="utf8")
mtSymFile = codecs.open(opts.symFile + ".mt", "w+", encoding="utf8")
# Only write output symbols to one file to make processing faster
weightsFile = open(opts.weightsFile)

vocabulary = {}
# Read external symbol file first (if available)
if opts.eSymFile is not None:
  eSymFile = codecs.open(opts.eSymFile, encoding="utf8")
  for line in eSymFile:
    lineDetails = line.strip().split()
    # Expected format : symbol id
    vocabulary[lineDetails[0]] = int(lineDetails[1])
    symFile.write(line.strip() + "\n")
else:
  parser.print_help()
  sys.exit(1)

# Write final state to the FST
FSTFile.write("0\n")

# Record variables to increment when an item is added to the 
# vocabulary or if a new arc is added (record new state)
vocabID = len(vocabulary.keys())
stateID = 1

mtSyms = {'<eps>':0}
mtSymFile.write("<eps> 0\n")

def getVocabID(word, isPhrase):
  """
  Returns the vocabulary ID of the word argument
  If the word is not in the vocabulary, it is added
  """
  global vocabID, symFile
  if word not in vocabulary:
    if isPhrase:
      vocabulary[word] = vocabID
      symFile.write(word + " " + str(vocabID) + "\n")
      vocabID = vocabID + 1
    else:
      return False

  # The MT system uses this, record
  if word not in mtSyms:
    mtSyms[word] = vocabulary[word]
    mtSymFile.write(word + " " + str(vocabulary[word]) + "\n")

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
    vocabEntry = getVocabID(phraseComp[0], False)
    if vocabEntry:
      FSTFile.write("0 0 " + vocabEntry + " " + vocabEntry + " " + str(cost) + "\n")
  else:
    # Create a path, starts at 0, ends at 0 with intermediate states
    currentState = 0
    nextState = stateID
    writeQueue = []
    for item in phraseComp:
      vocabEntry = getVocabID(item, False)
      if vocabEntry:
        writeQueue.append(str(currentState) + " " + str(nextState) + " " + vocabEntry + " 0\n")
        currentState = nextState
        nextState = nextState + 1
      else:
        # This phrase can never be used by the ASR output
        writeQueue = []
        break
    if len(writeQueue) != 0:
      for line in writeQueue:
        FSTFile.write(line)
      stateID = nextState
      FSTFile.write(str(currentState) + " 0 0 " + getVocabID("_".join(phraseComp), True) + " " + str(cost) + "\n")

# Write an OOV symbol
FSTFile.write("0 0 999999 999999 0.0\n")
symFile.write("OOV 999999\n")

symFile.close()
mtSymFile.close()
eSymFile.close()
FSTFile.close()
phraseFeats.close()
