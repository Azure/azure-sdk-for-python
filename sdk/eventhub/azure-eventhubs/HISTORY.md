# Release History

## 5.0.0b1 (2019-06-25)

- Added more configuration parameters when creating EventHubClient.
- New error hierarchy
  - `azure.error.EventHubError`
  - `azure.error.ConnectionLostError`
  - `azure.error.ConnectError`
  - `azure.error.AuthenticationError`
  - `azure.error.EventDataError`
  - `azure.error.EventDataSendError`
- Renamed Sender/Receiver to EventHubProducer/EventHubConsumer
  - New APIs for creating EventHubProducer/EventHubConsumer.
  - EventHubConsumer is now iterable.
- Rename class azure.eventhub.Offset to azure.eventhub.EventPosition
- Reorganized connection management, EventHubClient is no longer responsible for opening/closing EventHubProducer/EventHubConsumer.
  - Each EventHubProducer/EventHubConsumer is responsible for its own connection management.
  - Added support for context manager on EventHubProducer and EventHubConsumer.
- Reorganized async APIs into "azure.eventhub.aio" namespace and rename to drop the "_async" suffix.
- Added support for authentication using azure-core credential.
- Added support for transport using AMQP over WebSocket.
- Updated uAMQP dependency to 1.2.0


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