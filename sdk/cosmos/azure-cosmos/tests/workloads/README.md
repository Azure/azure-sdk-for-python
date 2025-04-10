## SDK Scale Testing
This directory contains the scale testing workloads for the SDK. The workloads are designed to test the performance 
and scalability of the SDK under various conditions. There are different types of workloads and each will create a log 
file when run. These logs are named in this format. 

## Setup VM
1. Create a VM in Azure with the following configuration:
   - 8 vCPUs
   - 32 GB RAM
   - Ubuntu
   - Accelerated networking
2. Fork and clone this repository
3. Go to azure cosmos folder
   - `cd azure-sdk-for-python/sdk/cosmos/azure-cosmos`
4. Install the required packages and create virtual environment
   - `sudo apt-get update`
   - `sudo apt-get install python3-pip`
   - `sudo apt-get install python3.12-venv`
   - `python3 -m venv azure-cosmosdb-sdk-environment`
   - `source azure-cosmosdb-sdk-environment/bin/activate`
   - `pip install -r dev_requirements.txt`
5. Checkout the branch with the changes to test. 
6. Install azure-cosmos
   - `pip install .`
7. Go to workloads folder
    - `cd tests/workloads`
8. Fill out relevant configs in `workload_configs.py`: key, host, etc
9. Install envoy proxy https://www.envoyproxy.io/docs/envoy/latest/start/install
10. Go to envoy folder and start envoy
    - `cd envoy`
    - `mkdir logs`
    - `envoy -c <envoy_file>.yaml --log-level debug --log-path logs/debug.txt`
11. Run the setup workload to create the database and containers and insert data
    - `python3 initial-setup.py`
12. Run the scale workloads
    - `python3 run_workloads.sh`

## Monitor Run
- `ps -eaf | grep "python3"` to see the running processes
- `tail -f <log_file>` to see the logs in real time 
- `pkill -f "python3"` This will stop all the running python processes
