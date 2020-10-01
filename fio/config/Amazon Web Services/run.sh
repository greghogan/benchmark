#!/usr/bin/env sh

SIZE=100g

for TEST in read write randread randwrite ; do
  sudo fio ${TEST}.fio --output=../results/${TEST}.out --output-format=normal,json --size=${SIZE}
done
