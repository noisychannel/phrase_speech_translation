#!/bin/bash

# This script takes an Google OpenFST .fsm file on STDIN and produces a PLF file on STDOUT.

set -u

if [ $# -lt 2 ]
then
    echo "Usage: fsm2plf.sh <wordlist> <FSM file>"
    exit 1
fi

: ${wordlist=$1}

if [[ ! -e $wordlist ]]; then
  echo "* FATAL: Can't find wordlist '$wordlist'"
  exit 1
fi

fstprint --isymbols=$wordlist --osymbols=$wordlist $2 | $(dirname $0)/txt2plf.pl	
