#!/bin/bash

export PYTHONPATH=$PYTHONPATH:../src

echo "Running tests..."
python -m unittest discover -p "test_*.py"
