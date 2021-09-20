#!/bin/bash

if [ $# -lt 3 ]; then
  echo "Usage: $0 <termination string> <program> [arguments...]"
  exit 1
fi

TERMINATION_STRING="$1"
PROGRAM_WITH_ARGUMENTS="${@:2}"
echo $TERMINATION_STRING
echo $PROGRAM_WITH_ARGUMENTS

cat <($PROGRAM_WITH_ARGUMENTS & wait) | awk -v termination_string="$TERMINATION_STRING" '{if ($0 ~ termination_string) {exit 1} else {print $0}}'
