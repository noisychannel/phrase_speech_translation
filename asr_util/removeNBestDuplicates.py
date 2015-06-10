#!/usr/bin/env python

import sys

nBestFile = open(sys.argv[1])
nBest_nodup = open(sys.argv[1] + ".nodup", "w+")

curL = None
nBest = []
nBestHash = set()
for line in nBestFile:
    line = line.split()
    timeInfo = "-".join(line[0].split("-")[:-1])
    if timeInfo != curL and curL is not None:
        for item in nBest:
            nBest_nodup.write(curL + " " + item + "\n")
        nBest = []
        nBestHash = set()
        curL = timeInfo
    if curL is None:
        curL = timeInfo
    trans = " ".join(line[1:]).strip()
    if trans not in nBestHash:
        nBest.append(trans)
        nBestHash.add(trans)

for item in nBest:
    nBest_nodup.write(curL + " " + item + "\n")

nBestFile.close()
nBest_nodup.close()
