## SDK Scale Testing
This directory contains the scale testing workloads for the SDK. The workloads are designed to test the performance 
and scalability of the SDK under various conditions. There are different types of workloads and each will create a log 
file when run. These logs are named in this format `<file name>-<process id>-<date time>.log`. 

### Setup Scale Testing
1. Create a VM in Azure with the following configuration:
   - 8 vCPUs
   - 32 GB RAM
   - Ubuntu
   - Accelerated networking
1. Give the VM necessary [permissions](https://learn.microsoft.com/azure/cosmos-db/nosql/how-to-grant-data-plane-access?tabs=built-in-definition%2Ccsharp&pivots=azure-interface-cli) to access the Cosmos DB account if using AAD (Optional). 
1. Create an Azure App Insights Resource (Optional)
1. Fork and clone this repository
1. Go to azure cosmos folder
   - `cd azure-sdk-for-python/sdk/cosmos/azure-cosmos`
1. Install the required packages and create virtual environment
   - `setup_env.sh` 
   - `source azure-cosmosdb-sdk-environment/bin/activate`
1. Checkout the branch with the changes to test. 
1. Install azure-cosmos
   - `pip install .`
1. Go to workloads folder
    - `cd tests/workloads`
1. Fill out relevant configs in `workload_configs.py`: key, host, etc
1. Go to envoy folder and generate envoy configuration file using template. Template files are in `envoy/templates` directory. `<account_name>` is your Cosmos DB account name.
    - `cd envoy`
    - `./generate_envoy_config.sh <template_file_path> <output_envoy_config_file> <account_name> <write_region> <read_region>`
1. Start envoy using the generated configuration file
    - `mkdir logs`
    - `envoy -c <envoy_config_file>.yaml --log-level debug --log-path logs/debug.txt`
1. Run the setup workload to create the database and containers and insert data
    - `python3 initial-setup.py`
1. Run the scale workloads
    - `./run_workloads.sh <number of clients per workload>`

### Monitor Run
- `ps -eaf | grep "python3"` to see the running processes
- `tail -f <log_file>` to see the logs in real time 

### Close Workloads
- If you want to keep the logs and stop the scripts,  
   `./shutdown_workloads.sh --do-not-remove-logs` 
- If you want to remove the logs and stop the scripts,        
   `./shutdown_workloads.sh`
