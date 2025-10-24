#!/bin/bash

# init env
python -m pip install -U pip > /dev/null
python -m pip install eng/tools/azure-sdk-tools[build,ghtools,sdkgenerator] > /dev/null

# install tsp-client
echo Install tsp-client
cd eng/common/tsp-client
npm ci > /dev/null
cd ../../..

echo "{}" >> $2
echo "[Generate] init success!!!"
