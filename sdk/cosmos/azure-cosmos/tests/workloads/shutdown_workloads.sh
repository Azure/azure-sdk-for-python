#!/bin/bash
# cspell:disable

NO_REMOVE_LOGS=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-remove-logs)
            NO_REMOVE_LOGS=true
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
    shift
done

# Kill all python3 processes
pkill -f "python3 ./r_"
pkill -f "python3 ./w_"

if [ "$NO_REMOVE_LOGS" = false ]; then
    # Remove all files with .log in their filename
    rm -f *.log*
    # Remove envoy log files
    rm envoy/logs/*
fi
