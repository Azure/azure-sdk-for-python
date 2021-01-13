#!/bin/bash

rm -rf ../venv-sdk
python3 -m venv ../venv-sdk
VIRTUAL_ENV=$(pwd)/../venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
python scripts/dev_setup.py -p azure-core
echo "{}" >> $2
echo "[Generate] init success!!!"
