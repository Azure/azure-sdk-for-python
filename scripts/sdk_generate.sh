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
n 14.15.0
echo "$PATH"
export PATH="/usr/local/n/versions/node/14.15.0/bin:$PATH"

TEMP_FILE="$TMPDIR/venv-sdk/auto_temp.json"
# generate code
python -m packaging_tools.sdk_generator "$1" "$TEMP_FILE" 2>&1
echo "[Generate] codegen done!!!"
if [ ! -f "$TEMP_FILE" ]; then
  echo "[Autorest]$TEMP_FILE does not exist!!!Error happened during codegen"
  exit 1
fi

# package
python -m packaging_tools.sdk_package "$TEMP_FILE" "$2" 2>&1
echo "[Generate] generate done!!!"
if [ ! -f "$2" ]; then
  echo "[Autorest]$2 does not exist!!!Error happened during package"
  exit 1
fi
