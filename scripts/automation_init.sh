#!/bin/bash

# install python3.10
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.10
sudo apt-get install python3.10-venv

# init env
rm -rf $TMPDIR/venv-sdk
python3.10 -m venv $TMPDIR/venv-sdk
VIRTUAL_ENV=$TMPDIR/venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
python -m pip install -U pip
python scripts/dev_setup.py -p azure-core
pip install tox==4.15.0

# install tsp-client globally (local install may interfere with tooling)
echo Install tsp-client
sudo npm install -g @azure-tools/typespec-client-generator-cli

echo "{}" >> $2
echo "[Generate] init success!!!"
