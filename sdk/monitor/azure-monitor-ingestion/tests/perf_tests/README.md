# Monitor Ingestion performance tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the `dev_requirements`.
Start by creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured Log Analytics workspace. The `test-resources.json` file can be used to provision the needed resources. The following environment variables will need to be set for the tests to access the live resources:
```
AZURE_MONITOR_DCR_ID=<The ID of the data collection rule>
AZURE_MONITOR_DCE=<The data collection endpoint to upload logs to>
AZURE_MONITOR_STREAM_NAME=<The data collection stream name>
```

### Setup for perf test runs

```cmd
(env) ~/azure-monitor-ingestion> pip install -r dev_requirements.txt
(env) ~/azure-monitor-ingestion> pip install -e .
```

## Test commands

```cmd
(env) ~/azure-monitor-ingestion> perfstress
```

### Common perf command line options

These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).
- `--profile` Whether to run the perftest with cProfile. If enabled (default is False), the output file of a single iteration will be written to the current working directory in the format `"cProfile-<TestClassName>-<TestID>-<sync|async>.pstats"`.

### Ingestion test options

These options are available for all ingestion perf tests:
- `-n`, `--num-logs` Number of logs to be uploaded. Defaults to 100.
- `-l`, `--log-content-length` Length of the "AdditionalContext" value for each log entry. Use this to increase the size of each log entry. Defaults to 20.
- `-r`, `--random-log-content` Whether to use a random alphanumeric string for each "AdditionalContext" entry as opposed to a string comprised of a single repeating character. Use this to decrease the compression ratio when the logs are gzipped. Defaults to False.

### Available tests

The tests currently written for the T2 SDK:
- `UploadLogsTest` Upload a collection of logs to Azure Monitor

## Example command

```cmd
(env) ~/azure-monitor-ingestion> perfstress UploadLogsTest --num-logs=1000
```
