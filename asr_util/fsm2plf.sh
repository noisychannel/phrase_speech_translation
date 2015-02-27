#!/bin/bash

# This script takes an Google OpenFST .fsm file on STDIN and produces a PLF file on STDOUT.

set -u

if [ $# -lt 2 ]
then
    echo "Location of wordlist required"
    exit 1
fi

: ${wordlist=$1}

if [[ ! -e $wordlist ]]; then
  echo "* FATAL: Can't find wordlist '$wordlist'"
  exit 1
fi

fstprint --isymbols=$wordlist --osymbols=$wordlist $2 | asr_util/txt2plf.pl	
