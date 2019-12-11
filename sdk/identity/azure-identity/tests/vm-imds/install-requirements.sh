#!/bin/bash

set -e

set -x

sudo apt update
sudo apt install python-pip python3-pip -y --no-install-recommends

git clone https://github.com/chlowell/azure-sdk-for-python.git --depth 1 --single-branch --branch cloudshell

cd azure-sdk-for-python/sdk/identity/azure-identity
pip install -r dev_requirements.txt .
pip3 install -r dev_requirements.txt .
