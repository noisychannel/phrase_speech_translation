#!/usr/bin/env python

import sys

if len(sys.argv) < 3:
    print "USAGE : n21best.py [WEIGHTS] [NBEST-1] [NBEST-2] .."

weightsFile = open(sys.argv[1])

weights = []
for line in weightsFile:
    line = line.strip().split()
    weights.append(float(line[1]))

hyps = {}

def process_hyps(nbest, weights):
    global hyps
    for line in nbest:
        line = line.split("|||")
        ln = int(line[0].strip())
        feats = line[2].strip().split()
        if ln not in hyps:
            hyps[ln] = []
        hyps[ln].append((line[1].strip(), sum([float(feats[i]) * weights[i] for i in range(len(weights))])))

for i in range(2, len(sys.argv)):
    nbest = open(sys.argv[i])
    process_hyps(nbest, weights)

for lineNo in sorted(hyps.keys()):
    print sorted(hyps[lineNo], key=lambda x:x[1], reverse=True)[0][0]
