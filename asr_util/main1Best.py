#!/usr/bin/env python
# Copyright 2014  Gaurav Kumar.   Apache 2.0

# Extracts one best output for a set of files
# The list of files in the conversations for which 1 best output has to be extracted
# words.txt 

import os
import sys
import argparse

parser = argparse.ArgumentParser("Merges Kaldi 1best output based on time information provided with the Spanish Fisher corpus")
parser.add_argument("-s", "--scoring", dest="scoringFile", help="The location of Kaldi scoring file that contains the 1best output")
parser.add_argument("-s", "--symtable", dest="symtable", help="The location of the symbol table for this output")
parser.add_argument("-c", "--convList", dest="conversationList", help="The location of the conversation list for this dataset partition")
parser.add_argument("-o", "--outputDir", dest="provDir", help="The location of the directory into which the PLFs will be written")
parser.add_argument("-t", "--timingDir", dest="timingDir", help="The location of the directory which contains timing information for this dataset")

scoringFile = opts.scoringFile
wordsFile = open(opts.symtable)
conversationList = open(opts.conversationList)
oneBestTmp = opts.provDir + '/tmp'
provFile = open(opts.provDir + '/asr.1best', 'w+')
timLocation = opts.timingDir

# Create the tmp directory if it does not exist
os.system("mkdir -p " + oneBestTmp)

def findTranscription(timeDetail):
	file1 = open(scoringFile)
	for line in file1:
		lineComp = line.split()
		if lineComp[0] == timeDetail:
			return " ".join(lineComp[1:])
	# No result found
	return -1

words = {}

# Extract word list
for line in wordsFile:
	lineComp = line.split()
	words[int(lineComp[1])] = lineComp[0].strip()

# Now read list of files in conversations
fileList = []
for line in conversationList: 
    line = line.strip()
    line = line[:-4]
    fileList.append(line)

# Now get timing information to concatenate the ASR outputs
if not os.path.exists(oneBestTmp):
	os.makedirs(oneBestTmp)

for item in fileList:
	timingFile = open(timLocation + '/' + item + '.es')
	newFile = open(oneBestTmp + '/' + item + '.es', 'w+')
	for line in timingFile:
		timeInfo = line.split()
		mergedTranslation = ""
		for timeDetail in timeInfo:
			#Locate this in ASR dev/test, this is going to be very slow
			tmp = findTranscription(timeDetail)
			if tmp != -1:
				mergedTranslation = mergedTranslation + " " + tmp
		mergedTranslation = mergedTranslation.strip()
		transWords = [words[int(x)] for x in mergedTranslation.split()]
		newFile.write(" ".join(transWords) + "\n")
		provFile.write(" ".join(transWords) + "\n")

	newFile.close()
provFile.close()
wordsFile.close()
conversationList.close()
