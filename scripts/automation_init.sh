#!/bin/bash

# install python3.8
sudo apt-get install python3.8
sudo apt-get install python3.8-venv

# init env
rm -rf $TMPDIR/venv-sdk
python3.8 -m venv $TMPDIR/venv-sdk
VIRTUAL_ENV=$TMPDIR/venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
python -m pip install -U pip
python scripts/dev_setup.py -p azure-core
echo "{}" >> $2
echo "[Generate] init success!!!"
