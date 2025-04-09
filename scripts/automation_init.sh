#!/bin/bash

# install python3.10
sudo add-apt-repository ppa:deadsnakes/ppa > /dev/null
sudo apt-get install python3.10 > /dev/null
sudo apt-get install python3.10-venv > /dev/null

# init env
rm -rf $TMPDIR/venv-sdk > /dev/null
python3.10 -m venv $TMPDIR/venv-sdk > /dev/null
VIRTUAL_ENV=$TMPDIR/venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
python -m pip install -U pip > /dev/null
python scripts/dev_setup.py -p azure-core > /dev/null
pip install tox==4.15.0 > /dev/null
pip install wheel > /dev/null

# install tsp-client globally (local install may interfere with tooling)
echo Install tsp-client
sudo npm install -g @azure-tools/typespec-client-generator-cli > /dev/null

echo "{}" >> $2
echo "[Generate] init success!!!"
