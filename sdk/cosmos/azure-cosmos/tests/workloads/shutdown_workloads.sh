#!/bin/bash
# Kill all python3 processes
pkill -f "python3"

# Remove all files with .logs in their filename
rm -f *.log*