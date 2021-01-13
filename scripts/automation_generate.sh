#!/bin/bash

VIRTUAL_ENV=$TMPDIR/venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

# node version degrade
sudo npm install -g n
sudo n 10.15.0
export PATH=/usr/local/n/versions/node/10.15.0/bin:$PATH

# generate code and package
python -m packaging_tools.auto_codegen "$1" "$TMPDIR/venv-sdk/auto_temp.json" 2>&1
echo "[Generate] codegen done!!!"
python -m packaging_tools.auto_package "$TMPDIR/venv-sdk/auto_temp.json" "$2" 2>&1
echo "[Generate] generate done!!!"
