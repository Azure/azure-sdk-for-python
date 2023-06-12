#  Event Hubs Python client performance tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements.txt`. installation. Start by creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured EventHub. The following environment variables will need to be set for the tests to access the live resources:

```
AZURE_EVENTHUB_CONNECTION_STRING=<the connection string of an Event Hub.>
AZURE_EVENTHUB_NAME=<the path of the specific Event Hub to connect to>
```

If using Azure Blob Storage for checkpointing, the following environment variable will need to be set:

```
AZURE_STORAGE_CONNECTION_STRING=<the connection string of an Azure Storage account>
```

### Setup for perf test runs

```cmd
(env) ~/azure-eventhub> pip install -r dev_requirements.txt
(env) ~/azure-eventhub> pip install .
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-eventhub> perfstress
```

Using the `perfstress` command alone will list the available perf tests found.

### Tests

The tests currently available:

- `ProcessEventsTest` - Receive and process events using the `receive` method from `EventHubConsumerClient`
- `ProcessEventsBatchTest` - Receive and process events using the `receive_batch` method from `EventHubConsumerClient`
- `SendEventsTest` - Send events using the `send_event` method from `EventHubProducerClient` if `batch-size` is 1, otherwise  send a list of events using the `send_batch` method.
- `SendEventBatchTest` - Send batches of events (`EventDataBatch`) using the `send_batch` method from `EventHubProducerClient`.
- `UamqpReceiveEventTest` - Receive and process events using `ReceiveClient` from `uamqp`.

A complete list of options for each test can be found by using `--help` on the test name. For example:

```cmd
(env) ~/azure-eventhub> perfstress ProcessEventsTest --help
```

### Common perf command line options

The `perfstress` framework has a series of common command line options built in. View them [here](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/perfstress_tests.md#default-command-options).

### Event Hubs perf test command line options

The options that are available for `SendEventsTest`/`SendEventBatchTest`:

- `--event-size=100` - Size of event body (in bytes). Defaults to 100.
- `--batch-size=100` - The number of events that should be included in each batch. Defaults to 100.
- `--uamqp-transport` - Use the `uamqp` library as the underlying transport instead of the Python-based AMQP library. Defaults to False.
- `--transport-type` - Whether to use AMQP (0) or Websocket (1) transport protocol when communicating with the Event Hubs service. Defaults to 0 (AMQP).
- `--event-extra` - Add properties to the events to increase payload and serialization. Defaults to False.

The options that are available for `ProcessEventsTest`/`ProcessEventsBatchTest`:

- `--event-size=100` - Size of event body (in bytes). Defaults to 100.
- `--prefetch-count=300` - Number of events to receive locally per request. Defaults to 300.
- `--load-balancing-strategy` - Event processor load balancing strategy (`greedy` or `balanced`). Defaults to `greedy`.
- `--checkpoint-interval` - Interval between checkpoints (in number of events). Defaults to None (no checkpoints).
- `--max-wait-time=0` - Maximum time to wait (in seconds) for an event to be received. Defaults to 0 (indefinitely).
- `--processing-delay` - Delay (in ms) when processing each event. Defaults to None (no delay).
- `--processing-delay-strategy` - Whether to 'sleep' or 'spin' during processing delay. Defaults to 'sleep'.
- `--preload` - Ensure the specified number of events are available across all partitions. Defaults to 0.
- `--use-storage-checkpoint` - Use Blob storage for checkpointing. Defaults to False (in-memory checkpointing).
- `--uamqp-transport` - Use the `uamqp` library as the underlying transport instead of the Python-based AMQP library. Defaults to False.
- `--transport-type` - Whether to use AMQP (0) or Websocket (1) transport protocol when communicating with the Event Hubs service. Defaults to 0 (AMQP).
- `--event-extra` - Add properties to the preloaded events (if applicable) to increase payload and serialization. Defaults to False.

The following option is also available for `ProcessEventsBatchTest`

- `--max-batch-size=100` - Maximum number of events to process in a single batch. Defaults to 100.

## Example command

```cmd
(env) ~/azure-eventhub> perfstress SendEventBatchTest --parallel=2 --duration=30 --event-size 2048 --batch-size 200 --transport-type 1 --uamqp-transport
```
