#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser("Tunes phrase lattice features")
parser.add_argument("-l", "--word-lat", dest="wordLattice", help="The location of the word lattice")
parser.add_argument("-o", "--out-feats", dest="outFeats", help="The location of the output file for the features")
opts = parser.parse_args()
