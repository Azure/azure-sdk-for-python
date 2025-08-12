#!/bin/bash
# cspell:disable
# setup_env.sh - Automates Azure Cosmos SDK scale testing environment setup
# Usage: bash setup_env.sh

set -e

# 1. System update and install dependencies
echo "[Step 1] System update and install dependencies: started."
sudo apt-get update
sudo apt-get install -y python3-pip python3.12-venv wget gnupg
echo "[Step 1] System update and install dependencies: completed."

# 2. Create and activate Python virtual environment
echo "[Step 2] Create and activate Python virtual environment: started."
python3 -m venv azure-cosmosdb-sdk-environment
source azure-cosmosdb-sdk-environment/bin/activate
echo "[Step 2] Create and activate Python virtual environment: completed."

# 3. Install Python requirements
echo "[Step 3] Install Python requirements: started."
pip install --upgrade pip
cd ../../
pip install -r dev_requirements.txt
pip install azure-monitor-opentelemetry
echo "[Step 3] Install Python requirements: completed."

# 4. Install the current azure-cosmos package
echo "[Step 4] Install the current azure-cosmos package: started."
pip install .
cd tests/workloads
echo "[Step 4] Install the current azure-cosmos package: completed."

# 5. Install Envoy proxy
echo "[Step 5] Install Envoy proxy: started."
wget -O- https://apt.envoyproxy.io/signing.key | sudo gpg --dearmor -o /etc/apt/keyrings/envoy-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/envoy-keyring.gpg] https://apt.envoyproxy.io focal main" | sudo tee /etc/apt/sources.list.d/envoy.list
sudo apt-get update
sudo apt-get install -y envoy
envoy --version
echo "[Step 5] Install Envoy proxy: completed."

# 6. Manual steps
echo "[Step 6] Manual steps: started."
cat << EOF

Manual steps remaining:
----------------------
1. Fill out relevant configs in tests/workloads/workload_configs.py (key, host, etc).
2. Generate Envoy config:
   cd envoy
   ./generate_envoy_config.sh <template_file_path> <output_envoy_config_file> <account_name> <write_region> <read_region>
3. Start Envoy:
   mkdir -p logs
   envoy -c <envoy_config_file>.yaml --log-level debug --log-path logs/debug.txt
4. Run initial setup workload:
   cd ../tests/workloads
   python3 initial-setup.py
5. Run scale workloads:
   ./run_workloads.sh <number of clients per workload>

Refer to dev.md for more details.
EOF
echo "[Step 6] Manual steps: completed."
