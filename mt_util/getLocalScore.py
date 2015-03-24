#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser("Tunes phrase lattice features")
parser.add_argument("-o", "--one_best", dest="oneBest", help="The 1best file for tuning")
parser.add_argument("-n", "--nbest", dest="nBest", help="The nbest file for tuning")
parser.add_argument("-c", "--nbest_count", dest="nBestCounts", help="The count of nbest entries")
parser.add_argument("-s", "--nbest_scores", dest="nBestScoresFile", help="The BLEU+1 scores for the nbest file")
opts = parser.parse_args()

# First read the nbest file and store the scores
nBestScores = {}
nBestCounts = open(opts.nBestCounts)
nBest = open(opts.nBest)
nBestScoresFile = open(opts.nBestScoresFile)
for lineNo, count in enumerate(nBestCounts):
  nBestScores[lineNo] = {}
  for _ in range(int(count)):
    nBestScores[lineNo][nBest.readline()] = float(nBestScoresFile.readline())

oneBest = open(opts.oneBest)
scores = []

for lineNo, line in enumerate(oneBest):
  if line in nBestScores[lineNo]:
    scores.append(nBestScores[lineNo][line])

# Return average cost
print 1. - sum(scores) / float(len(scores))

nBest.close()
nBestCounts.close()
nBestScoresFile.close()
oneBest.close()
