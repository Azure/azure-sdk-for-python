#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: $0 num_runs"
    exit 1
fi

num_runs=$1

# Loop over each Python file in the current directory ending with _workload.py
for file in ./*_workload.py; do
    for (( i=0; i<num_runs; i++ )); do
        python3 "$file" &
    done
done
