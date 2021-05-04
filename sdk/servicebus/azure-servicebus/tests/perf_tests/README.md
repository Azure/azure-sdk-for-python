# ServiceBus Performance Tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements`.
Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.
Note that tests for T1 and T2 SDKs cannot be run from the same environment, and will need to be setup separately.

### Setup for T2 perf test runs

```cmd
(env) ~/azure-servicebus> pip install -r dev_requirements.txt
(env) ~/azure-servicebus> pip install .
```

### Setup for T1 perf test runs

```cmd
(env) ~/azure-servicebus> pip install -r dev_requirements.txt
(env) ~/azure-servicebus> pip install tests/perf_tests/T1_legacy_tests/t1_test_requirements.txt
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-servicebus> cd tests
(env) ~/azure-servicebus/tests> perfstress
```
Using the `perfstress` command alone will list the available perf tests found. Note that the available tests discovered will vary depending on whether your environment is configured for the T1 or T2 SDK.

### Common perf command line options
These options are available for all perf tests:
- `--duration=10` Number of seconds to run as many operations (the "run" function) as possible. Default is 10.
- `--iterations=1` Number of test iterations to run. Default is 1.
- `--parallel=1` Number of tests to run in parallel. Default is 1.
- `--no-client-share` Whether each parallel test instance should share a single client, or use their own. Default is False (sharing).
- `--warm-up=5` Number of seconds to spend warming up the connection before measuing begins. Default is 5.
- `--sync` Whether to run the tests in sync or async. Default is False (async).
- `--no-cleanup` Whether to keep newly created resources after test run. Default is False (resources will be deleted).

### Common Service Bus command line options
The options are available for all SB perf tests:
- `--message-size=100` Number of bytes each message contains. Default is 100.
- `--num-messages` Number of messages to send/receive as part of a single run.

#### Receive command line options
The receiving tests have these additional command line options:
- `--peeklock` Whether to run the test using peeklock or receive and delete. If peeklock is used, messages will be completed. Default is False (receive and delete).
- `--max-wait-time=0` The max time to wait for the specified number of messages to be received. Default is 0 (indefinitely).
- `--preload=10000` The number of messages to preload into the queue before the receiving tests start. Default is 10000 messages.

### T2 Tests
The tests currently written for the T2 SDK:
- `SendMessageTest` Sends a single message per run.
- `SendMessageBatchTest` Sends `num-messages` in a batch per run.
- `ReceiveMessageStreamTest` Receives `num-messages` using an iterator. Receive command options apply. 
- `ReceiveMessageBatchTest` Receives `num-messages` using a single fetch call. Receive command options apply.

### T1 Tests
The tests currently written for the T2 SDK:
- `LegacySendMessageTest` Sends a single message per run.
- `LegacySendMessageBatchTest` Sends `num-messages` in a batch per run.
- `LegacyReceiveMessageStreamTest` Receives `num-messages` using an iterator. Receive command options apply. 
- `LegacyReceiveMessageBatchTest` Receives `num-messages` using a single fetch call. Receive command options apply.

## Example command
```cmd
(env) ~/azure-servicebus/tests> perfstress ReceiveMessageBatchTest --parallel=2 --message-size=10240 --num-messages=100 --peeklock
```