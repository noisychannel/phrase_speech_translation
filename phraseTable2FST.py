#!/usr/bin/env python

"""
Converts a Moses phrase table to a FST in the OpenFST format
A text based FST is written out and may need to be compiled
into a binary using fstcompile
Also writes a symbol table with the vocbulary and the corresponding
symbol IDs

Author : Gaurav Kumar (Johns Hopkins University)
"""

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
# Record variables to increment when an item is added to the 
# vocabulary or if a new arc is added (record new state)
vocabID = 1
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

# Get the source side phrases from the phrase table
for line in phraseTable:
  # Split phrase pair
  # TODO: Scores are not recorded in the current form. Fix. Add a switch for this.
  phraseInfo = line.split("|||")
  sourcePhrase = phraseInfo[0].strip()
  sourcePhrases.add(sourcePhrase)

# Create paths for each of the source side phrases
for phrase in sourcePhrases:
  phraseComp = phrase.split()
  if len(phraseComp) == 1:
    # Single word phrase, the path starts and ends at 0
    # TODO: Length based features currently used, this may be replaced by the actual features later
    FSTFile.write("0 0 " + getVocabID(phraseComp[0]) + " " + getVocabID(phraseComp[0]) + "1 \n")
    pass
  else:
    # Create a path, starts at 0, ends at 0 with intermediate states
    currentState = 0
    nextState = stateID
    for item in phraseComp:
      # TODO: Length based features currently used, this may be replaced by the actual features later
      FSTFile.write(str(currentState) + " " + str(nextState) + " " + getVocabID(item) + " 0 1\n")
      currentState = nextState
      nextState = nextState + 1
    stateID = nextState
    FSTFile.write(str(currentState) + " 0 0 " + getVocabID("_".join(phraseComp)) + "\n")

symFile.close()
FSTFile.close()
phraseTable.close()
