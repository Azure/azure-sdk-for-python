#!/bin/bash

VIRTUAL_ENV=$TMPDIR/venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

TEMP_FILE="$TMPDIR/venv-sdk/auto_temp.json"
# generate code
python -m packaging_tools.sdk_generator "$1" "$TEMP_FILE" --debug 2>&1
echo "[Generate] codegen done!!!"
if [ ! -f "$TEMP_FILE" ]; then
  echo "[Autorest]$TEMP_FILE does not exist!!!Error happened during codegen"
  exit 1
fi

if [ -f "$2" ]; then
  rm "$2"
fi

# package
python -m packaging_tools.sdk_package "$TEMP_FILE" "$2" --debug 2>&1
echo "[Generate] generate done!!!"
if [ ! -f "$2" ]; then
  echo "[Autorest]$2 does not exist!!!Error happened during package"
  exit 1
fi
