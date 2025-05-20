#!/bin/bash

# init env
python -m pip install -U pip > /dev/null
python scripts/dev_setup.py -p azure-core > /dev/null
pip install tox==4.15.0 > /dev/null
pip install wheel==0.43.0 > /dev/null
pip install setuptools==78.1.0 > /dev/null
pip install setuptools-scm==8.3.0 > /dev/null

# install tsp-client globally (local install may interfere with tooling)
echo Install tsp-client
npm install -g @azure-tools/typespec-client-generator-cli > /dev/null

echo "{}" >> $2
echo "[Generate] init success!!!"
