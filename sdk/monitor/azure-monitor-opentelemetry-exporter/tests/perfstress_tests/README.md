# Monitor Exporter Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start by creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured Application Insights resource. The following environment variable will need to be set for the tests to access the live resources:
```
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection string for app insights>
```

### Setup for perf test runs

```cmd
(env) ~/azure-monitor-opentelemetry-exporter> pip install -r dev_requirements.txt
(env) ~/azure-monitor-opentelemetry-exporter> pip install -e .
```

## Test commands

```cmd
(env) ~/azure-monitor-opentelemetry-exporter> cd tests
(env) ~/azure-monitor-opentelemetry-exporter/tests> perfstress MonitorExporterPerfTest --sync --num-spans=10
```

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async). This must be set to True explicitly.
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

### MonitorExporter Test options
These options are available for all monitor exporter perf tests:
- `--num-spans` Number of spans to be exported. Defaults to 10.

### T2 Tests
The tests currently written for the T2 SDK:
- `MonitorExporterPerfTest` Collects sample traces and exports to application insights.

## Example command

**Note:** The `--sync` flag must be explicitly set for this package since there is no `async` support.

```cmd
(env) ~/azure-monitor-opentelemetry-exporter/tests> perfstress MonitorExporterPerfTest --sync --num-spans=10
```
