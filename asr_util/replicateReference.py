#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser("Replicates the reference for an nbest file based on counts")
parser.add_argument("-c", "--countFile", dest="countFile", help="A file that lists how many times the reference has to be replicated")
parser.add_argument("-r", "--refFile", dest="refFile", help="The reference file")
parser.add_argument("-o", "--outputFile", dest="outputFile", help="The output file")
opts = parser.parse_args()

countFile = open(opts.countFile)
refFile = open(opts.refFile)
outputFile = open(opts.outputFile, "w+")

for (count, ref) in zip(countFile, refFile):
  for _ in range(int(count)):
    outputFile.write(ref)

outputFile.close()
refFile.close()
countFile.close()
