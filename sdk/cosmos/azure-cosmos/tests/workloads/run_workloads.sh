#!/bin/bash
if [ $# -eq 0 ]; then
    echo "Usage: $0 num_runs"
    exit 1
fi

num_runs=$1

for (( i=0; i<num_runs; i++ )); do
    python3 r_proxy_workload.py &
done

for (( i=0; i<num_runs; i++ )); do
    python3 r_w_q_proxy_workload.py &
done

for (( i=0; i<num_runs; i++ )); do
    python3 r_w_q_workload.py &
done

for (( i=0; i<num_runs; i++ )); do
    python3 r_workload.py &
done

for (( i=0; i<num_runs; i++ )); do
    python3 w_proxy_workload.py &
done

for (( i=0; i<num_runs; i++ )); do
    python3 w_workload.py &
done

for (( i=0; i<num_runs; i++ )); do
    python3 r_w_q_workload_sync.py &
done

wait