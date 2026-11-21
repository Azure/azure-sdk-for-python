#!/usr/bin/env bash
# Stop only explicitly supplied workload PIDs. Retain logs as measurement evidence.
set -euo pipefail
if [[ "$#" -eq 0 ]]; then
  echo "Usage: shutdown_workloads.sh PID [PID ...]" >&2
  exit 2
fi
for pid in "$@"; do
  if [[ ! "${pid}" =~ ^[1-9][0-9]*$ || "${pid}" -le 1 ]]; then
    echo "ERROR: invalid workload PID: ${pid}" >&2
    exit 2
  fi
done
for pid in "$@"; do
  kill -INT -- "${pid}"
done
echo "Stop requested for the supplied PIDs. Wait for clean exits; logs were retained."
