#!/usr/bin/env python

import sys
import argparse

parser = argparse.ArgumentParser("Extracts 1-best hyps from a weighted n-best file")
parser.add_argument("-n", "--nbest", dest="nbestFile", help="The n-best file to extract 1-best hyps from")
parser.add_argument("-w", "--weights", dest="weightsFile", help="The weights for the features in the n-best file")
opts = parser.parse_args()

if opts.nbestFile is None or opts.weightsFile is None:
    parser.print_help()
    sys.exit(1)

nbestFile = open(opts.nbestFile)
weightsFile = open(opts.weightsFile)

weights = []
for line in weightsFile:
    line = line.strip().split()
    weights.append(float(line[1]))

curL = -1
hyps = []
for line in nbestFile:
    line = line.split("|||")
    ln = int(line[0].strip())
    if ln != curL and ln != 0:
        print sorted(hyps, key=lambda x: x[1])[0][0]
        hyps = []
        curL = ln
    feats = line[2].strip().split()
    hyps.append((line[1].strip(), sum([float(feats[i]) * weights[i] for i in range(len(weights))])))

print sorted(hyps, key=lambda x:x[1])[0][0]
