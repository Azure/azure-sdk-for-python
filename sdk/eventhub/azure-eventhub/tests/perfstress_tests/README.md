# EventHub Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start by creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured EventHub. The following environment variable will need to be set for the tests to access the live resources:
```
AZURE_EVENTHUB_CONNECTION_STRING=<the connection string of an Event Hub.>
AZURE_EVENTHUB_NAME=<the path of the specific Event Hub to connect to>
```

### Setup for perf test runs

```cmd
(env) ~/azure-eventhub> pip install -r dev_requirements.txt
(env) ~/azure-eventhub> pip install .
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-eventhub> cd tests
(env) ~/azure-eventhub/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found.

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--warm-up=5` Number of seconds to spend warming up the connection before measuring begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).

### Common Event Hub command line options
The options are available for all SB perf tests:
- `--event-size=100` Number of bytes each event contains. Default is 100.
- `--num-events` Number of events to send/receive as part of a single run.

#### Receive command line options
The receiving tests have these additional command line options:
- `--max-wait-time=0` The max time to wait for the specified number of events to be received. Default is 0 (indefinitely).
- `--preload=10000` The number of events to preload into the event hub before the receiving tests start. Default is 10000 events.

### T2 Tests
The tests currently written for the T2 SDK:
- `SendEventBatchTest` Sends `num-events` in a batch per run.
- `ReceiveEventTest` Receives `num-events` using the `receive` method. Receive command options apply. 
- `ReceiveEventBatchTest` Receives `num-events` using the `receive_batch` method. Receive command options apply.

## Example command
```cmd
(env) ~/azure-eventhub/tests> perfstress ReceiveEventBatchTest --parallel=2 --event-size=1024 --num-events=100 --duration=100
```
