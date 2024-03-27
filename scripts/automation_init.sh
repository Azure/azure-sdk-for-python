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
python -m pip install PyGithub
python -m pip install GitPython

echo "{}" >> $2
echo "[Generate] init success!!!"
