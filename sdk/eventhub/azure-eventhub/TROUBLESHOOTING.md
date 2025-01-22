# Troubleshoot Event Hubs issues

This troubleshooting guide covers failure investigation techniques, common errors for the credential types in the Azure Event Hubs Python client library, and mitigation steps to resolve these errors.

- [Handle Event Hubs exceptions](#handle-event-hubs-exceptions)
  - [Find relevant information in exception messages](#find-relevant-information-in-exception-messages)
  - [Commonly encountered exceptions](#commonly-encountered-exceptions)
- [Permission issues](#permission-issues)
- [Connectivity issues](#connectivity-issues)
  - [Timeout when connecting to service](#timeout-when-connecting-to-service)
    - [SSL handshake failures](#ssl-handshake-failures)
    - [Managing clients](#managing-clients)
    - [Cannot add components to the connection string](#cannot-add-components-to-the-connection-string)
    - [Connect using an IoT connection string](#connect-using-an-iot-connection-string)
      - ["TransportType=AmqpOverWebsocket" Alternative](#adding-transporttypeamqpoverwebsocket)
      - ["Authentication=Managed Identity" Alternative](#adding-authenticationmanaged-identity)
- [Enable and configure logging](#enable-and-configure-logging)
  - [Enable AMQP transport logging](#enable-amqp-transport-logging)
  - [Logging required for filing Github issues](#logging-required-for-filing-github-issues)
- [Troubleshoot EventHubProducerClient (Sync/Async) issues](#troubleshoot-eventhubproducerclient-syncasync-issues)
  - [Cannot set multiple partition keys for events in EventDataBatch](#cannot-set-multiple-partition-keys-for-events-in-eventdatabatch)
  - [Setting partition key on EventData is not set in Kafka consumer](#setting-partition-key-on-eventdata-is-not-set-in-kafka-consumer)
  - [Buffered producer not sending events](#buffered-producer-not-sending-events)
- [Troubleshoot EventHubConsumerClient issues](#troubleshoot-eventhubconsumerclient-issues)
  - [Logs reflect intermittent HTTP 412 and HTTP 409 responses from Azure Storage](#logs-reflect-intermittent-http-412-and-http-409-responses-from-storage)
  - [Partitions close and initialize intermittently or during scaling](#partitions-close-and-initialize-intermittently-or-during-scaling)
  - [Partitions close and initialize frequently](#partitions-close-and-initialize-frequently)
  - ["...current receiver '<RECEIVER_NAME>' with epoch '0' is getting disconnected"](#current-receiver-receiver_name-with-epoch-0-is-getting-disconnected)
  - [Blocking Calls in Async](#blocking-calls-in-async)
  - [High CPU usage](#high-cpu-usage)
  - [A partition is not being processed](#a-partition-is-not-being-processed)
  - [Duplicate events are being processed](#duplicate-events-are-being-processed)
  - [Soft Delete or Blob versioning is enabled for a Blob Storage checkpoint store](#soft-delete-or-blob-versioning-is-enabled-for-a-blob-storage-checkpoint-store)
  - [Migrate from legacy to new client library](#migrate-from-legacy-to-new-client-library)
- [Get additional help](#get-additional-help)
  - [Filing GitHub issues](#filing-github-issues)

## Handle Event Hubs exceptions

All Event Hubs exceptions are wrapped in an [EventHubError][EventHubError].  They often have an underlying AMQP error code which specifies whether an error should be retried.  For retryable errors (ie. `amqp:connection:forced` or `amqp:link:detach-forced`), the client libraries will attempt to recover from these errors based on the retry options specified using the following keyword arguments when instantiating the client:
* `retry_total`: The total number of attempts to redo a failed operation when an error occurs
* `retry_backoff_factor`: A backoff factor to apply between attempts after the second try
* `retry_backoff_max`: The maximum back off time
* `retry_mode`: The delay behavior between retry attempts. Supported values are 'fixed' or 'exponential'

To configure retry options, follow the sample [client_creation][ClientCreation].  If the error is non-retryable, there is some configuration issue that needs to be resolved.

The recommended way to solve the specific exception the AMQP exception represents is to follow the
[Event Hubs Messaging Exceptions][EventHubsMessagingExceptions] guidance.

### Find relevant information in exception messages

An [EventHubError][EventHubError] contains three fields which describe the error:

* **message**: The underlying AMQP error message. A description of the errors can be found in the [Exceptions module][ExceptionModule] or the [OASIS AMQP 1.0 spec][AmqpSpec].
* **error**: The error condition if available.
* **details**: The error details, if included in the service response.

By default the producer and consumer clients will retry for error conditions.
  
### Commonly encountered exceptions

#### ConnectionLostError Exception

When the connection to Event Hubs is idle, the service will disconnect the client after some time and raise a `ConnectionLostError` exception. The underlying issues that cause this are `amqp:connection:forced` and `amqp:link:detach-forced`.  This is not a problem as the clients will re-establish a connection when a service operation is requested.  More information can be found in the [AMQP troubleshooting documentation][AmqpTroubleshooting].

## Permission issues

An `AuthenticationError` means that the provided credentials do not allow for them to perform the action (receiving or sending) with Event Hubs.

* [Double check you have the correct connection string][GetConnectionString]
* [Ensure your SAS token is generated correctly][AuthorizeSAS]
* [Verify the correct RBAC roles were granted][RBACRoles]

[Troubleshoot authentication and authorization issues with Event Hubs][TroubleshootAuthenticationAuthorization] lists other possible solutions.

## Connectivity issues

### Timeout when connecting to service

* Verify that the connection string or fully qualified domain name specified when creating the client is correct.  [Get an Event Hubs connection string][GetConnectionString] demonstrates how to acquire a connection string.
* Check the firewall and port permissions in your hosting environment and that the AMQP ports 5671 and 5762 are open.
  * Make sure that the endpoint is allowed through the firewall.
* Try using WebSockets, which connects on port 443.  See [configure web sockets][PublishEventsWithWebSocketsAndProxy] sample.
* See if your network is blocking specific IP addresses.
  * [What IP addresses do I need to allow?][EventHubsIPAddresses]
* If applicable, check the proxy configuration.  See [configure proxy][PublishEventsWithWebSocketsAndProxy] sample.
* For more information about troubleshooting network connectivity, refer to [Event Hubs troubleshooting][EventHubsTroubleshooting]

### SSL handshake failures

This error can occur when an intercepting proxy is used.  We recommend testing in your hosting environment with the proxy disabled to verify.

### Managing Clients

Applications should manage how they open and close the eventhub client.  It is essential to be aware that your application is responsible for calling `close()` when it is finished using a client or to use the `with` statement for clients so that they are automatically closed after the flow execution leaves that block. This make sures that the socket connection to the server is closed correctly. If the client is not closed this can leave AMQP connections open, underlying socket connections open and prevent other clean up activities from running.

### Cannot add components to the connection string

The current generation of the Event Hubs clients supports connection strings only in the form published by the Azure portal. These are intended to provide basic location and shared key information only; configuring behavior of the clients is done through its options.

Previous generations of the Event Hubs clients allowed for some behavior to be configured by adding key/value components to a connection string. These components are no longer recognized and have no effect on client behavior.

### Connect using an IoT connection string

Because translating a connection string requires querying the IoT Hub service, the Event Hubs client library cannot use it directly.  The [IoT Hub Connection String Sample][IoTConnectionString] sample describes how to query IoT Hub to translate an IoT connection string into one that can be used with Event Hubs.

Further reading:
* [Control access to IoT Hub using Shared Access Signatures][IoTHubSAS]
* [Read device-to-cloud messages from the built-in endpoint][IoTEventHubEndpoint]

#### Adding "TransportType=AmqpOverWebsocket"

To use web sockets, pass in a kwarg `transport_type = TransportType.AmqpOverWebsocket` during client [creation][WebsocketConfig].

#### Adding "Authentication=Managed Identity"

To authenticate with Managed Identity, see the [sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/sync_samples/client_identity_authentication.py).

For more information about the `azure.identity` library, check out our [Authentication and the Azure SDK][AuthenticationAndTheAzureSDK] blog post.

## Enable and configure logging

The Azure SDK for Python offers a consistent logging story to help troubleshoot application errors and expedite their resolution.  The logs produced will capture the flow of an application before reaching the terminal state to help locate the root issue.

This library uses the standard [Logging] library for logging and an example to set up debug logging with transport level logging is [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub#logging).

```python
import logging
import sys

handler = logging.StreamHandler(stream=sys.stdout)
log_fmt = logging.Formatter(fmt="%(asctime)s | %(threadName)s | %(levelname)s | %(name)s | %(message)s")
handler.setFormatter(log_fmt)
logger = logging.getLogger('azure.eventhub')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

...

from azure.eventhub import EventHubProducerClient, EventHubConsumerClient

producer = EventHubProducerClient(..., logging_enable=True)
consumer = EventHubConsumerClient(..., logging_enable=True)

```

- Enable `azure.eventhub` logger to collect traces from the library.

### Enable AMQP transport logging

If enabling client logging is not enough to diagnose your issues. You can enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

### Logging required for filing Github issues

When filing issues on Github please make sure that `DEBUG` level logs are enabled along with transport logging. You can find instructions on enabling logging [here](#enable-and-configure-logging). This provides the team with the information necessary best help you further. Ideally the time period spans at least +/- 10 minutes from when the issue occured as it can show patterns leading up to/after the issue that help in diagnosis and troubleshooting. Take a look at [Get Additional Help](#get-additional-help) for more information.

## Troubleshoot EventHubProducerClient (Sync/Async) issues

### Cannot set multiple partition keys for events in EventDataBatch

When publishing messages, the Event Hubs service supports a single partition key for each EventDataBatch.  Customers can consider using the producer client in `buffered mode` if they want that capability.  Otherwise, they'll have to manage their batches.

### Setting partition key on EventData is not set in Kafka consumer

The partition key of the EventHubs event is available in the Kafka record headers, the protocol specific key being "x-opt-partition-key" in the header.

By design, Event Hubs does not promote the Kafka message key to be the Event Hubs partition key nor the reverse because with the same value, the Kafka client and the Event Hubs client likely send the message to two different partitions.  It might cause some confusion if we set the value in the cross-protocol communication case.  Exposing the properties with a protocol specific key to the other protocol client should be good enough.

### Buffered producer not sending events

The sync buffered producer client uses the ThreadPoolExecutor to manage the partitions and ensure that messages are sent in a timely manner. If it's observed that messages are not being sent for a particular partition, ensure that there are enough workers available for all the partitions. By default ThreadPoolExecutor uses the formula described [here](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor) to allocate max_workers. Keyword argument `buffer_concurrency` can be used to set the desired number of workers or accept a ThreadPoolExecutor with `max_workers` specified. We recommend one worker per partition.

## Troubleshoot EventHubConsumerClient issues

### Logs reflect intermittent HTTP 412 and HTTP 409 responses from storage

This is normal and doesn't an indicate an issue with the consumer or the checkpoint store.

An HTTP 412 precondition response occurs when the event processor requests ownership of a partition, but that partition was recently claimed by another processor. An HTTP 409 occurs when the processor issues a "create if not exists" call when creating data and the item already exists.

Though these are expected scenarios, because the HTTP response code falls into the 400-499 range, Application Insights and other logging platforms are likely to surface them as errors.

### Partitions close and initialize intermittently or during scaling

This is usually normal and most often does not indicate an issue with the processor.

Event Hubs consumers configured to use the same Event Hubs, consumer group, and checkpoint store will coordinate with one another to share the responsibility of processing partitions. When the number of event consumers changes, usually when scaling up/down, ownership of partitions is re-balanced and some may change owners.

During this time, it is normal and expected to see partitions initializing and closing across event consumers. After one or two minutes, ownership should stabilize and the frequency that partitions close and initialize should decrease. While ownership is stable, some error recovery scenarios may trigger partitions closing and initializing occasionally.

### Partitions close and initialize frequently

If the number of consumers configured to use the same Event Hubs, consumer group, and checkpoint store are being scaled or if host nodes are being rebooted, partitions closing and initializing frequently for a short time is normal and expected. If the behavior persists longer than five minutes, it likely indicates a problem.

### "...current receiver '<RECEIVER_NAME>' with epoch '0' is getting disconnected"

The entire error message looks something like this:

> New receiver 'nil' with higher epoch of '0' is created hence current receiver 'nil' with epoch '0'
> is getting disconnected. If you are recreating the receiver, make sure a higher epoch is used.
> TrackingId:<GUID>, SystemTracker:<NAMESPACE>:eventhub:<EVENT_HUB_NAME>|<CONSUMER_GROUP>,
> Timestamp:2022-01-01T12:00:00}"}

This error is expected when load balancing occurs after EventHubConsumerClient instances are added or removed.  Load balancing is an ongoing process.  When using the BlobCheckpointStore with your consumer, every ~30 seconds (by default), the consumer will check to see which consumers have a claim for each partition, then run some logic to determine whether it needs to 'steal' a partition from another consumer.  The service mechanism used to assert exclusive ownership over a partition is known as the [Epoch][Epoch].

However, if no instances are being added or removed, there is an underlying issue that should be addressed.  See [Partition ownership changes a lot](#partition-ownership-changes-a-lot) for additional information and [Filing GitHub issues](#filing-github-issues).

### Blocking Calls in Async

When working with the async clients, applications should ensure that they are not blocking the event loop as the load balancing operation runs as a task in the background. Blocking the event loop can impact load balancing, error handling, checkpointing, and recovering after an error. CPU-bound code that can block the event loop should be run in [executor](https://docs.python.org/3/library/asyncio-dev.html#running-blocking-code).

### High CPU usage

High CPU usage is usually because an instance owns too many partitions.  We recommend no more than three partitions for every 1 CPU core; better to start with 1.5 partitions for each CPU core and test increasing the number of partitions owned.

### One or more partitions have high latency for processing

When processing for one or more partitions is delayed, it is most often because an event processor owns too many partitions. Consider adding additional consumers to handle partitions, we generally recommend 1 - 3 partitions per consumer depending on throughput.

### A partition is not being processed

An event consumer runs continually in a host application for a prolonged period. Sometimes, it may appear that some partitions are uncrowned or are not being processed. Most often, this presents as [partitions closing and initialize frequently](#partitions-close-and-initialize-frequently) or there are other errors/warnings being raised related to the problem.

If partitions are not observed closing and initializing frequently and no warning is being raised to the error callback, then a stalled or unowned partition may be part of a larger problem and a GitHub issue should be opened. Please see: [Filing GitHub issues](#filing-github-issues).

### Duplicate events are being processed

This is usually normal and most often does not indicate an issue unless partitions are frequently closing and initializing.

An important call-out is that Event Hubs has an at-least-once delivery guarantee; it is highly recommended that applications ensure that processing is resilient to event duplication in whatever way is appropriate for their environment and application scenarios.

Event processors configured to use the same Event Hub, consumer group, and checkpoint store will coordinate with one another to share the responsibility of processing partitions. When a processor isn’t able to reach its fair share of the work by claiming unowned partitions, it will attempt to steal ownership from other event processors. During this time, the new owner will begin reading from the last recorded checkpoint. At the same time, the old owner may be dispatching the events that it last read to the handler for processing; it will not understand that ownership has changed until it attempts to read the next set of events from the Event Hubs service.

As a result, there will be an amount of duplicate events being processed when event processors are started or stopped which will subside when partition ownership has stabilized. if the partition frequently takes 5 minutes to initialize, it likely indicates a problem.

### "Soft Delete" or "Blob versioning" is enabled for a Blob Storage checkpoint store

To coordinate with other event processors, the checkpoint store ownership records are inspected during each load balancing cycle.  When using an Azure Blob Storage as a checkpoint store, the "soft delete" and "Blob versioning" features can cause large delays when attempting to read the contents of a container.  It is strongly recommended that both be disabled.  For more information, see: [Soft delete for blobs][SoftDeleteBlobStorage] and [Blob versioning][VersioningBlobStorage].

### Migrate from legacy to new client library

The [migration guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/migration_guide.md) includes steps on migrating from the legacy client and migrating legacy checkpoints.

## Get additional help

Additional information on ways to reach out for support can be found in the [SUPPORT.md][SUPPORT] at the repo's root.

### Filing GitHub issues

When filing GitHub issues, the following details are requested:

* Event Hubs environment
  * How many partitions?
* EventHubConsumerClient environment
  * What is the machine(s) specs processing your Event Hubs?
  * How many instances are running?
* What is the average size of each EventData?
* What is the traffic pattern like in your Event Hubs?  (i.e. # messages/minute and if the EventHubConsumerClient is always busy or has slow traffic periods.)
* Repro code and steps
  * This is important as we often cannot reproduce the issue in our environment.
* Logs.  DEBUG level logs are needed to best help you. If that is not possible, INFO level logs must be provided.  ERROR and WARNING level logs do not provide enough information to help debug the issue in most cases.  The time period for logs must be at least +/- 10 minutes from when the issue occurred. See the [Enable and configure logging](#enable-and-configure-logging) section for more information.

<!-- repo links -->
[IoTConnectionString]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/async_samples/iot_hub_connection_string_receive_async.py
[PublishEventsWithWebSocketsAndProxy]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/async_samples/proxy_async.py
[WebsocketConfig]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/async_samples/send_and_receive_amqp_annotated_message_async.py#L95
[MigrationGuide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/migration_guide.md
[ClientCreation]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/sync_samples/client_creation.py
[SUPPORT]: https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md

<!-- learn.microsoft.com links -->
[ExceptionModule]: https://learn.microsoft.com/python/api/azure-eventhub/azure.eventhub.exceptions
[EventHubError]: https://learn.microsoft.com/python/api/azure-eventhub/azure.eventhub.exceptions.eventhuberror
[AmqpTroubleshooting]: https://learn.microsoft.com/azure/service-bus-messaging/service-bus-amqp-troubleshoot
[AuthorizeSAS]: https://learn.microsoft.com/azure/event-hubs/authorize-access-shared-access-signature
[RBACRoles]: https://learn.microsoft.com/azure/event-hubs/troubleshoot-authentication-authorization
[Epoch]: https://learn.microsoft.com/azure/event-hubs/event-hubs-event-processor-host#epoch
[EventHubsIPAddresses]: https://learn.microsoft.com/azure/event-hubs/troubleshooting-guide#what-ip-addresses-do-i-need-to-allow
[EventHubsMessagingExceptions]: https://learn.microsoft.com/azure/event-hubs/event-hubs-messaging-exceptions
[EventHubsTroubleshooting]: https://learn.microsoft.com/azure/event-hubs/troubleshooting-guide
[GetConnectionString]: https://learn.microsoft.com/azure/event-hubs/event-hubs-get-connection-string
[IoTEventHubEndpoint]: https://learn.microsoft.com/azure/iot-hub/iot-hub-devguide-messages-read-builtin
[IoTHubSAS]: https://learn.microsoft.com/azure/iot-hub/iot-hub-dev-guide-sas#security-tokens
[TroubleshootAuthenticationAuthorization]: https://learn.microsoft.com/azure/event-hubs/troubleshoot-authentication-authorization

<!-- external links -->
[AuthenticationAndTheAzureSDK]: https://devblogs.microsoft.com/azure-sdk/authentication-and-the-azure-sdk
[AmqpSpec]: https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-types-v1.0-os.html
[Logging]: https://docs.python.org/3/library/logging.html
