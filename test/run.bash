#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.

echo "Running tests..."
python -m unittest discover -p "test_*.py"
