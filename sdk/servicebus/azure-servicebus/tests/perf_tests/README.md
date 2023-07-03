# Service Bus Python client performance tests

In order to run the performance tests, the `azure-devtools` package must be installed. This is done as part of the `dev_requirements.txt` installation. Start be creating a new virtual environment for your perf tests. This will need to be a Python 3 environment, preferably >=3.7.

### Setup for test resources

These tests will run against a pre-configured Service Bus. The following environment variables will need to be set for the tests to access the live resources:

```
AZURE_SERVICEBUS_CONNECTION_STRING=<the connection string of a Service Bus Namespace>
AZURE_SERVICEBUS_QUEUE_NAME=<the name of a Service Bus queue>
AZURE_SERVICEBUS_TOPIC_NAME=<the name of a Service Bus topic>
AZURE_SERVICEBUS_SUBSCRIPTION_NAME=<the name of a Service Bus subscription for the given topic>
```

### Setup for perf test runs

```cmd
(env) ~/azure-servicebus> pip install -r dev_requirements.txt
(env) ~/azure-servicebus> pip install .
```

## Test commands

When `azure-devtools` is installed, you will have access to the `perfstress` command line tool, which will scan the current module for runable perf tests. Only a specific test can be run at a time (i.e. there is no "run all" feature).

```cmd
(env) ~/azure-servicebus> cd tests
(env) ~/azure-servicebus/tests> perfstress
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

### Service Bus perf test command line options

The options that are available for all `Send` perf tests:

- `--message-size=100` - Size of a single message (in bytes). Defaults to 100.
- `--batch-size=100` - The number of messages that should be included in each batch. Defaults to 100.
- `--uamqp-transport` - Use the `uamqp` library as the underlying transport instead of the Python-based AMQP library. Defaults to False.
- `--transport-type` - Whether to use AMQP (0) or Websocket (1) transport protocol when communicating with the Service Bus service. Defaults to 0 (AMQP).

The options that are available for all `Receive` perf tests:

- `--message-size=100` - Size of a single message (in bytes). Defaults to 100.
- `--num-messages=100` - Maximum number of messages to receive. Defaults to 100.
- `--uamqp-transport` - Use the `uamqp` library as the underlying transport instead of the Python-based AMQP library. Defaults to False.
- `--transport-type` - Whether to use AMQP (0) or Websocket (1) transport protocol when communicating with the Service Bus service. Defaults to 0 (AMQP).
- `--peeklock` - Whether to run the test using peeklock mode instead of receive and  mode. If peeklock is used, messages will be completed. Default is False (receive and delete).
- `--max-wait-time=0` - The max time to wait for the specified number of messages to be received. Defaults to 0 (indefinitely).
- `--preload=10000` - The number of messages to preload into the queue before the receiving tests start. Defaults to 10000 messages.


## Example command
```cmd
(env) ~/azure-servicebus> perfstress ReceiveQueueMessageBatchTest --parallel=2 --message-size=10240 --num-messages=100 --peeklock
```
