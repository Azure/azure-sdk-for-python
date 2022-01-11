# Monitor Query Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start by creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured Log Analytics workspace. The following environment variable will need to be set for the tests to access the live resources:
```
LOG_WORKSPACE_ID=<workspace id of the log workspace>
METRICS_RESOURCE_URI=<uri of the resource for which the metrics are being queried>
```

### Setup for perf test runs

```cmd
(env) ~/azure-monitor-query> pip install -r dev_requirements.txt
(env) ~/azure-monitor-query> pip install -e .
```

## Test commands

```cmd
(env) ~/azure-monitor-query> cd tests
(env) ~/azure-monitor-query/tests> perfstress
```

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

### T2 Tests
The tests currently written for the T2 SDK:
- `LogsPerfTest` queries a single query.
- `LogsBatchPerfTest` queries multiple queries using the batch operation.
- `MetricsPerfTest` to test a metrics query on eventgrid resource

## Example command
```cmd
(env) ~/azure-monitor-query/tests> perfstress LogsPerfTest
(env) ~/azure-monitor-query/tests> perfstress LogsBatchPerfTest
(env) ~/azure-monitor-query/tests> perfstress MetricsPerfTest
```
