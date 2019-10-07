# Release History

## 5.0.0b4 (2019-10-08)

**New features**

- Added support for tracing (issue #7153).
- Added the capability of tracking last enqueued event properties of the partition to `EventHubConsumer` .
    - Added new boolean type parameter`track_last_enqueued_event_properties` in method `EventHubClient.create_consumer()`.
    - Added new property `last_enqueued_event_properties` of `EventHubConsumer` which contains sequence_number, offset, enqueued_time and retrieval_time information.
    - By default the capability is disabled as it will cost extra bandwidth for transferring more information if turned on.

**Breaking changes**

- Removed support for IoT Hub direct connection.
    - [EventHubs compatible connection string](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-read-builtin) of an IotHub can be used to create `EventHubClient` and read properties or events from an IoT Hub.
- Removed support for sending EventData to IoT Hub.
- Removed parameter `exception` in method `close()` of `EventHubConsumer` and `EventHubProcuer`.
- Updated uAMQP dependency to 1.2.3.

## 5.0.0b3 (2019-09-10)

**New features**

- Added support for automatic load balancing among multiple `EventProcessor`.
- Added `BlobPartitionManager` which implements `PartitionManager`.
    - Azure Blob Storage is applied for storing data used by `EventProcessor`.
    - Packaged separately as a plug-in to `EventProcessor`.
    - For details, please refer to [Azure Blob Storage Partition Manager](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhubs-checkpointstoreblob-aio).
- Added property `system_properties` on `EventData`.

**Breaking changes**

- Removed constructor method of `PartitionProcessor`. For initialization please implement the method `initialize`.
- Replaced `CheckpointManager` by `PartitionContext`.
    - `PartitionContext` has partition context information and method `update_checkpoint`.
- Updated all methods of `PartitionProcessor` to include `PartitionContext` as part of the arguments.
- Updated accessibility of class members in `EventHub/EventHubConsumer/EventHubProducer`to be private.
- Moved `azure.eventhub.eventprocessor` under `aio` package, which now becomes `azure.eventhub.aio.eventprocessor`.

## 5.0.0b2 (2019-08-06)

**New features**

- Added method `create_batch` on the `EventHubProducer` to create an `EventDataBatch` that can then be used to add events until the maximum size is reached.
    - This batch object can then be used in the `send()` method to send all the added events to Event Hubs.
    - This allows publishers to build batches without the possibility of encountering the error around the message size exceeding the supported limit when sending events.
    - It also allows publishers with bandwidth concerns to control the size of each batch published.
- Added new configuration parameters for exponential delay between retry operations.
    - `retry_total`: The total number of attempts to redo the failed operation.
    - `backoff_factor`: The delay time factor.
    - `backoff_max`: The maximum delay time in total.
- Added support for context manager on `EventHubClient`.
- Added new error type `OperationTimeoutError` for send operation.
- Introduced a new class `EventProcessor` which replaces the older concept of [Event Processor Host](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-event-processor-host). This early preview is intended to allow users to test the new design using a single instance of `EventProcessor`. The ability to checkpoints to a durable store will be added in future updates.
    - `EventProcessor`: EventProcessor creates and runs consumers for all partitions of the eventhub.
    - `PartitionManager`: PartitionManager defines the interface for getting/claiming ownerships of partitions and updating checkpoints.
    - `PartitionProcessor`: PartitionProcessor defines the interface for processing events.
    - `CheckpointManager`: CheckpointManager takes responsibility for updating checkpoints during events processing.

**Breaking changes**

- `EventProcessorHost` was replaced by `EventProcessor`, please read the new features for details.
- Replaced `max_retries` configuration parameter of the EventHubClient with `retry_total`.


## 5.0.0b1 (2019-06-25)

Version 5.0.0b1 is a preview of our efforts to create a client library that is user friendly and idiomatic to the Python ecosystem. The reasons for most of the changes in this update can be found in the [Azure SDK Design Guidelines for Python](https://azuresdkspecs.z5.web.core.windows.net/PythonSpec.html). For more information, please visit https://aka.ms/azure-sdk-preview1-python.

**New features**

- Added new configuration parameters for creating EventHubClient.
  - `credential`: The credential object used for authentication which implements `TokenCredential` interface of getting tokens.
  - `transport_type`: The type of transport protocol that will be used for communicating with the Event Hubs service.
  - `max_retries`: The max number of attempts to redo the failed operation when an error happened.
  - for detailed information about the configuration parameters, please read the reference documentation.
- Added new methods `get_partition_properties` and `get_partition_ids` to EventHubClient.
- Added support for http proxy.
- Added support for authentication using azure-identity credential.
- Added support for transport using AMQP over WebSocket.

**Breaking changes**

- New error hierarchy
  - `azure.error.EventHubError`
  - `azure.error.ConnectionLostError`
  - `azure.error.ConnectError`
  - `azure.error.AuthenticationError`
  - `azure.error.EventDataError`
  - `azure.error.EventDataSendError`
- Renamed Sender/Receiver to EventHubProducer/EventHubConsumer.
  - Renamed `add_sender` to `create_producer` and `add_receiver` to `create_consumer` in EventHubClient.
  - EventHubConsumer is now iterable.
- Rename class azure.eventhub.Offset to azure.eventhub.EventPosition.
- Rename method `get_eventhub_info` to `get_properties` of EventHubClient.
- Reorganized connection management, EventHubClient is no longer responsible for opening/closing EventHubProducer/EventHubConsumer.
  - Each EventHubProducer/EventHubConsumer is responsible for its own connection management.
  - Added support for context manager on EventHubProducer and EventHubConsumer.
- Reorganized async APIs into "azure.eventhub.aio" namespace and rename to drop the "_async" suffix.
- Updated uAMQP dependency to 1.2.

## 1.3.1 (2019-02-28)

**BugFixes**

- Fixed bug where datetime offset filter was using a local timestamp rather than UTC.
- Fixed stackoverflow error in continuous connection reconnect attempts.


## 1.3.0 (2019-01-29)

**BugFixes**

- Added support for auto reconnect on token expiration and other auth errors (issue #89).

**Features**

- Added ability to create ServiceBusClient from an existing SAS auth token, including
  providing a function to auto-renew that token on expiry.
- Added support for storing a custom EPH context value in checkpoint (PR #84, thanks @konstantinmiller)


## 1.2.0 (2018-11-29)

- Support for Python 2.7 in azure.eventhub module (azure.eventprocessorhost will not support Python 2.7).
- Parse EventData.enqueued_time as a UTC timestamp (issue #72, thanks @vjrantal)


## 1.1.1 (2018-10-03)

- Fixed bug in Azure namespace package.


## 1.1.0 (2018-09-21)

- Changes to `AzureStorageCheckpointLeaseManager` parameters to support other connection options (issue #61):
  - The `storage_account_name`, `storage_account_key` and `lease_container_name` arguments are now optional keyword arguments.
  - Added a `sas_token` argument that must be specified with `storage_account_name` in place of `storage_account_key`.
  - Added an `endpoint_suffix` argument to support storage endpoints in National Clouds.
  - Added a `connection_string` argument that, if specified, overrides all other endpoint arguments.
  - The `lease_container_name` argument now defaults to `"eph-leases"` if not specified.

- Fix for clients failing to start if run called multipled times (issue #64).
- Added convenience methods `body_as_str` and `body_as_json` to EventData object for easier processing of message data.


## 1.0.0 (2018-08-22)

- API stable.
- Renamed internal `_async` module to `async_ops` for docs generation.
- Added optional `auth_timeout` parameter to `EventHubClient` and `EventHubClientAsync` to configure how long to allow for token
  negotiation to complete. Default is 60 seconds.
- Added optional `send_timeout` parameter to `EventHubClient.add_sender` and `EventHubClientAsync.add_async_sender` to determine the
  timeout for Events to be successfully sent. Default value is 60 seconds.
- Reformatted logging for performance.


## 0.2.0 (2018-08-06)

- Stability improvements for EPH.
- Updated uAMQP version.
- Added new configuration options for Sender and Receiver; `keep_alive` and `auto_reconnect`.
  These flags have been added to the following:

  - `EventHubClient.add_receiver`
  - `EventHubClient.add_sender`
  - `EventHubClientAsync.add_async_receiver`
  - `EventHubClientAsync.add_async_sender`
  - `EPHOptions.keey_alive_interval`
  - `EPHOptions.auto_reconnect_on_error`


## 0.2.0rc2 (2018-07-29)

- **Breaking change** `EventData.offset` will now return an object of type `~uamqp.common.Offset` rather than str.
  The original string value can be retrieved from `~uamqp.common.Offset.value`.
- Each sender/receiver will now run in its own independent connection.
- Updated uAMQP dependency to 0.2.0
- Fixed issue with IoTHub clients not being able to retrieve partition information.
- Added support for HTTP proxy settings to both EventHubClient and EPH.
- Added error handling policy to automatically reconnect on retryable error.
- Added keep-alive thread for maintaining an unused connection.


## 0.2.0rc1 (2018-07-06)

- **Breaking change** Restructured library to support Python 3.7. Submodule `async` has been renamed and all classes from
  this module can now be imported from azure.eventhub directly.
- **Breaking change** Removed optional `callback` argument from `Receiver.receive` and `AsyncReceiver.receive`.
- **Breaking change** `EventData.properties` has been renamed to `EventData.application_properties`.
  This removes the potential for messages to be processed via callback for not yet returned
  in the batch.
- Updated uAMQP dependency to v0.1.0
- Added support for constructing IoTHub connections.
- Fixed memory leak in receive operations.
- Dropped Python 2.7 wheel support.


## 0.2.0b2 (2018-05-29)

- Added `namespace_suffix` to EventHubConfig() to support national clouds.
- Added `device_id` attribute to EventData to support IoT Hub use cases.
- Added message header to workaround service bug for PartitionKey support.
- Updated uAMQP dependency to vRC1.


## 0.2.0b1 (2018-04-20)

- Updated uAMQP to latest version.
- Further testing and minor bug fixes.


## 0.2.0a2 (2018-04-02)

- Updated uAQMP dependency.


## 0.2.0a1 (unreleased)

- Swapped out Proton dependency for uAMQP.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python/sdk/eventhub/azure-eventhubs/HISTORY.png)