#!/usr/bin/env bash

# Install and use nvm version from .nvmrc
source $NVM_DIR/nvm.sh
nvm install
nvm use
# Set default node to version we just installed so that new shells start with it
nvm alias default $(node --version)

# Install utilities
npm install -g autorest @typespec/compiler @azure-tools/typespec-client-generator-cli

# Install PowerShell. PowerShell is needed for the test proxy asset sync migration scripts,
# and is also useful for running scripts in eng/common/scripts and eng/common/TestResources.
# Update the list of packages
sudo apt-get update
# Install pre-requisite packages.
sudo apt-get install -y wget apt-transport-https software-properties-common
# Download the Microsoft repository GPG keys
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
# Register the Microsoft repository GPG keys
sudo dpkg -i packages-microsoft-prod.deb
# Delete the the Microsoft repository GPG keys file
rm packages-microsoft-prod.deb
# Update the list of packages after we added packages.microsoft.com
sudo apt-get update
# Install PowerShell
sudo apt-get install -y powershell

# Install Python tooling
# init env
python -m pip install -U pip > /dev/null
python scripts/dev_setup.py -p azure-core > /dev/null
pip install -r eng/ci_tools.txt > /dev/null

