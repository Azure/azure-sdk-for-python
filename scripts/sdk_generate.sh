#!/bin/bash

TMPDIR="$(dirname $(dirname $(readlink -f "$0")))/venv"
export TMPDIR
VIRTUAL_ENV=$TMPDIR/venv-sdk
echo "$VIRTUAL_ENV"
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

# node version degrade
npm install -g n
n 18.19.0
echo "$PATH"
export PATH="/usr/local/n/versions/node/18.19.0/bin:$PATH"

TEMP_FILE="$TMPDIR/venv-sdk/auto_temp.json"
# generate code and package in one step
python -m packaging_tools.sdk_generator "$1" "$2" 2>&1
echo "[Generate] generation and packaging done!!!"
if [ ! -f "$2" ]; then
  echo "[Autorest]$2 does not exist!!!Error happened during generation"
  exit 1
fi
