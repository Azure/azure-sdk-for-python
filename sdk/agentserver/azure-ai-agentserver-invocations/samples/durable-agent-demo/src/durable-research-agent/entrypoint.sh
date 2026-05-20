#!/usr/bin/env bash
# Auto-restart wrapper — immediately restarts on crash, unlimited retries.
set -u

while true; do
    echo "$(date -Iseconds) [entrypoint] Starting agent..."
    python app.py
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "$(date -Iseconds) [entrypoint] Agent exited cleanly. Stopping."
        exit 0
    fi

    echo "$(date -Iseconds) [entrypoint] 💥 Crashed (exit $exit_code). Restarting..."
done
