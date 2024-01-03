# Core Python client performance tests

In order to run the performance tests, the `devtools_testutils` package must be installed. This is done as part of the `dev_requirements.txt` installation. Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources
The following environment variables will need to be set for the tests to access the live resources:

```
AZURE_STORAGE_CONTAINER_SAS_URL=<the URI of the Storage container>
```

### Setup for perf test runs

```cmd
(env) ~/azure-core> pip install -r dev_requirements.txt
(env) ~/azure-core> pip install .
```

## Test commands

When `devtools_testutils` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-core> cd tests
(env) ~/azure-core/tests> perfstress
```

Using the `perfstress` command alone will list the available perf tests found.

### Tests

The tests currently available:

- `ReceiveQueueMessageBatchTest` - Receive batches of messages from a queue.
- `ReceiveQueueMessageStreamTest` - Receive messages from a queue using an iterator.
- `ReceiveSubscriptionMessageBatchTest` - Receive batches of messages from a subscription.
- `ReceiveSubscriptionMessageStreamTest` - Receive messages from a subscription using an iterator.
- `SendQueueMessageTest` - Send individual messages (or a list of messages if `batch-size` is more than 1) to a queue.
- `SendQueueMessageBatchTest` - Send batches of messages (`ServiceBusMessageBatch`) to a queue.
- `SendTopicMessageTest` - Send individual messages (or a list of messages if `batch-size` is more than 1) to a topic.
- `SendTopicMessageBatchTest` - Send batches of messages (`ServiceBusMessageBatch`) to a topic.

### Common perf command line options

The `perfstress` framework has a series of common command line options built in. View them [here](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/perfstress_tests.md#default-command-options).

### Core perf test command line options

The options that are available for all `SendRequest` perf tests:

- `--transport-type` - By default, uses AiohttpTransport (0) for async. By default, uses RequestsTransport (0) for sync. All options:
  - For async:
    - 0: AiohttpTransport (default)
    - 1: AsyncioRequestsTransport
    - 2: AsyncHttpXTransport
  - For sync:
    - 0: RequestsTransport (default)
    - 1: HttpXTransport
- `--size=10240` - Size of request content (in bytes). Defaults to 10240.
- `--sync` Whether to run the tests in sync or async. Default is False (async).

The options that are available for all `Receive` perf tests:

- `--transport-type` - By default, uses AiohttpTransport (0) for async. By default, uses RequestsTransport (0) for sync. All options:
  - For async:
    - 0: AiohttpTransport (default)
    - 1: AsyncioRequestsTransport
    - 2: AsyncHttpXTransport
  - For sync:
    - 0: RequestsTransport (default)
    - 1: HttpXTransport
- `--size=10240` - Size of request content (in bytes). Defaults to 10240.
- `--sync` Whether to run the tests in sync or async. Default is False (async).

## Example command
```cmd
(env) ~/azure-core> perfstress StreamDownloadTest
```
