#!/bin/bash

# init env
python -m pip install -U pip > /dev/null
python scripts/dev_setup.py -p azure-core > /dev/null
pip install tox==4.15.0 > /dev/null
pip install wheel==0.43.0 > /dev/null
pip install setuptools==78.1.0 > /dev/null
pip install setuptools-scm==8.3.0 > /dev/null
pip install build==1.3.0 > /dev/null

# install tsp-client
echo Install tsp-client
cd eng/common/tsp-client
npm ci > /dev/null
cd ../../..

echo "{}" >> $2
echo "[Generate] init success!!!"
