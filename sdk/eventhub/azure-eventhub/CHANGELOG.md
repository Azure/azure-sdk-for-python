# Release History

## 5.8.0a4 (Unreleased)

### Features Added

- Added support for connection using websocket and http proxy.

## 5.8.0a3 (2022-03-08)

### Other Changes

- Improved the performance of async sending and receiving.

## 5.8.0a2 (2022-02-09)

### Features Added

- Added support for async `EventHubProducerClient` and `EventHubConsumerClient`.

### Breaking changes

- The following features have been temporarily pulled out of async `EventHubProducerClient` and `EventHubConsumerClient` which will be added back in future previews as we work towards a stable release:
  - Passing the following keyword arguments to the constructors and `from_connection_string` methods of the `EventHubProducerClient` and `EventHubConsumerClient` is not supported:  `transport_type`, `http_proxy`, `custom_endpoint_address`, and `connection_verify`.

## 5.8.0a1 (2022-01-13)

Version 5.8.0a1 is our first efforts to build an Azure Event Hubs client library based on pure python implemented AMQP stack.

### Breaking changes

- The following features have been temporarily pulled out which will be added back in future previews as we work towards a stable release:
  - Async is not supported.
  - Passing the following keyword arguments to the constructors and `from_connection_string` methods of the `EventHubProducerClient` and `EventHubConsumerClient` is not supported:  `transport_type`, `http_proxy`, `custom_endpoint_address`, and `connection_verify`.

### Other Changes

- uAMQP dependency is removed.

## 5.7.0 (2022-01-11)

### Features Added

- The classmethod `from_message_content` has been added to `EventData` for interoperability with the Schema Registry Avro Encoder library, and takes `content` and `content_type` as positional parameters.

### Other Changes

- Features related to buffered sending of events are still in beta and will not be included in this release.

### Features Added

- Added suppport for connection using websocket and http proxy.

### Breaking Changes

### Bugs Fixed

### Other Changes

## 5.8.0a3 (2022-03-08)

### Other Changes

- Improved the performance of async sending and receiving.

## 5.8.0a2 (2022-02-09)

### Features Added

- Added support for async `EventHubProducerClient` and `EventHubConsumerClient`.

### Breaking changes

- The following features have been temporarily pulled out of async `EventHubProducerClient` and `EventHubConsumerClient` which will be added back in future previews as we work towards a stable release:
  - Passing the following keyword arguments to the constructors and `from_connection_string` methods of the `EventHubProducerClient` and `EventHubConsumerClient` is not supported:  `transport_type`, `http_proxy`, `custom_endpoint_address`, and `connection_verify`.

## 5.8.0a1 (2022-01-13)

Version 5.8.0a1 is our first efforts to build an Azure Event Hubs client library based on pure python implemented AMQP stack.

### Breaking changes

- The following features have been temporarily pulled out which will be added back in future previews as we work towards a stable release:
  - Async is not supported.
  - Passing the following keyword arguments to the constructors and `from_connection_string` methods of the `EventHubProducerClient` and `EventHubConsumerClient` is not supported:  `transport_type`, `http_proxy`, `custom_endpoint_address`, and `connection_verify`.

### Other Changes

- uAMQP dependency is removed.

## 5.7.0 (2022-01-12)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Features Added

- Added support for fixed (linear) retry backoff:
  - Sync/async `EventHubProducerClient` and `EventHubConsumerClient` constructors and `from_connection_string` take `retry_mode` as a keyword argument.

### Bugs Fixed

- Fixed a bug that `EventHubProducerClient` could be reopened for sending events instead of encountering with `KeyError` when the client is previously closed (issue #21849).

### Other Changes

- Improved token refresh timing to prevent potentially blocking main flow when the token is about to get expired soon.
- Updated uAMQP dependency to 1.5.1.

## 5.6.1 (2021-10-06)

### Bugs Fixed

- Fixed a bug for checking that `azure.eventhub.amqp.AmqpMessageHeader` and `azure.eventhub.amqp.AmqpMessageProperties` contain specific properties using the `in` keyword.

### Other Changes

- Updated uAMQP dependency to 1.4.3.
  - Added support for Python 3.10.
  - Fixed memory leak in win32 socketio and tlsio (issue #19777).
  - Fixed memory leak in the process of converting AMQPValue into string (issue #19777).

## 5.6.0 (2021-07-07)

### Features Added

- Added support for sending AMQP annotated message which allows full access to the AMQP message fields.
  - Introduced new namespace `azure.eventhub.amqp`.
  - Added new enum class `azure.eventhub.amqp.AmqpMessageBodyType` to represent the body type of the message which includes:
    - `DATA`: The body of message consists of one or more data sections and each section contains opaque binary data.
    - `SEQUENCE`: The body of message consists of one or more sequence sections and each section contains an arbitrary number of structured data elements.
    - `VALUE`: The body of message consists of one amqp-value section and the section contains a single AMQP value.
  - Introduced new class `azure.eventhub.amqp.AmqpAnnotatedMessage` for accessing low-level amqp message sections which can be instantiated for sending.
  - Introduced new classes `azure.eventhub.amqp.AmqpMessageHeader` and `azure.eventhub.amqp.AmqpMessageProperties` for accessing amqp header and properties.
  - Added new property `body_type` on `azure.eventhub.EventData` which returns `azure.eventhub.amqp.AmqpMessageBodyType`.
  - Added new read-only property `raw_amqp_message` on `azure.eventhub.EventData` which returns `azure.eventhub.amqp.AmqpAnnotatedMessage`.

### Fixed

- Updated uAMQP dependency to 1.4.1.
  - Fixed a bug that attributes creation_time, absolute_expiry_time and group_sequence on MessageProperties should be compatible with integer types on Python 2.7.

## 5.5.0 (2021-05-13)

**New Features**

- Added support for using `azure.core.credentials.AzureNamedKeyCredential` as credential for authenticating producer and consumer clients.

**Bug Fixes**

- Fixed bug that custom user agent string should be put in front of the built-in user agent string instead of being appended.
- Updated uAMQP dependency to 1.4.0.
  - Fixed memory leaks in the process of link attach where source and target cython objects are not properly deallocated (#15747).
  - Improved management operation callback not to parse description value of non AMQP_TYPE_STRING type as string (#18361).

**Notes**

- Updated azure-core dependency to 1.14.0.

## 5.4.0 (2021-04-07)

This version follows from version 5.3.1, rather than 5.4.0b1 so that the preview idempotent producer feature is not included.

**New Features**

- Added support for using `azure.core.credentials.AzureSasCredential` as credential for authenticating producer and consumer clients.
- Updated `list_ownership`, `claim_ownership`, `update_checkpoint`, `list_checkpoints` on sync and async `CheckpointStore` to support taking `**kwargs`.
  - WARNING: Implementing a custom checkpointstore that does not support taking `**kwargs` in the methods listed previously will result in the following pylint error: `W0221: Parameters differ from overridden ________ method (arguments-differ)`.
- Updated `update_checkpoint` on sync and async `PartitionContext` to support taking `**kwargs`.

**Bug Fixes**

- Updated uAMQP dependency to 1.3.0.
  - Fixed bug that sending message of large size triggering segmentation fault when the underlying socket connection is lost (#13739, #14543).
  - Fixed bug in link flow control where link credit and delivery count should be calculated based on per message instead of per transfer frame (#16934).

**Notes**

- Updated azure-core dependency to 1.13.0.

## 5.4.0b1 (2021-03-09)

This version and all future versions will require Python 2.7 or Python 3.6+, Python 3.5 is no longer supported.

**New Features**

- Added support for idempotent publishing which is supported by the service to endeavor to reduce the number of duplicate
  events that are published.
  - `EventHubProducerClient` constructor accepts two new parameters for idempotent publishing:
    - `enable_idempotent_partitions`: A boolean value to tell the `EventHubProducerClient` whether to enable idempotency.
    - `partition_config`: The set of configurations that can be specified to influence publishing behavior
     specific to the configured Event Hub partition.
  - Introduced a new method `get_partition_publishing_properties` on `EventHubProducerClient` to inspect the information
    about the state of publishing for a partition.
  - Introduced a new property `published_sequence_number` on `EventData` to get the publishing sequence number assigned
    to the event at the time it was successfully published.
  - Introduced a new property `starting_published_sequence_number` on `EventDataBatch` to get the publishing sequence
    number assigned to the first event in the batch at the time the batch was successfully published.
  - Introduced a new class `azure.eventhub.PartitionPublishingConfiguration` which is a set of configurations that can be
    specified to influence the behavior when publishing directly to an Event Hub partition.

**Notes**

- Updated uAMQP dependency to 1.2.15.

## 5.3.1 (2021-03-09)

This version will be the last version to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

**Bug fixes**

- Sending empty `event_data_batch` will be a no-op now instead of raising error.

## 5.3.0 (2021-02-08)

**New Features**

- Added a `parse_connection_string` method which parses a connection string into a properties bag, `EventHubConnectionStringProperties`, containing its component parts.
- The constructor and `from_connection_string` method of `EventHubConsumerClient` and `EventHubProducerClient` now accept two new optional arguments:
  - `custom_endpoint_address` which allows for specifying a custom endpoint to use when communicating with the Event Hubs service,
and is useful when your network does not allow communicating to the standard Event Hubs endpoint.
  - `connection_verify` which allows for specifying the path to the custom CA_BUNDLE file of the SSL certificate which is used to authenticate
the identity of the connection endpoint.

**Notes**

- Updated uAMQP dependency to 1.2.14.

## 5.2.1 (2021-01-11)

**Bug fixes**

- Updated `azure.eventhub.extension.__init__.py` to be compatible with pkgutil-style namespace (PR #13210, thanks @pjachowi).
- Updated uAMQP dependency to 1.2.13
  - Added support for Python 3.9.
  - Fixed bug that macOS was unable to detect network error (#15473).
  - Fixed bug that `uamqp.ReceiveClient` and `uamqp.ReceiveClientAsync` receive messages during connection establishment (#15555).
  - Fixed bug where connection establishment on macOS with Clang 12 triggering unrecognized selector exception (#15567).
  - Fixed bug in accessing message properties triggering segmentation fault when the underlying C bytes are NULL (#15568).

## 5.2.0 (2020-09-08)

**New Features**

- Connection strings used with `from_connection_string` methods now supports using the `SharedAccessSignature` key in leiu of `sharedaccesskey` and `sharedaccesskeyname`, taking the string of the properly constructed token as value.

## 5.2.0b1 (2020-07-06)

**New Features**

- `EventHubConsumerClient` constructor accepts two new parameters for the load balancer.
    - `load_balancing_strategy`, which can be "greedy" or "balanced".
     With greedy strategy, one execution of load balancing will claim as many partitions as required to balance the load
     whereas with balanced strategy one execution of load balancing will claim at most 1 partition.
    - `partition_ownership_expiration_interval`, which allows you to customize the partition ownership expiration for load balancing.
     A consumer client may lose its owned partitions more often with a smaller expiration interval. But a larger interval
     may result in idle partitions not being claimed for longer time.
- Added enum class `azure.eventhub.LoadBalancingStrategy` for `load_balancing_strategy`.

## 5.1.0 (2020-05-04)

**New Features**

- `EventHubProducerClient.send_batch` accepts either an `EventDataBatch` or a finite list of `EventData`. #9181
- Added enqueueTime to span links of distributed tracing. #9599

**Bug fixes**

- Fixed a bug that turned `azure.eventhub.EventhubConsumerClient` into an exclusive receiver when it has no checkpoint store. #11181
- Updated uAMQP dependency to 1.2.7.
  - Fixed bug in setting certificate of tlsio on MacOS. #7201
  - Fixed bug that caused segmentation fault in network tracing on MacOS when setting `logging_enable` to `True` in `EventHubConsumerClient` and `EventHubProducerClient`.

## 5.1.0b1 (2020-04-06)

**New Features**

- Added `EventHubConsumerClient.receive_batch()` to receive and process events in batches instead of one by one. #9184
- `EventHubConsumerCliuent.receive()` has a new param `max_wait_time`.
`on_event` is called every `max_wait_time` when no events are received and `max_wait_time` is not `None` or 0.
- Param event of `PartitionContext.update_checkpoint` is now optional. The last received event is used when param event is not passed in.
- `EventData.system_properties` has added missing properties when consuming messages from IotHub. #10408

## 5.0.1 (2020-03-09)

**Bug fixes**

- Fixed a bug that swallowed errors when receiving events with `azure.eventhub.EventHubConsumerClient`  #9660
- Fixed a bug that caused `get_eventhub_properties`, `get_partition_ids`, and `get_partition_properties` to raise
an error on Azure Stack #9920

## 5.0.0 (2020-01-13)

**Breaking changes**

- `EventData`
    - Removed deprecated property `application_properties` and deprecated method `encode_message()`.
- `EventHubConsumerClient`
    - `on_error` would be called when `EventHubConsumerClient` failed to claim ownership of partitions.
    - `on_partition_close` and `on_partition_initialize` would be called in the case of exceptions raised by `on_event` callback.
        -  `EventHubConsumerClient` would close and re-open the internal partition receiver in this case.
    - Default starting position from where `EventHubConsumerClient` should resume receiving after recovering from an error has been re-prioritized.
        - If there is checkpoint, it will resume from the checkpoint.
        - If there is no checkpoint but `starting_position` is provided, it will resume from `starting_posititon`.
        - If there is no checkpoint or `starting_position`, it will resume from the latest position.
- `PartitionContext`
    - `update_checkpoint` would do in-memory checkpoint instead of doing nothing when checkpoint store is not explicitly provided.
        - The in-memory checkpoints would be used for `EventHubConsumerClient` receiving recovering.
- `get_partition_ids`, `get_partition_properties`, `get_eventhub_properties` would raise error in the case of service returning an error status code.
    - `AuthenticationError` would be raised when service returning error code 401.
    - `ConnectError` would be raised when service returning error code 404.
    - `EventHubError` would be raised when service returning other error codes.

## 5.0.0b6 (2019-12-03)

**Breaking changes**

- All exceptions should now be imported from `azure.eventhub.exceptions`.
- Introduced separate `EventHubSharedKeyCredential` objects for synchronous and asynchronous operations.
  For async, import the credentials object from the `azure.eventhub.aio` namespace.
- `EventData`
    - Renamed property `application_properties` to `properties`.
    - `EventData` no longer has attribute `last_enqueued_event_properties` - use this on `PartitionContext` instead.
- `EvenDataBatch`
    - `EventDataBatch.try_add` has been renamed to `EventDataBatch.add`.
    - Renamed property `size` to `size_in_bytes`.
    - Renamed attribute `max_size` to `max_size_in_bytes`.
- `EventHubConsumerClient` and `EventHubProducerClient`
    - Renamed method `get_properties` to `get_eventhub_properties`.
    - Renamed parameters in constructor: `host` to `fully_qualified_namespace`, `event_hub_path` to `eventhub_name`.
    - Renamed parameters in `get_partition_properties`: `partition` to `partition_id`.
    - Renamed parameter `consumer_group_name` to `consumer_group` and moved that parameter from `receive` method to the constructor of `EventHubConsumerClient`.
    - Renamed parameter `initial_event_position` to `starting_position` on the `receive` method of `EventHubConsumerClient`.
    - Renamed parameter `event_hub_path` to `eventhub_name` in constructor and `from_connection_string` method of the client object.
    - `EventHubProducerClient.send` has been renamed to `send_batch` which will only accept `EventDataBatch` object as input.
    - `EventHubProducerClient.create_batch` now also takes the `partition_id` and `partition_key` as optional parameters (which are no longer specified at send).
- Renamed module `PartitionManager` to `CheckpointStore`.
- Receive event callback parameter has been renamed to `on_event` and now operates on a single event rather than a list of events.
- Removed class `EventPostition`.
    - The `starting_position` parameter of the `receive` method accepts offset(`str`), sequence number(`int`), datetime (`datetime.datetime`) or `dict` of these types.
    - The `starting_position_inclusive` parameter of the `receive` method accepts `bool` or `dict` indicating whether the given event position is inclusive or not.
- `PartitionContext` no longer has attribute `owner_id`.
- `PartitionContext` now has attribute `last_enqueued_event_properties` which is populated if `track_last_enqueued_event_properties` is set to `True` in the `receive` method.

**New features**

- Added new parameter `idle_timeout` in construct and `from_connection_string` to `EventHubConsumerClient` and `EventHubProducerClient`
after which the underlying connection will close if there is no further activity.

## 5.0.0b5 (2019-11-04)

**Breaking changes**

- `EventHubClient`, `EventHubConsumer` and `EventHubProducer` has been removed. Use `EventHubProducerClient` and `EventHubConsumerClient` instead.
    - Construction of both objects is the same as it was for the previous client.
- Introduced `EventHubProducerClient` as substitution for`EventHubProducer`.
    - `EventHubProducerClient` supports sending events to different partitions.
- Introduced `EventHubConsumerClient` as substitution for `EventHubConsumer`.
    - `EventHubConsumerClient` supports receiving events from single/all partitions.
    - There are no longer methods which directly return `EventData`, all receiving is done via callback method: `on_events`.
- `EventHubConsumerClient` has taken on the responsibility of `EventProcessor`.
    - `EventHubConsumerClient` now accepts `PartitionManager` to do load-balancing and checkpoint.
- Replaced `PartitionProcessor`by four independent callback methods accepted by the `receive` method on `EventHubConsumerClient`.
    - `on_events(partition_context, events)` called when events are received.
    - `on_error(partition_context, exception` called when errors occur.
    - `on_partition_initialize(partition_context)` called when a partition consumer is opened.
    - `on_partition_close(partition_context, reason)` called when a partition consumer is closed.
- Some modules and classes that were importable from several different places have been removed:
    - `azure.eventhub.common` has been removed. Import from `azure.eventhub` instead.
    - `azure.eventhub.client_abstract` has been removed. Use `azure.eventhub.EventHubProducerClient` or `azure.eventhub.EventHubConsumerClient` instead.
    - `azure.eventhub.client` has been removed. Use `azure.eventhub.EventHubProducerClient` or `azure.eventhub.EventHubConsumerClient` instead.
    - `azure.eventhub.producer` has been removed. Use `azure.eventhub.EventHubProducerClient` instead.
    - `azure.eventhub.consumer` has been removed. Use `azure.eventhub.EventHubConsumerClient` instead.
    - `azure.eventhub.aio.client_async` has been removed. Use `azure.eventhub.aio.EventHubProducerClient` or `azure.eventhub.aio.EventHubConsumerClient` instead.
    - `azure.eventhub.aio.producer_async` has been removed. Use `azure.eventhub.aio.EventHubProducerClient` instead.
    - `azure.eventhub.aio.consumer_async` has been removed. Use `azure.eventhub.aio.EventHubConsumerClient` instead.
    - `azure.eventhub.aio.event_processor.event_processor` has been removed. Use `azure.eventhub.aio.EventHubConsumerClient` instead.
    - `azure.eventhub.aio.event_processor.partition_processor` has been removed. Use callback methods instead.
    - `azure.eventhub.aio.event_processor.partition_manager` has been removed. Import from `azure.eventhub.aio` instead.
    - `azure.eventhub.aio.event_processor.partition_context` has been removed. Import from `azure.eventhub.aio` instead.
    - `azure.eventhub.aio.event_processor.sample_partition_manager` has been removed.

**Bug fixes**

- Fixed bug in user-agent string not being parsed.

## 5.0.0b4 (2019-10-08)

**New features**

- Added support for tracing (issue #7153).
- Added the capability of tracking last enqueued event properties of the partition to `EventHubConsumer` .
    - Added new boolean type parameter`track_last_enqueued_event_properties` in method `EventHubClient.create_consumer()`.
    - Added new property `last_enqueued_event_properties` of `EventHubConsumer` which contains sequence_number, offset, enqueued_time and retrieval_time information.
    - By default the capability is disabled as it will cost extra bandwidth for transferring more information if turned on.

**Breaking changes**

- Removed support for IoT Hub direct connection.
    - [EventHubs compatible connection string](https://docs.microsoft.com/azure/iot-hub/iot-hub-devguide-messages-read-builtin) of an IotHub can be used to create `EventHubClient` and read properties or events from an IoT Hub.
- Removed support for sending EventData to IoT Hub.
- Removed parameter `exception` in method `close()` of `EventHubConsumer` and `EventHubProcuer`.
- Updated uAMQP dependency to 1.2.3.

## 5.0.0b3 (2019-09-10)

**New features**

- Added support for automatic load balancing among multiple `EventProcessor`.
- Added `BlobPartitionManager` which implements `PartitionManager`.
    - Azure Blob Storage is applied for storing data used by `EventProcessor`.
    - Packaged separately as a plug-in to `EventProcessor`.
    - For details, please refer to [Azure Blob Storage Partition Manager](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub-checkpointstoreblob-aio).
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
- Introduced a new class `EventProcessor` which replaces the older concept of [Event Processor Host](https://docs.microsoft.com/azure/event-hubs/event-hubs-event-processor-host). This early preview is intended to allow users to test the new design using a single instance of `EventProcessor`. The ability to checkpoints to a durable store will be added in future updates.
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


