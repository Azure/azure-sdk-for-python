#!/bin/bash

# generate code and package in one step
sdk_generator "$1" "$2" --debug 2>&1
echo "[Generate] generation and packaging done!!!"
if [ ! -f "$2" ]; then
  echo "[Autorest]$2 does not exist!!!Error happened during generation"
  exit 1
fi
