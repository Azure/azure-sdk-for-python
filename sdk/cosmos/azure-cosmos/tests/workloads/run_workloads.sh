#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: $0 num_runs"
    exit 1
fi

num_runs=$1

echo "[Info] Installing azure-cosmos package..."
pip install ../../.
if [ $? -ne 0 ]; then
    echo "[Error] Failed to install azure-cosmos. Exiting."
    exit 2
fi
echo "[Info] azure-cosmos installed successfully."

# Loop over each Python file in the current directory ending with _workload.py
for file in ./*_workload.py; do
    for (( i=0; i<num_runs; i++ )); do
        python3 "$file" &
        # slow start up
        sleep 1
    done
done

echo "[Info] All workloads started successfully."
