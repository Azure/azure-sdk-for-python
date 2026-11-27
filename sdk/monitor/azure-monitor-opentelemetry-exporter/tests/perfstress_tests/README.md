# Monitor Exporter Performance Tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the `dev_requirements`.
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
- `--gen-ai-message-size` Length of the `gen_ai.input.messages` and `gen_ai.output.messages` attributes on each span (e.g. `4194304` for the 4 MiB limit, which requires setting `APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES=gen_ai_input_output_limit_increase`). Defaults to 0 (attributes not set).

### T2 Tests
The tests currently written for the T2 SDK:
- `MonitorExporterPerfTest` Collects sample traces and exports to application insights.

## Example command

**Note:** The `--sync` flag must be explicitly set for this package since there is no `async` support.

```cmd
(env) ~/azure-monitor-opentelemetry-exporter/tests> perfstress MonitorExporterPerfTest --sync --num-spans=10
```

## Offline feature benchmarks

[Multi-endpoint routing](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/monitor/azure-monitor-opentelemetry-exporter/tests/perf/test_multi_endpoint_routing.py) benchmarks use
512 prebuilt spans and a fake transport, without Azure resources or credentials.
After setup, run from the package directory:

```powershell
python -m pytest tests\perf --benchmark-only --benchmark-json routing.json
python -m pytest tests\perf -k peak_memory --benchmark-disable -s
```

The matrix covers disabled, disabled with routing attributes, and enabled modes
at 1, 3, and 25 endpoints, each warmed and cold. Use `-k` to select cases.
The memory command measures allocations separately, without a timing loop.

Performance tests are skipped unless a `--benchmark-*` option is supplied.
These benchmarks run locally; no performance CI job or regression threshold is added.
