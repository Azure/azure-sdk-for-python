#!/bin/bash

# install python3.8
apt-get install python3.8
apt-get install python3.8-venv

# init env
TMPDIR="$(dirname $(dirname $(readlink -f "$0")))/venv"
export TMPDIR
echo "$TMPDIR"
rm -rf $TMPDIR/venv-sdk
VIRTUAL_ENV=$TMPDIR/venv-sdk
export VIRTUAL_ENV
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
echo "$PATH"
python3.8 -m venv $TMPDIR/venv-sdk
python -m pip install -U pip
python scripts/dev_setup.py -p azure-core

if [ x"$1" = x ]; then
        echo "[Generate] init success!!!"
        exit 0
fi

echo "{}" >> $1
echo "[Generate] init success!!!！"
