#!/usr/bin/env python
# Copyright 2014  Gaurav Kumar.   Apache 2.0

# Extracts n-best output for a set of files
# Merges the nbest files based on timing information that is available
# The list of files in the conversations for which n best output has to be extracted

import os
import sys
import argparse

parser = argparse.ArgumentParser("Merges Kaldi nbest output based on time information provided with the Spanish Fisher corpus")
parser.add_argument("-i", "--input", dest="nBestFile", help="The location of Kaldi scoring file that contains the 1best output")
parser.add_argument("-c", "--convList", dest="conversationList", help="The location of the conversation list for this dataset partition")
parser.add_argument("-o", "--outputDir", dest="provDir", help="The location of the directory into which the 1best will be written")
parser.add_argument("-t", "--timingDir", dest="timingDir", help="The location of the directory which contains timing information for this dataset")
opts = parser.parse_args()

nBestFile = open(opts.nBestFile)
conversationList = open(opts.conversationList)
nBestTmp = opts.provDir + '/tmp'
# Create the tmp directory if it does not exist
os.system("mkdir -p " + nBestTmp)

refCountFile = open(opts.provDir + "/asr.ncount", "w+")
provFile = open(opts.provDir + '/asr.nbest', 'w+')
timLocation = opts.timingDir

# Read the nbest file and store the results
# n-best files are big, this is going to take time
nBest = {}
for line in nBestFile:
  line = line.split()
  # 20051023_232057_325_fsp-A-000015-000211-65
  timeInfo = "-".join(line[0].split("-")[:-1])
  trans = " ".join(line[1:]).strip()
  if timeInfo not in nBest:
    nBest[timeInfo] = []
  nBest[timeInfo].append(trans)


def findTranscription(timeDetail):
  # 20051021_222225_307_fsp-B-021848-022135
  if timeDetail in nBest:
    return nBest[timeDetail]
  else:
    return -1


# Now read list of files in conversations
fileList = []
for line in conversationList: 
    line = line.strip()
    line = line[:-4]
    fileList.append(line)

for item in fileList:
  timingFile = open(timLocation + "/" + item + ".es")
  newFile = open(nBestTmp + "/" + item + ".es", "w+")
  for line in timingFile:
    timeInfo = line.split()
    mergedTranslation = []
    for timeDetail in timeInfo:
      tmp = findTranscription(timeDetail)
      if tmp != -1:
        if len(mergedTranslation) == 0:
          mergedTranslation = tmp
        else:
          mergedTranslation = [x + " " + y for x in mergedTranslation for y in tmp]
      # Prune to get only the top 500 hyps
      mergedTranslation = mergedTranslation[:500]
    # Add an empty entry if no hyps were found
    if len(mergedTranslation) == 0:
      mergedTranslation.append("")

    # Write the number of hyps to a file
    refCountFile.write(str(len(mergedTranslation)) + "\n")

    # Write hyps
    for item in mergedTranslation:
      newFile.write(item + "\n")
      provFile.write(item + "\n")

  newFile.close()

provFile.close()
refCountFile.close()
conversationList.close()