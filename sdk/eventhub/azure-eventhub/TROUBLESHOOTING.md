# Troubleshoot Event Hubs issues

This troubleshooting guide covers failure investigation techniques, common errors for the credential types in the Azure Event Hubs Python client library, and mitigation steps to resolve these errors.

- [Handle Event Hubs exceptions](#handle-event-hubs-exceptions)
  - [Find relevant information in exception messages](#find-relevant-information-in-exception-messages)
  - [Commonly encountered exceptions](#commonly-encountered-exceptions)
- [Permission issues](#permission-issues)
- [Connectivity issues](#connectivity-issues)
  - [Timeout when connecting to service](#timeout-when-connecting-to-service)
  - [SSL handshake failures](#ssl-handshake-failures)
  - [Socket exhaustion errors](#socket-exhaustion-errors)
  - [Connect using an IoT connection string](#connect-using-an-iot-connection-string)
  - [Cannot add components to the connection string](#cannot-add-components-to-the-connection-string)
- [Enable and configure logging](#enable-and-configure-logging)
  - [Configuring Log4J 2](#configuring-log4j-2)
  - [Configuring logback](#configuring-logback)
  - [Enable AMQP transport logging](#enable-amqp-transport-logging)
  - [Reduce logging](#reduce-logging)
- [Troubleshoot EventProducerAsyncClient/EventProducerClient issues](#troubleshoot-eventproducerasyncclienteventproducerclient-issues)
  - [Cannot set multiple partition keys for events in EventDataBatch](#cannot-set-multiple-partition-keys-for-events-in-eventdatabatch)
  - [Setting partition key on EventData is not set in Kafka consumer](#setting-partition-key-on-eventdata-is-not-set-in-kafka-consumer)
- [Troubleshoot EventHubConsumerClient issues](#troubleshoot-eventprocessorclient-issues)
  - [412 precondition failures when using an event processor](#412-precondition-failures-when-using-an-event-processor)
  - [Partition ownership changes frequently](#partition-ownership-changes-frequently)
  - ["...current receiver '<RECEIVER_NAME>' with epoch '0' is getting disconnected"](#current-receiver-receiver_name-with-epoch-0-is-getting-disconnected)
  - [High CPU usage](#high-cpu-usage)
  - [Processor client stops receiving](#processor-client-stops-receiving)
  - [Migrate from legacy to new client library](#migrate-from-legacy-to-new-client-library)
- [Get additional help](#get-additional-help)
  - [Filing GitHub issues](#filing-github-issues)

## Handle Event Hubs exceptions

All Event Hubs exceptions are wrapped in an [EventHubError][EventHubError].  They often have an underlying AMQP error code which specifies whether an error should be retried.  For retryable errors (ie. `amqp:connection:forced` or `amqp:link:detach-forced`), the client libraries will attempt to recover from these errors based on the [retry options][AmqpRetryOptions] specified when instantiating the client.  To configure retry options, follow the sample [Client Creation][ClientCreation].  If the error is non-retryable, there is some configuration issue that needs to be resolved.

The recommended way to solve the specific exception the AMQP exception represents is to follow the
[Event Hubs Messaging Exceptions][EventHubsMessagingExceptions] guidance.

### Find relevant information in exception messages

An [EventHubError][EventHubError] contains three fields which describe the error:

* **message**: The underlying AMQP error message. A description of the errors can be found in the [Exceptions module][ExceptionModule] or the [OASIS AMQP 1.0 spec][AmqpSpec].
* **error**: The error condition if available.
* **details**: The error details, if included in the service response.
  
### Commonly encountered exceptions

#### `amqp:connection:forced` and `amqp:link:detach-forced`

When the connection to Event Hubs is idle, the service will disconnect the client after some time.  This is not a problem as the clients will re-establish a connection when a service operation is requested.  More information can be found in the [AMQP troubleshooting documentation][AmqpTroubleshooting].

## Permission issues

An `AuthenticationError` means that the provided credentials do not allow for them to perform the action (receiving or sending) with Event Hubs.

* [Double check you have the correct connection string][GetConnectionString]
* [Ensure your SAS token is generated correctly][AuthorizeSAS]

[Troubleshoot authentication and authorization issues with Event Hubs][troubleshoot_authentication_authorization] lists other possible solutions.

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

### Socket exhaustion errors

Applications should prefer treating the Event Hubs clients as a singleton, creating and using a single instance through the lifetime of their application.  This is important as each client type manages its connection; creating a new Event Hub client results in a new AMQP connection, which uses a socket.  Additionally, it is essential to be aware that your client is responsible for calling `close()` when it is finished using a client or to use the `with statement` for clients so that they are automatically closed after the flow execution leaves that block.

### Connect using an IoT connection string

Because translating a connection string requires querying the IoT Hub service, the Event Hubs client library cannot use it directly.  The [IoT Hub Connection String Sample][IoTConnectionString] sample describes how to query IoT Hub to translate an IoT connection string into one that can be used with Event Hubs.

Further reading:
* [Control access to IoT Hub using Shared Access Signatures][IoTHubSAS]
* [Read device-to-cloud messages from the built-in endpoint][IoTEventHubEndpoint]

### Cannot add components to the connection string

The legacy Event Hub clients allowed customers to add components to the connection string retrieved from the portal.  The legacy clients are in packages [com.microsoft.azure:azure-eventhubs][MavenAzureEventHubs] and [com.microsoft.azure:azure-eventhubs-eph][MavenAzureEventHubsEPH].  The current generation supports connection strings only in the form published by the Azure portal.

#### Adding "TransportType=AmqpWebSockets"

To use web sockets, pass in a kwarg `transport_type = TransportType.AmqpOverWebsocket` during client creation.

#### Adding "Authentication=Managed Identity"

To authenticate with Managed Identity, see the sample [client_identity_authentication.py][PublishEventsWithAzureIdentity].

For more information about the `Azure.Identity` library, check out our [Authentication and the Azure SDK][AuthenticationAndTheAzureSDK] blog post.

## Enable and configure logging

The Azure SDK for Python offers a consistent logging story to help troubleshoot application errors and expedite their resolution.  The logs produced will capture the flow of an application before reaching the terminal state to help locate the root issue.

This library uses the standard [Logging] library for logging

- Enable `azure.eventhub` logger to collect traces from the library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.

### Enable AMQP transport logging

If enabling client logging is not enough to diagnose your issues. You can enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

### Reduce logging

There may be cases where you consider the `uamqp` logging to be too verbose. To suppress unnecessary logging, add the following snippet to the top of your code:

```python
import logging

# The logging levels below may need to be adjusted based on the logging that you want to suppress.
uamqp_logger = logging.getLogger('uamqp')
uamqp_logger.setLevel(logging.ERROR)

# or even further fine-grained control, suppressing the warnings in uamqp.connection module
uamqp_connection_logger = logging.getLogger('uamqp.connection')
uamqp_connection_logger.setLevel(logging.ERROR)
```

## Troubleshoot EventHubProducerClient (Sync/Async) issues

### Cannot set multiple partition keys for events in EventDataBatch

When publishing messages, the Event Hubs service supports a single partition key for each EventDataBatch.  Customers can consider using the producer client in `buffered mode` if they want that capability.  Otherwise, they'll have to manage their batches.

### Setting partition key on EventData is not set in Kafka consumer

The partition key of the EventHubs event is available in the Kafka record headers, the protocol specific key being "x-opt-partition-key" in the header.

By design, Event Hubs does not promote the Kafka message key to be the Event Hubs partition key nor the reverse because with the same value, the Kafka client and the Event Hub client likely send the message to two different partitions.  It might cause some confusion if we set the value in the cross-protocol communication case.  Exposing the properties with a protocol specific key to the other protocol client should be good enough.

## Troubleshoot EventHubConsumerClient issues

### 412 precondition failures when using an event processor

412 precondition errors occur when the client tries to take or renew ownership of a partition, but the local version of the ownership record is outdated.  This occurs when another processor instance steals partition ownership.  See [Partition ownership changes a lot](#partition-ownership-changes-a-lot) for more information.

### Partition ownership changes frequently

When the number of EventHubConsumerClient instances changes (i.e. added or removed), the running instances try to load-balance partitions between themselves.  For a few minutes after the number of processors changes, partitions are expected to change owners.   Once balanced, partition ownership should be stable and change infrequently.  If partition ownership is changing frequently when the number of processors is constant, this likely indicates a problem.  It is recommended that a GitHub issue with logs and a repro be filed in this case.

### "...current receiver '<RECEIVER_NAME>' with epoch '0' is getting disconnected"

The entire error message looks something like this:

> New receiver 'nil' with higher epoch of '0' is created hence current receiver 'nil' with epoch '0'
> is getting disconnected. If you are recreating the receiver, make sure a higher epoch is used.
> TrackingId:<GUID>, SystemTracker:<NAMESPACE>:eventhub:<EVENT_HUB_NAME>|<CONSUMER_GROUP>,
> Timestamp:2022-01-01T12:00:00}"}

This error is expected when load balancing occurs after EventHubConsumerClient instances are added or removed.  Load balancing is an ongoing process.  When using the BlobCheckpointStore with your consumer, every ~30 seconds (by default), the consumer will check to see which consumers have a claim for each partition, then run some logic to determine whether it needs to 'steal' a partition from another consumer.  The service mechanism used to assert exclusive ownership over a partition is known as the [Epoch][Epoch].

However, if no instances are being added or removed, there is an underlying issue that should be addressed.  See [Partition ownership changes a lot](#partition-ownership-changes-a-lot) for additional information and [Filing GitHub issues](#filing-github-issues).

### High CPU usage

High CPU usage is usually because an instance owns too many partitions.  We recommend no more than three partitions for every 1 CPU core; better to start with 1.5 partitions for each CPU core and test increasing the number of partitions owned.

### Processor client stops receiving

The processor client often is continually running in a host application for days on end.  Sometimes, they notice that EventHubConsumerClient is not processing one or more partitions.  Usually, this is not enough information to determine why the exception occurred.  The EventHubConsumerClient stopping is the symptom of an underlying cause (i.e. race condition) that occurred while trying to recover from a transient error.  Please see [Filing Github issues](#filing-github-issues) for the information we require.

### Migrate from legacy to new client library

The [migration guide][MigrationGuide] includes steps on migrating from the legacy client and migrating legacy checkpoints.

## Get additional help

Additional information on ways to reach out for support can be found in the [SUPPORT.md][SUPPORT] at the repo's root.

### Filing GitHub issues

When filing GitHub issues, the following details are requested:

* Event Hub environment
  * How many partitions?
* EventHubConsumerClient environment
  * What is the machine(s) specs processing your Event Hub?
  * How many instances are running?
* What is the average size of each EventData?
* What is the traffic pattern like in your Event Hub?  (i.e. # messages/minute and if the EventHubConsumerClient is always busy or has slow traffic periods.)
* Repro code and steps
  * This is important as we often cannot reproduce the issue in our environment.
* Logs.  We need DEBUG logs, but if that is not possible, INFO at least.  Error and warning level logs do not provide enough information.  The period of at least +/- 10 minutes from when the issue occurred.

<!-- repo links -->
[IoTConnectionString]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventhub/azure-eventhub/samples/async_samples/iot_hub_connection_string_receive_async.py

<!-- docs.microsoft.com links -->
[ExceptionModule]: https://docs.microsoft.com/python/api/azure-eventhub/azure.eventhub.exceptions
[EventHubError]: https://docs.microsoft.com/python/api/azure-eventhub/azure.eventhub.exceptions.eventhuberror
[AmqpTroubleshooting]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-amqp-troubleshoot
[AuthorizeSAS]: https://docs.microsoft.com/azure/event-hubs/authorize-access-shared-access-signature
[Epoch]: https://docs.microsoft.com/azure/event-hubs/event-hubs-event-processor-host#epoch
[EventHubsIPAddresses]: https://docs.microsoft.com/azure/event-hubs/troubleshooting-guide#what-ip-addresses-do-i-need-to-allow
[EventHubsMessagingExceptions]: https://docs.microsoft.com/azure/event-hubs/event-hubs-messaging-exceptions
[EventHubsTroubleshooting]: https://docs.microsoft.com/azure/event-hubs/troubleshooting-guide
[GetConnectionString]: https://docs.microsoft.com/azure/event-hubs/event-hubs-get-connection-string
[IoTEventHubEndpoint]: https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-messages-read-builtin
[IoTHubSAS]: https://docs.microsoft.com/azure/iot-hub/iot-hub-dev-guide-sas#security-tokens
[troubleshoot_authentication_authorization]: https://docs.microsoft.com/azure/event-hubs/troubleshoot-authentication-authorization

<!-- external links -->
[AuthenticationAndTheAzureSDK]: https://devblogs.microsoft.com/azure-sdk/authentication-and-the-azure-sdk
[AmqpSpec]: https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-types-v1.0-os.html
[Logging]: https://docs.python.org/3/library/logging.html
