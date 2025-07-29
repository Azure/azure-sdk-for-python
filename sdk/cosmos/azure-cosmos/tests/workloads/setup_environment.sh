#!/bin/bash

# Update package lists
sudo apt-get update

# Install pip for Python 3
sudo apt-get install -y python3-pip

# Install Python 3.12 virtual environment package
sudo apt-get install -y python3.12-venv

# Create a virtual environment
python3 -m venv azure-cosmosdb-sdk-environment

# Activate the virtual environment
source azure-cosmosdb-sdk-environment/bin/activate

# Install required Python packages
pip install -r dev_requirements.txt
pip install azure-monitor-opentelemetry
