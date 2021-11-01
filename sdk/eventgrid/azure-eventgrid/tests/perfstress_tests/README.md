# EventGrid Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start by creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured Eventgrid topic. The following environment variable will need to be set for the tests to access the live resources:
```
EG_ACCESS_KEY=<access key of your eventgrid account>
EG_TOPIC_HOSTNAME=<hostname of the eventgrid topic>
```

### Setup for perf test runs

```cmd
(env) ~/azure-eventgrid> pip install -r dev_requirements.txt
(env) ~/azure-eventgrid> pip install -e .
```

## Test commands

```cmd
(env) ~/azure-eventgrid> cd tests
(env) ~/azure-eventgrid/tests> perfstress
```

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

### EventGrid Test options
These options are available for all eventgrid perf tests:
- `--num-events` Number of events to be published using the send method.

### T2 Tests
The tests currently written for the T2 SDK:
- `EventGridPerfTest` Publishes a list of eventgrid events.

## Example command
```cmd
(env) ~/azure-eventgrid/tests> perfstress EventGridPerfTest --num-events=100
```
