#!/bin/bash
# cspell:disable
# Kill all python3 processes
pkill -f "python3 ./r_"
pkill -f "python3 ./w_"

# Remove all files with .logs in their filename
rm -f *.log*
