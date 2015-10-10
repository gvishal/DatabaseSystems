#!/bin/bash
# set -f
# echo $1
set -e
make external-merge-sort &>> make_output
./external-merge-sort "$@"