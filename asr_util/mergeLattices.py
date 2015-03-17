#!/usr/bin/env python
# Copyright 2014  Gaurav Kumar.   Apache 2.0

# Merges lattices based on time information specified in the Fisher Spanish corpus

import os
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser("Merges Kaldi segment lattices based on time information provided with the Spanish Fisher corpus")
parser.add_argument("-l", "--lattice", dest="latticeLocation", help="The location of the Kaldi segment lattices")
parser.add_argument("-s", "--symtable", dest="symtable", help="The location of the symbol table for these lattices")
parser.add_argument("-c", "--convList", dest="conversationList", help="The location of the conversation list for this dataset partition")
parser.add_argument("-o", "--outputDir", dest="provDir", help="The location of the directory into which the PLFs will be written")
parser.add_argument("-t", "--timingDir", dest="timingDir", help="The location of the directory which contains timing information for this dataset")
opts = parser.parse_args()

if opts.latticeLocation is None or opts.symtable is None or opts.conversationList is None or opts.provDir is None:
  parser.print_help()
  sys.exit(1)

latticeLocation = opts.latticeLocation
symtable = opts.symtable

# Create the output directory
os.system("mkdir -p " + opts.provDir)
os.system("rm -rf " + opts.provDir + "/*")
finalLatLocation = opts.provDir + "/finalLat"
os.system("mkdir -p " + finalLatLocation)

conversationList = open(opts.conversationList)
blankLat = open(opts.provDir + "/blankLat", "w+")
rmLines = open(opts.provDir + "/removeLines", "w+")

tmpdir = opts.provDir + "/lattmp"
os.system("mkdir -p " + tmpdir)

def latticeConcatenate(lat1, lat2):
  '''
  Concatenates lattices, writes temporary results to tmpdir
  '''
  if lat1 == "":
    os.system('rm ' + tmpdir + '/tmp.lat')
    return lat2
  else:
    proc = subprocess.Popen(['fstconcat', lat1, lat2, (tmpdir + '/tmp.lat')])
    proc.wait()
    return tmpdir + '/tmp.lat'


def findLattice(timeDetail):
  '''
  Finds the lattice corresponding to a time segment
  ''' 
  if os.path.isfile(latticeLocation + "/" + timeDetail + '.lat'):
    return latticeLocation + "/" + timeDetail + '.lat'
  else:
    return -1


# Now read list of files in conversations
fileList = []
for line in conversationList:
  line = line.strip()
  line = line[:-4]
  fileList.append(line)

# IN what order were the conversations added to the spanish files?
# Now get timing information to concatenate the ASR outputs

lineNo = 1
for item in fileList:
  timingFile = open(opts.timingDir + '/' + item + '.es')
  for line in timingFile:
    timeInfo = line.split()

    # For utterances that are concatenated in the translation file, 
    # the corresponding FSTs have to be translated as well
    mergedTranslation = ""
    for timeDetail in timeInfo:
      tmp = findLattice(timeDetail)
      if tmp != -1:
        # Concatenate lattices
        mergedTranslation = latticeConcatenate(mergedTranslation, tmp)

      print mergedTranslation
    if mergedTranslation != "":

      # Sanjeev's Recipe : Remove epsilons and topo sort
      finalFST = tmpdir + "/final.fst"
      os.system("fstrmepsilon " + mergedTranslation + " | fsttopsort - " + finalFST)

      # Copy this lattice into our merged lattice dir
      os.system("mv " + finalFST + " " + finalLatLocation + "/" + str(lineNo) + ".lat")

    else:
      blankLat.write(timeInfo[0] + "\n")
      rmLines.write(str(lineNo) + "\n")
    lineNo += 1

blankLat.close()
rmLines.close()
