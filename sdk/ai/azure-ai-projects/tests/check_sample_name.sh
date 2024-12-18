#!/bin/bash
# This is simple helper script to chreck the name of a file
# the name should appear at least once as:
#
# python $fname
#
# If the file contain its name less times, we print its name.

SAMPLES_SYNC="`dirname ${0}`/../samples/agents"
SAMPLES_ASYNC="`dirname ${0}`/../samples/agents/async_samples"

for sample_dir in "$SAMPLES_SYNC" "$SAMPLES_ASYNC"; do
  for fname in `ls "$sample_dir" | grep \^sample_ | grep \[.\]py\$`; do
    cnt=`grep -c "${fname}" "${sample_dir}/${fname}"`
    if [ $cnt -lt  1 ]; then
      echo "${sample_dir}/${fname} name encountered ${cnt} times."
    fi
  done
done
exit 0
