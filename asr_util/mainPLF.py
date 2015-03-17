#!/usr/bin/env python
# Copyright 2014  Gaurav Kumar.   Apache 2.0

# Extracts one best output for a set of files
# The list of files in the conversations for which 1 best output has to be extracted
# words.txt 

# Merges lattices based on time information specified in the Fisher Spanish corpus
# Then converts these lattices to PLF

import os
import sys
import subprocess
import argparse

checkPLF = "/export/a04/gkumar/code/mosesdecoder/contrib/checkplf/checkplf"

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
if not os.path.exists(opts.provDir):
  os.makedirs(opts.provDir)
else:
  os.system("rm " + opts.provDir + "/*")

conversationList = open(opts.conversationList)
provFile = open(opts.provDir + "/output.plf", "w+")
invalidPLF = open(opts.provDir + "/invalidPLF", "w+")
blankPLF = open(opts.provDir + "/blankPLF", "w+")
rmLines = open(opts.provDir + "/removeLines", "w+")
#invalidPLF = open('/export/a04/gkumar/corpora/fishcall/jack-splits/split-matt/bmmi-t/invalidPLF', 'w+')
#blankPLF = open('/export/a04/gkumar/corpora/fishcall/jack-splits/split-matt/bmmi-t/blankPLF', 'w+')
#rmLines = open('/export/a04/gkumar/corpora/fishcall/jack-splits/split-matt/bmmi-t/removeLines', 'w+')
#latticeLocation = 'latjosh-bmmi/lattices-pushed/'
#symtable = '/export/a04/gkumar/kaldi-trunk/egs/fishcall_es/j-matt/data/lang/words.clean.txt'
#conversationList = open('/export/a04/gkumar/corpora/fishcall/jack-splits/split-matt/test')
#provFile = open('/export/a04/gkumar/corpora/fishcall/jack-splits/split-matt/bmmi-t/asr.test.plf', 'w+')

tmpdir = latticeLocation + "/lattmp"
#tmpdir = 'data/local/data/tmp/bmmi-t/lattmp'

invalidplfdir = opts.provDir + '/invalidPLFs'

if not os.path.exists(tmpdir):
  os.makedirs(tmpdir)
if not os.path.exists(invalidplfdir):
  os.makedirs(invalidplfdir)
else:
  os.system("rm " + invalidplfdir + "/*")

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

      # Now convert to PLF
      proc = subprocess.Popen('asr_util/fsm2plf.sh ' + symtable +  ' ' + finalFST, stdout=subprocess.PIPE, shell=True)
      PLFline = proc.stdout.readline()
      finalPLFFile = tmpdir + "/final.plf"
      finalPLF = open(finalPLFFile, "w+")
      finalPLF.write(PLFline)
      finalPLF.close()

      # now check if this is a valid PLF, if not write it's ID in a 
      # file so it can be checked later
      proc = subprocess.Popen(checkPLF + " < " + finalPLFFile + " 2>&1 | awk 'FNR == 2 {print}'", stdout=subprocess.PIPE, shell=True)
      line = proc.stdout.readline()
      print line + " " + str(lineNo)
      if line.strip() != "PLF format appears to be correct.":
        os.system("cp " + finalFST + " " + invalidplfdir + "/" + timeInfo[0])
        invalidPLF.write(invalidplfdir + "/" + timeInfo[0] + "\n")
        rmLines.write(str(lineNo) + "\n")
      else:
        provFile.write(PLFline)
    else:
      blankPLF.write(timeInfo[0] + "\n")
      rmLines.write(str(lineNo) + "\n")
    # Now convert to PLF
    lineNo += 1

provFile.close()
invalidPLF.close()
blankPLF.close()
rmLines.close()
