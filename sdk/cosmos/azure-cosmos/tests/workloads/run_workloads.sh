#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: $0 num_runs"
    exit 1
fi

num_runs=$1
# Get the directory where the script is located
WORKLOAD_DIR="core_workloads"

# Loop over each Python file in the directory and run it num_runs times in background.
for file in "$WORKLOAD_DIR"/*.py; do
    for (( i=0; i<num_runs; i++ )); do
        python3 "$file" &
    done
done
