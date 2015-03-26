#!/usr/bin/env python

"""
An FST based featurized decoder for phrase based speech translation

Author : Gaurav Kumar (Johns Hopkins University)
"""

import argparse
import math
import codecs
import sys

parser = argparse.ArgumentParser("Extracts features from a Moses phrase table")
parser.add_argument("-p", "--phraselat-dir", dest="phraseLatDir", help="The location of the phrase lattices that contain the ASR weights")
parser.add_argument("-c", "--config", dest="config", help="The decoder config file, contains weights only")
parser.add_argument("-f", "-feats", dest="phraseFeatsFile", help="The file containing the phrase features")
parser.add_argument("-o", "--output-dir", dest="outputDir", help="The output directory")
parser.add_argument("-s", "--syms", dest="symsFile", help="The symbol table")
opts = parser.parse_args()

if opts.phraseLatDir is None or opts.config is None:
  parser.print_help()
  sys.exit(1)

# What do you need to do?
# 1. Read the feats file, create W_mt, take inspiration from phrase2FST
# 2. Keep, the phrase features in memory
# 3. Call a helper file that does the following : Composition with P \forall L, shortestpath (n?), 
# !!! How do you print n shortest paths : FST randgen outputs different files
# Project input for the n-best output
# Project output to look up the phrase features
