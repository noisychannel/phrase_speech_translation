#!/usr/bin/env python

import argparse
import sys
import os

parser = argparse.ArgumentParser("Extracts reweighted lattice 1best files from a directory")
parser.add_argument("-i", "--input", dest="inputDir", help="The location of the 1best files")
parser.add_argument("-a", "--asr-best", dest="asrBest", help="The location of the ASR one best file")
parser.add_argument("-o", "--out", dest="output", help="The location of the output file for the lat-1best")
opts = parser.parse_args()

if opts.inputDir is None or opts.output is None or opts.asrBest is None:
  parser.print_help()
  sys.exit(1)

inputDir = opts.inputDir
asrBest = open(opts.asrBest)
output = open(opts.output, "w+")

for lineNo, line in enumerate(asrBest):
  actualLineNo = lineNo + 1
  if os.path.exists(inputDir + "/" + str(actualLineNo) + ".lat.1best"):
    f = open(inputDir + "/" + str(actualLineNo) + ".lat.1best").readline()
    if f.strip() == "":
      # Lat hyp is empty, write the asr 1-best instead
      # There is very little hope of translating this since
      # no phrase match was found for this entry
      output.write(line)
    else:
      output.write(f)
  else:
    output.write(line)

asrBest.close()
output.close()
