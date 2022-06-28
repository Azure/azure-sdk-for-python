# Release History

## 7.8.0 (2022-07-07)

### Features Added

- In `ServiceBusClient`, `get_receiver` for `queue and subscription` and `get_sender` for `queue and topic` now accept
an optional `client_identifier` argument which allows for specifying a custom identifier for the respective sender or receiver. It can
be useful during debugging as Service Bus associates the id with errors and helps with easier correlation.
- `ServiceBusReceiver` and `ServiceBusSender` have an added property `identifier` which returns the `client_identifier` for the current instance.

## 7.7.0 (2022-06-07)

### Bugs Fixed

- Fixed bug to make AMQP exceptions retryable by default, if condition is not non-retryable, to ensure that InternalServerErrors are retried.

### Features Added

- The `ServiceBusClient` constructor now accepts optional `custom_endpoint_address` argument
which allows for specifying a custom endpoint to use when communicating with the Service Bus service,
and is useful when your network does not allow communicating to the standard Service Bus endpoint.
- The `ServiceBusClient`constructor now accepts optional `connection_verify` argument
which allows for specifying the path to the custom CA_BUNDLE file of the SSL certificate which is used to authenticate
the identity of the connection endpoint.

## 7.6.1 (2022-04-11)

### Other Changes

- Improved receiving by releasing messages from internal buffer when the `prefetch_count` of `ServiceBusReceiver`  is set 0 and there is no active receive call, this helps avoid receiving expired messages and incrementing delivery count of a message.

## 7.6.0 (2022-02-10)

### Features Added

- Introduce `ServiceBusMessageState` enum that can assume the values of `active`, `scheduled` or `deferred`.
- Add `state` property in `ServiceBusReceivedMessage`.

## 7.5.0 (2022-01-12)

This version and all future versions will require Python 3.6+. Python 2.7 is no longer supported.

### Features Added

- Added support for fixed (linear) retry backoff:
  - Sync/async `ServiceBusClient` constructors and `from_connection_string` take `retry_mode` as a keyword argument.
- Added new enum class `ServiceBusSessionFilter`, which is the type of existing `NEXT_AVAILABLE_SESSION` value.

### Bugs Fixed

- Fixed bug that when setting `ServiceBusMessage.time_to_live` with value being `datetime.timedelta`, `total_seconds` should be respected (PR #21869, thanks @jyggen).

### Other Changes

- Improved token refresh timing to prevent potentially blocking main flow when the token is about to get expired soon.
- Updated uAMQP dependency to 1.5.1.

## 7.4.0 (2021-11-09)

### Features Added

- GA the support to create and update queues and topics of large message size to `ServiceBusAdministrationClient`. This feature is only available for Service Bus of Premium Tier.
  - Methods`create_queue`, `create_topic`, `update_queue`, `update_topic` on `ServiceBusAdministrationClient` now take a new keyword argument `max_message_size_in_kilobytes`.
  - `QueueProperties` and `TopicProperties` now have a new instance variable `max_message_size_in_kilobytes`.
- The constructor of`ServiceBusAdministrationClient` as well as `ServiceBusAdministrationClient.from_connection_string` now take keyword argument `api_version` to configure the Service Bus API version. Supported service versions are "2021-05" and "2017-04".
- Added new enum class `azure.servicebus.management.ApiVersion` to represent the supported Service Bus API versions.

### Bugs Fixed

- Fixed bug that `ServiceBusReceiver` can not connect to sessionful entity with session id being empty string.
- Fixed bug that `ServiceBusMessage.partition_key` can not parse empty string properly.

## 7.4.0b1 (2021-10-06)

### Features Added

- Added support to create and update queues and topics of large message size to `ServiceBusAdministrationClient`. This feature is only available for Service Bus of Premium Tier.
  - Methods`create_queue`, `create_topic`, `update_queue`, `update_topic` on `ServiceBusAdministrationClient` now take a new keyword argument `max_message_size_in_kilobytes`.
  - `QueueProperties` and `TopicProperties` now have a new instance variable `max_message_size_in_kilobytes`.

## 7.3.4 (2021-10-06)

### Other Changes

- Updated uAMQP dependency to 1.4.3.
  - Added support for Python 3.10.
  - Fixed memory leak in win32 socketio and tlsio (issue #19777).
  - Fixed memory leak in the process of converting AMQPValue into string (issue #19777).

## 7.3.3 (2021-09-08)

### Bugs Fixed

- Improved memory usage of `ServiceBusClient` to automatically discard spawned `ServiceBusSender` or `ServiceBusReceiver` from its handler set when no strong reference to the sender or receiver exists anymore.
- Reduced CPU load of `azure.servicebus.AutoLockRenewer` during lock renewal.

## 7.3.2 (2021-08-10)

### Bugs Fixed

- Fixed a bug that `azure.servicebus.aio.AutoLockRenewer` crashes on disposal if no messages have been registered (#19642).
- Fixed a bug that `azure.servicebus.AutoLockRenewer` only supports auto lock renewal for `max_workers` amount of messages/sessions at a time (#19362).

## 7.3.1 (2021-07-07)

### Fixed

- Fixed a bug that when setting `ServiceBusMessage.partition_key`, input value should be not validated against `session_id` of None (PR #19233, thanks @bishnu-shb).
- Fixed a bug that setting `ServiceBusMessage.time_to_live` causes OverflowError error on Ubuntu 20.04.
- Fixed a bug that `AmqpAnnotatedProperties.creation_time` and `AmqpAnnotatedProperties.absolute_expiry_time` should be calculated in the unit of milliseconds instead of seconds.
- Updated uAMQP dependency to 1.4.1.
  - Fixed a bug that attributes creation_time, absolute_expiry_time and group_sequence on MessageProperties should be compatible with integer types on Python 2.7.

## 7.3.0 (2021-06-08)

**New Features**

- Support for sending AMQP annotated message which allows full access to the AMQP message fields is now GA.
  - Introduced new namespace `azure.servicebus.amqp`.
  - Introduced new classes `azure.servicebus.amqp.AmqpMessageHeader` and `azure.servicebus.amqp.AmqpMessageProperties` for accessing amqp header and properties.

**Breaking Changes from 7.2.0b1**
  - Renamed and moved `azure.servicebus.AMQPAnnotatedMessage` to `azure.servicebus.amqp.AmqpAnnotatedMessage`.
  - Renamed and moved `azure.servicebus.AMQPMessageBodyType` to `azure.servicebus.amqp.AmqpMessageBodyType`.
  - `AmqpAnnotatedMessage.header` returns `azure.servicebus.amqp.AmqpMessageHeader` instead of `uamqp.message.MessageHeader`.
  - `AmqpAnnotatedMessage.properties` returns `azure.servicebus.amqp.AmqpMessageProperties` instead of `uamqp.message.MessageProperties`.
  - `raw_amqp_message` on `ServiceBusMessage` and `ServiceBusReceivedMessage` is now a read-only property instead of an instance variable.

**Bug Fixes**

* Fixed a bug that `ServiceBusReceiver` iterator stops iteration after recovery from connection error (#18795).

## 7.2.0 (2021-05-13)

The preview features related to AMQPAnnotatedMessage introduced in 7.2.0b1 are not included in this version.

**New Features**

* Added support for using `azure.core.credentials.AzureNamedKeyCredential` as credential for authenticating the clients.
* Support for using `azure.core.credentials.AzureSasCredential` as credential for authenticating the clients is now GA.
* `ServiceBusAdministrationClient.update_*` methods now accept keyword arguments to override the properties specified in the model instance.

**Bug Fixes**

* Fixed a bug where `update_queue` and `update_subscription` methods were mutating the properties `forward_to` and `forward_dead_lettered_messages_to` of the model instance when those properties are entities instead of full paths.
* Improved the `repr` on `ServiceBusMessage` and `ServiceBusReceivedMessage` to show more meaningful text.
* Updated uAMQP dependency to 1.4.0.
  - Fixed memory leaks in the process of link attach where source and target cython objects are not properly deallocated (#15747).
  - Improved management operation callback not to parse description value of non AMQP_TYPE_STRING type as string (#18361).

**Notes**

* Updated azure-core dependency to 1.14.0.

## 7.2.0b1 (2021-04-07)

**New Features**

* Added support for using `azure.core.credentials.AzureSasCredential` as credential for authenticating the clients.
* Added support for sending AMQP annotated message which allows full access to the AMQP message fields.
  -`azure.servicebus.AMQPAnnotatedMessage` is now made public and could be instantiated for sending.
* Added new enum class `azure.servicebus.AMQPMessageBodyType` to represent the body type of the message message which includes:
  - `DATA`: The body of message consists of one or more data sections and each section contains opaque binary data.
  - `SEQUENCE`: The body of message consists of one or more sequence sections and each section contains an arbitrary number of structured data elements.
  - `VALUE`: The body of message consists of one amqp-value section and the section contains a single AMQP value.
* Added new property `body_type` on `azure.servicebus.ServiceBusMessage` and `azure.servicebus.ReceivedMessage` which returns `azure.servicebus.AMQPMessageBodyType`.

## 7.1.1 (2021-04-07)

This version and all future versions will require Python 2.7 or Python 3.6+, Python 3.5 is no longer supported.

**New Features**

* Updated `forward_to` and `forward_dead_lettered_messages_to` parameters in `create_queue`, `update_queue`, `create_subscription`, and `update_subscription` methods on sync and async `ServiceBusAdministrationClient` to accept entities as well, rather than only full paths. In the case that an entity is passed in, it is assumed that the entity exists within the same namespace used for constructing the `ServiceBusAdministrationClient`.

**Bug Fixes**

* Updated uAMQP dependency to 1.3.0.
  - Fixed bug that sending message of large size triggering segmentation fault when the underlying socket connection is lost (#13739, #14543).
  - Fixed bug in link flow control where link credit and delivery count should be calculated based on per message instead of per transfer frame (#16934).

## 7.1.0 (2021-03-09)

This version will be the last version to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

**New Features**

* Updated the following methods so that lists and single instances of Mapping representations are accepted for corresponding strongly-typed object arguments (PR #14807, thanks @bradleydamato):
  - `update_queue`, `update_topic`, `update_subscription`, and `update_rule` on `ServiceBusAdministrationClient` accept Mapping representations of `QueueProperties`, `TopicProperties`, `SubscriptionProperties`, and `RuleProperties`, respectively.
  - `send_messages` and `schedule_messages` on both sync and async versions of `ServiceBusSender` accept a list of or single instance of Mapping representations of `ServiceBusMessage`.
  - `add_message` on `ServiceBusMessageBatch` now accepts a Mapping representation of `ServiceBusMessage`.

**BugFixes**

* Operations failing due to `uamqp.errors.LinkForceDetach` caused by no activity on the connection for 10 minutes will now be retried internally except for the session receiver case.
* `uamqp.errors.AMQPConnectionError` errors with condition code `amqp:unknown-error` are now categorized into `ServiceBusConnectionError` instead of the general `ServiceBusError`.
* The `update_*` methods on `ServiceBusManagementClient` will now raise a `TypeError` rather than an `AttributeError` in the case of unsupported input type.

## 7.0.1 (2021-01-12)

**BugFixes**

* `forward_to` and `forward_dead_lettered_messages_to` will no longer cause authorization errors when used in `ServiceBusAdministrationClient` for queues and subscriptions (#15543).
* Updated uAMQP dependency to 1.2.13.
  - Fixed bug that macOS was unable to detect network error (#15473).
  - Fixed bug that `uamqp.ReceiveClient` and `uamqp.ReceiveClientAsync` receive messages during connection establishment (#15555).
  - Fixed bug where connection establishment on macOS with Clang 12 triggering unrecognized selector exception (#15567).
  - Fixed bug in accessing message properties triggering segmentation fault when the underlying C bytes are NULL (#15568).

## 7.0.0 (2020-11-23)

> **Note:** This is the GA release of the `azure-servicebus` package, rolling out the official API surface area constructed over the prior preview releases.  Users migrating from `v0.50` are advised to view the [migration guide](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/servicebus/azure-servicebus/migration_guide.md).

**New Features**

* `sub_queue` and `receive_mode` may now be passed in as a valid string (as defined by their respective enum type) as well as their enum form when constructing `ServiceBusReceiver`.
* Added support for Distributed Tracing of send, receive, and schedule scenarios.

**Breaking Changes**

* `ServiceBusSender` and `ServiceBusReceiver` are no longer reusable and will raise `ValueError` when trying to operate on a closed handler.
* Rename `ReceiveMode` to `ServiceBusReceiveMode` and `SubQueue` to `ServiceBusSubQueue`, and convert their enum values from ints to human-readable strings.
* Rename enum values `DeadLetter` to `DEAD_LETTER`, `TransferDeadLetter` to `TRANSFER_DEAD_LETTER`, `PeekLock` to `PEEK_LOCK` and `ReceiveAndDelete` to `RECEIVE_AND_DELETE` to conform to sdk guidelines going forward.
* `send_messages`, `schedule_messages`, `cancel_scheduled_messages` and `receive_deferred_messages` now performs a no-op rather than raising a `ValueError` if provided an empty list of messages or an empty batch.
* `ServiceBusMessage.amqp_annotated_message` has been renamed to `ServiceBusMessage.raw_amqp_message` to normalize with other SDKs.
* Redesigned error hierarchy based on the service-defined error condition:
  - `MessageAlreadySettled` now inherits from `ValueError` instead of `ServiceBusMessageError` as it's a client-side validation.
  - Removed `NoActiveSession` which is now replaced by `OperationTimeoutError` as the client times out when trying to connect to any available session.
  - Removed `ServiceBusMessageError` as error condition based exceptions provide comprehensive error information.
  - Removed `MessageSettleFailed` as error condition based exceptions provide comprehensive error information.
  - Removed `MessageSendFailed` as error condition based exceptions provide comprehensive error information.
  - Renamed `MessageContentTooLarge` to `MessageSizeExceededError` to be consistent with the term defined by the service.
  - Renamed `MessageLockExpired` to `MessageLockLostError` to be consistent with the term defined by the service.
  - Renamed `SessionLockExpired` to `SessionLockLostError` to be consistent with the term defined by the service.
  - Introduced `MessageNotFoundError` which would be raised when the requested message was not found.
  - Introduced `MessagingEntityNotFoundError` which would be raised when a Service Bus resource cannot be found by the Service Bus service.
  - Introduced `MessagingEntityDisabledError` which would be raised when the Messaging Entity is disabled.
  - Introduced `MessagingEntityAlreadyExistsError` which would be raised when an entity with the same name exists under the same namespace.
  - Introduced `ServiceBusQuotaExceededError` which would be raised when a Service Bus resource has been exceeded while interacting with the Azure Service Bus service.
  - Introduced `ServiceBusServerBusyError` which would be raised when the Azure Service Bus service reports that it is busy in response to a client request to perform an operation.
  - Introduced `ServiceBusCommunicationError` which would be raised when there was a general communications error encountered when interacting with the Azure Service Bus service.
  - Introduced `SessionCannotBeLockedError` which would be raised when the requested session cannot be locked.
* Introduced new client side validation on certain use cases:
  - `ServiceBusMessage` will now raise a `TypeError` when provided an invalid body type.  Valid bodies are strings, bytes, and None.  Lists are no longer accepted, as they simply concatenated the contents prior.
  - An improper `receive_mode` value will now raise `ValueError` instead of `TypeError` in line with supporting extensible enums.
  - Setting `ServiceBusMessage.partition_key` to a value different than `session_id` on the message instance now raises `ValueError`.
  - `ServiceBusClient.get_queue/topic_sender` and `ServiceBusClient.get_queue/subscription_receiver` will now
raise `ValueError` if the `queue_name` or `topic_name` does not match the `EntityPath` in the connection string used to construct the `ServiceBusClient`.
  - Settling a message that has been peeked will raise `ValueError`.
  - Settling a message or renewing a lock on a message received in `RECEIVE_AND_DELETE` receive mode will raise `ValueError`.
  - Setting `session_id`, `reply_to_session_id`, `message_id` and `partition_key` on `ServiceBusMessage` longer than 128 characters will raise `ValueError`.
* `ServiceBusReceiver.get_streaming_message_iter` has been made internal for the time being to assess use patterns before committing to back-compatibility; messages may still be iterated over in equivalent fashion by iterating on the receiver itself.

**BugFixes**

* `ServiceBusAdministrationClient.create_rule` by default now creates a `TrueRuleFilter` rule.
* FQDNs and Connection strings are now supported even with strippable whitespace or protocol headers (e.g. 'sb://').
* Using parameter `auto_lock_renewer` on a sessionful receiver alongside `ReceiveMode.ReceiveAndDelete` will no longer fail during receipt due to failure to register the message with the renewer.

## 7.0.0b8 (2020-11-05)

**New Features**

* Added support for `timeout` parameter on the following operations:
  - `ServiceBusSender`: `send_messages`, `schedule_messages` and `cancel_scheduled_messages`
  - `ServiceBusReceiver`: `receive_deferred_messages`, `peek_messages` and `renew_message_lock`
  - `ServiceBusSession`: `get_state`, `set_state` and `renew_lock`
* `azure.servicebus.exceptions.ServiceBusError` now inherits from `azure.core.exceptions.AzureError`.
* Added a `parse_connection_string` method which parses a connection string into a properties bag containing its component parts
* Add support for `auto_lock_renewer` parameter on `get_queue_receiver` and `get_subscription_receiver` calls to allow auto-registration of messages and sessions for auto-renewal.

**Breaking Changes**

* Renamed `AutoLockRenew` to `AutoLockRenewer`.
* Removed class `ServiceBusSessionReceiver` which is now unified within class `ServiceBusReceiver`.
  - Removed methods `ServiceBusClient.get_queue_session_receiver` and `ServiceBusClient.get_subscription_session_receiver`.
  - `ServiceBusClient.get_queue_receiver` and `ServiceBusClient.get_subscription_receiver` now take keyword parameter `session_id` which must be set when getting a receiver for the sessionful entity.
* The parameter `inner_exception` that `ServiceBusError.__init__` takes is now renamed to `error`.
* Renamed `azure.servicebus.exceptions.MessageError` to `azure.servicebus.exceptions.ServiceBusMessageError`
* Removed error `azure.servicebus.exceptions.ServiceBusResourceNotFound` as `azure.core.exceptions.ResourceNotFoundError` is now raised when a Service Bus
resource does not exist when using the `ServiceBusAdministrationClient`.
* Renamed `Message` to `ServiceBusMessage`.
* Renamed `ReceivedMessage` to `ServiceBusReceivedMessage`.
* Renamed `BatchMessage` to `ServiceBusMessageBatch`.
  - Renamed method `add` to `add_message` on the class.
* Removed class `PeekedMessage`.
* Removed class `ReceivedMessage` under module `azure.servicebus.aio`.
* Renamed `ServiceBusSender.create_batch` to `ServiceBusSender.create_message_batch`.
* Exceptions `MessageSendFailed`, `MessageSettleFailed` and `MessageLockExpired`
 now inherit from `azure.servicebus.exceptions.ServiceBusMessageError`.
* `get_state` in `ServiceBusSession` now returns `bytes` instead of a `string`.
* `ServiceBusReceiver.receive_messages/get_streaming_message_iter` and
 `ServiceBusClient.get_<queue/subscription>_receiver` now raises ValueError if the given `max_wait_time` is less than or equal to 0.
* Message settlement methods are moved from `ServiceBusMessage` to `ServiceBusReceiver`:
  - Use `ServiceBusReceiver.complete_message` instead of `ServiceBusReceivedMessage.complete` to complete a message.
  - Use `ServiceBusReceiver.abandon_message` instead of `ServiceBusReceivedMessage.abandon` to abandon a message.
  - Use `ServiceBusReceiver.defer_message` instead of `ServiceBusReceivedMessage.defer` to defer a message.
  - Use `ServiceBusReceiver.dead_letter_message` instead of `ServiceBusReceivedMessage.dead_letter` to dead letter a message.
* Message settlement methods (`complete_message`, `abandon_message`, `defer_message` and `dead_letter_message`)
and methods that use amqp management link for request like `schedule_messages`, `received_deferred_messages`, etc.
now raise more concrete exception other than `MessageSettleFailed` and `ServiceBusError`.
* Message `renew_lock` method is moved from `ServiceBusMessage` to `ServiceBusReceiver`:
  - Changed `ServiceBusReceivedMessage.renew_lock` to `ServiceBusReceiver.renew_message_lock`
* `AutoLockRenewer.register` now takes `ServiceBusReceiver` as a positional parameter.
* Removed `encoding` support from `ServiceBusMessage`.
* `ServiceBusMessage.amqp_message` has been renamed to `ServiceBusMessage.amqp_annotated_message` for cross-sdk consistency.
* All `name` parameters in `ServiceBusAdministrationClient` are now precisely specified ala `queue_name` or `rule_name`
* `ServiceBusMessage.via_partition_key` is no longer exposed, this is pending a full implementation of transactions as it has no external use. If needed, the underlying value can still be accessed in `ServiceBusMessage.amqp_annotated_message.annotations`.
* `ServiceBusMessage.properties` has been renamed to `ServiceBusMessage.application_properties` for consistency with service verbiage.
* Sub-client (`ServiceBusSender` and `ServiceBusReceiver`) `from_connection_string` initializers have been made internal until needed. Clients should be initialized from root `ServiceBusClient`.
* `ServiceBusMessage.label` has been renamed to `ServiceBusMessage.subject`.
* `ServiceBusMessage.amqp_annotated_message` has had its type renamed from `AMQPMessage` to `AMQPAnnotatedMessage`
* `AutoLockRenewer` `timeout` parameter is renamed to `max_lock_renew_duration`
* Attempting to autorenew a non-renewable message, such as one received in `ReceiveAndDelete` mode, or configure auto-autorenewal on a `ReceiveAndDelete` receiver, will raise a `ValueError`.
* The default value of parameter `max_message_count` on `ServiceBusReceiver.receive_messages` is now `1` instead of `None` and will raise ValueError if the given value is less than or equal to 0.

**BugFixes**

* Updated uAMQP dependency to 1.2.12.
  - Added support for Python 3.9.
  - Fixed bug where amqp message `footer` and `delivery_annotation` were not encoded into the outgoing payload.

## 7.0.0b7 (2020-10-05)

**Breaking Changes**

* Passing any type other than `ReceiveMode` as parameter `receive_mode` now throws a `TypeError` instead of `AttributeError`.
* Administration Client calls now take only entity names, not `<Entity>Descriptions` as well to reduce ambiguity in which entity was being acted on. TypeError will now be thrown on improper parameter types (non-string).
* `AMQPMessage` (`Message.amqp_message`) properties are now read-only, changes of these properties would not be reflected in the underlying message.  This may be subject to change before GA.

## 7.0.0b6 (2020-09-10)

**New Features**

* `renew_lock()` now returns the UTC datetime that the lock is set to expire at.
* `receive_deferred_messages()` can now take a single sequence number as well as a list of sequence numbers.
* Messages can now be sent twice in succession.
* Connection strings used with `from_connection_string` methods now support using the `SharedAccessSignature` key in leiu of `sharedaccesskey` and `sharedaccesskeyname`, taking the string of the properly constructed token as value.
* Internal AMQP message properties (header, footer, annotations, properties, etc) are now exposed via `Message.amqp_message`

**Breaking Changes**

* Renamed `prefetch` to `prefetch_count`.
* Renamed `ReceiveSettleMode` enum to `ReceiveMode`, and respectively the `mode` parameter to `receive_mode`.
* `retry_total`, `retry_backoff_factor` and `retry_backoff_max` are now defined at the `ServiceBusClient` level and inherited by senders and receivers created from it.
* No longer export `NEXT_AVAILABLE` in `azure.servicebus` module.  A null `session_id` will suffice.
* Renamed parameter `message_count` to `max_message_count` as fewer messages may be present for method `peek_messages()` and `receive_messages()`.
* Renamed `PeekMessage` to `PeekedMessage`.
* Renamed `get_session_state()` and `set_session_state()` to `get_state()` and `set_state()` accordingly.
* Renamed parameter `description` to `error_description` for method `dead_letter()`.
* Renamed properties `created_time` and `modified_time` to `created_at_utc` and `modified_at_utc` within `AuthorizationRule` and `NamespaceProperties`.
* Removed parameter `requires_preprocessing` from `SqlRuleFilter` and `SqlRuleAction`.
* Removed property `namespace_type` from `NamespaceProperties`.
* Rename `ServiceBusManagementClient` to `ServiceBusAdministrationClient`
* Attempting to call `send_messages` on something not a `Message`, `BatchMessage`, or list of `Message`s, will now throw a `TypeError` instead of `ValueError`
* Sending a message twice will no longer result in a MessageAlreadySettled exception.
* `ServiceBusClient.close()` now closes spawned senders and receivers.
* Attempting to initialize a sender or receiver with a different connection string entity and specified entity (e.g. `queue_name`) will result in an AuthenticationError
* Remove `is_anonymous_accessible` from management entities.
* Remove `support_ordering` from `create_queue` and `QueueProperties`
* Remove `enable_subscription_partitioning` from `create_topic` and `TopicProperties`
* `get_dead_letter_[queue,subscription]_receiver()` has been removed.  To connect to a dead letter queue, utilize the `sub_queue` parameter of `get_[queue,subscription]_receiver()` provided with a value from the `SubQueue` enum
* No longer export `ServiceBusSharedKeyCredential`
* Rename `entity_availability_status` to `availability_status`

## 7.0.0b5 (2020-08-10)

**New Features**

* Added new properties to Message, PeekMessage and ReceivedMessage: `content_type`, `correlation_id`, `label`,
`message_id`, `reply_to`, `reply_to_session_id` and `to`. Please refer to the docstring for further information.
* Added new properties to PeekMessage and ReceivedMessage: `enqueued_sequence_number`, `dead_letter_error_description`,
`dead_letter_reason`, `dead_letter_source`, `delivery_count` and `expires_at_utc`. Please refer to the docstring for further information.
* Added support for sending received messages via `ServiceBusSender.send_messages`.
* Added `on_lock_renew_failure` as a parameter to `AutoLockRenew.register`, taking a callback for when the lock is lost non-intentially (e.g. not via settling, shutdown, or autolockrenew duration completion).
* Added new supported value types int, float, datetime and timedelta for `CorrelationFilter.properties`.
* Added new properties `parameters` and `requires_preprocessing` to `SqlRuleFilter` and `SqlRuleAction`.
* Added an explicit method to fetch the continuous receiving iterator, `get_streaming_message_iter()` such that `max_wait_time` can be specified as an override.

**Breaking Changes**

* Removed/Renamed several properties and instance variables on Message (the changes applied to the inherited Message type PeekMessage and ReceivedMessage).
  - Renamed property `user_properties` to `properties`
      - The original instance variable `properties` which represents the AMQP properties now becomes an internal instance variable `_amqp_properties`.
  - Removed property `enqueue_sequence_number`.
  - Removed property `annotations`.
  - Removed instance variable `header`.
* Removed several properties and instance variables on PeekMessage and ReceivedMessage.
  - Removed property `partition_id` on both type.
  - Removed property `settled` on both type.
  - Removed instance variable `received_timestamp_utc` on both type.
  - Removed property `settled` on `PeekMessage`.
  - Removed property `expired` on `ReceivedMessage`.
* `AutoLockRenew.sleep_time` and `AutoLockRenew.renew_period` have been made internal as `_sleep_time` and `_renew_period` respectively, as it is not expected a user will have to interact with them.
* `AutoLockRenew.shutdown` is now `AutoLockRenew.close` to normalize with other equivalent behaviors.
* Renamed `QueueDescription`, `TopicDescription`, `SubscriptionDescription` and `RuleDescription` to `QueueProperties`, `TopicProperties`, `SubscriptionProperties`, and `RuleProperties`.
* Renamed `QueueRuntimeInfo`, `TopicRuntimeInfo`, and `SubscriptionRuntimeInfo` to `QueueRuntimeProperties`, `TopicRuntimeProperties`, and `SubscriptionRuntimeProperties`.
* Removed param `queue` from `create_queue`, `topic` from `create_topic`, `subscription` from `create_subscription` and `rule` from `create_rule`
 of `ServiceBusManagementClient`. Added param `name` to them and keyword arguments for queue properties, topic properties, subscription properties and rule properties.
* Removed model class attributes related keyword arguments from `update_queue` and `update_topic` of `ServiceBusManagementClient`. This is to encourage utilizing the model class instance instead as returned from a create_\*, list_\* or get_\* operation to ensure it is properly populated.  Properties may still be modified.
* Model classes `QueueProperties`, `TopicProperties`, `SubscriptionProperties` and `RuleProperties` require all arguments to be present for creation.  This is to protect against lack of partial updates by requiring all properties to be specified.
* Renamed `idle_timeout` in `get_<queue/subscription>_receiver()` to `max_wait_time` to normalize with naming elsewhere.
* Updated uAMQP dependency to 1.2.10 such that the receiver does not shut down when generator times out, and can be received from again.

## 7.0.0b4 (2020-07-06)

**New Features**

* Added support for management of topics, subscriptions, and rules.
* `receive_messages()` (formerly `receive()`) now supports receiving a batch of messages (`max_batch_size` > 1) without the need to set `prefetch` parameter during `ServiceBusReceiver` initialization.

**BugFixes**

* Fixed bug where sync `AutoLockRenew` does not shutdown itself timely.
* Fixed bug where async `AutoLockRenew` does not support context manager.

**Breaking Changes**

* Renamed `receive()`, `peek()` `schedule()` and `send()` to `receive_messages()`, `peek_messages()`, `schedule_messages()` and `send_messages()` to align with other service bus SDKs.
* `receive_messages()` (formerly `receive()`) no longer raises a `ValueError` if `max_batch_size` is less than the `prefetch` parameter set during `ServiceBusReceiver` initialization.

## 7.0.0b3 (2020-06-08)

**New Features**

* Added support for management of queue entities.
    - Use `azure.servicebus.management.ServiceBusManagementClient` (`azure.servicebus.management.aio.ServiceBusManagementClient` for aio) to create, update, delete, list queues and get settings as well as runtime information of queues under a ServiceBus namespace.
* Added methods `get_queue_deadletter_receiver` and `get_subscription_deadletter_receiver` in `ServiceBusClient` to get a `ServiceBusReceiver` for the dead-letter sub-queue of the target entity.

**BugFixes**

* Updated uAMQP dependency to 1.2.8.
    * Fixed bug where reason and description were not being set when dead-lettering messages.

## 7.0.0b2 (2020-05-04)

**New Features**

* Added method `get_topic_sender` in `ServiceBusClient` to get a `ServiceBusSender` for a topic.
* Added method `get_subscription_receiver` in `ServiceBusClient` to get a `ServiceBusReceiver` for a subscription under specific topic.
* Added support for scheduling messages and scheduled message cancellation.
    - Use `ServiceBusSender.schedule(messages, schedule_time_utc)` for scheduling messages.
    - Use `ServiceBusSender.cancel_scheduled_messages(sequence_numbers)` for scheduled messages cancellation.
* `ServiceBusSender.send()` can now send a list of messages in one call, if they fit into a single batch.  If they do not fit a `ValueError` is thrown.
* `BatchMessage.add()` and `ServiceBusSender.send()` would raise `MessageContentTooLarge` if the content is over-sized.
* `ServiceBusReceiver.receive()` raises `ValueError` if its param `max_batch_size` is greater than param `prefetch` of `ServiceBusClient`.
* Added exception classes `MessageError`, `MessageContentTooLarge`, `ServiceBusAuthenticationError`.
   - `MessageError`: when you send a problematic message, such as an already sent message or an over-sized message.
   - `MessageContentTooLarge`: when you send an over-sized message. A subclass of `ValueError` and `MessageError`.
   - `ServiceBusAuthenticationError`: on failure to be authenticated by the service.
* Removed exception class `InvalidHandlerState`.

**BugFixes**

* Fixed bug where http_proxy and transport_type in ServiceBusClient are not propagated into Sender/Receiver creation properly.
* Updated uAMQP dependency to 1.2.7.
    * Fixed bug in setting certificate of tlsio on MacOS. #7201
    * Fixed bug that caused segmentation fault in network tracing on MacOS when setting `logging_enable` to `True` in `ServiceBusClient`.

**Breaking Changes**

* Session receivers are now created via their own top level functions, e.g. `get_queue_sesison_receiver` and `get_subscription_session_receiver`.  Non session receivers no longer take session_id as a paramter.
* `ServiceBusSender.send()` no longer takes a timeout parameter, as it should be redundant with retry options provided when creating the client.
* Exception imports have been removed from module `azure.servicebus`. Import from `azure.servicebus.exceptions` instead.
* `ServiceBusSender.schedule()` has swapped the ordering of parameters `schedule_time_utc` and `messages` for better consistency with `send()` syntax.

## 7.0.0b1 (2020-04-06)

Version 7.0.0b1 is a preview of our efforts to create a client library that is user friendly and idiomatic to the Python ecosystem. The reasons for most of the changes in this update can be found in the Azure SDK Design Guidelines for Python. For more information, please visit https://aka.ms/azure-sdk-preview1-python.
* Note: Not all historical functionality exists in this version at this point.  Topics, Subscriptions, scheduling, dead_letter management and more will be added incrementally over upcoming preview releases.

**New Features**

* Added new configuration parameters when creating `ServiceBusClient`.
    * `credential`: The credential object used for authentication which implements `TokenCredential` interface of getting tokens.
    * `http_proxy`: A dictionary populated with proxy settings.
    * For detailed information about configuration parameters, please see docstring in `ServiceBusClient` and/or the reference documentation for more information.
* Added support for authentication using Azure Identity credentials.
* Added support for retry policy.
* Added support for http proxy.
* Manually calling `reconnect` should no longer be necessary, it is now performed implicitly.
* Manually calling `open` should no longer be necessary, it is now performed implicitly.
    * Note: `close()`-ing is still required if a context manager is not used, to avoid leaking connections.
* Added support for sending a batch of messages destined for heterogenous sessions.

**Breaking changes**

* Simplified API and set of clients
    * `get_queue` no longer exists, utilize `get_queue_sender/receiver` instead.
    * `peek` and other `queue_client` functions have moved to their respective sender/receiver.
    * Renamed `fetch_next` to `receive`.
    * Renamed `session` to `session_id` to normalize naming when requesting a receiver against a given session.
    * `reconnect` no longer exists, and is performed implicitly if needed.
    * `open` no longer exists, and is performed implicitly if needed.
* Normalized top level client parameters with idiomatic and consistent naming.
    * Renamed `debug` in `ServiceBusClient` initializer to `logging_enable`.
    * Renamed `service_namespace` in `ServiceBusClient` initializer to `fully_qualified_namespace`.
* New error hierarchy, with more specific semantics
    * `azure.servicebus.exceptions.ServiceBusError`
    * `azure.servicebus.exceptions.ServiceBusConnectionError`
    * `azure.servicebus.exceptions.ServiceBusResourceNotFound`
    * `azure.servicebus.exceptions.ServiceBusAuthorizationError`
    * `azure.servicebus.exceptions.NoActiveSession`
    * `azure.servicebus.exceptions.OperationTimeoutError`
    * `azure.servicebus.exceptions.InvalidHandlerState`
    * `azure.servicebus.exceptions.AutoLockRenewTimeout`
    * `azure.servicebus.exceptions.AutoLockRenewFailed`
    * `azure.servicebus.exceptions.EventDataSendError`
    * `azure.servicebus.exceptions.MessageSendFailed`
    * `azure.servicebus.exceptions.MessageLockExpired`
    * `azure.servicebus.exceptions.MessageSettleFailed`
    * `azure.servicebus.exceptions.MessageAlreadySettled`
    * `azure.servicebus.exceptions.SessionLockExpired`
* BatchMessage creation is now initiated via `create_batch` on a Sender, using `add()` on the batch to add messages, in order to enforce service-side max batch sized limitations.
* Session is now set on the message itself, via `session_id` parameter or property, as opposed to on `Send` or `get_sender` via `session`.  This is to allow sending a batch of messages destined to varied sessions.
* Session management is now encapsulated within a property of a receiver, e.g. `receiver.session`, to better compartmentalize functionality specific to sessions.
    * To use `AutoLockRenew` against sessions, one would simply pass the inner session object, instead of the receiver itself.

## 0.50.2 (2019-12-09)

**New Features**

* Added support for delivery tag lock tokens

**BugFixes**

* Fixed bug where Message would pass through invalid kwargs on init when attempting to thread through subject.
* Increments UAMQP dependency min version to 1.2.5, to include a set of fixes, including handling of large messages and mitigation of segfaults.

## 0.50.1 (2019-06-24)

**BugFixes**

* Fixed bug where enqueued_time and scheduled_enqueue_time of message being parsed as local timestamp rather than UTC.


## 0.50.0 (2019-01-17)

**Breaking changes**

* Introduces new AMQP-based API.
* Original HTTP-based API still available under new namespace: azure.servicebus.control_client
* For full API changes, please see updated [reference documentation](https://docs.microsoft.com/python/api/azure-servicebus/azure.servicebus?view=azure-python).

Within the new namespace, the original HTTP-based API from version 0.21.1 remains unchanged (i.e. no additional features or bugfixes)
so for those intending to only use HTTP operations - there is no additional benefit in updating at this time.

**New Features**

* New API supports message send and receive via AMQP with improved performance and stability.
* New asynchronous APIs (using `asyncio`) for send, receive and message handling.
* Support for message and session auto lock renewal via background thread or async operation.
* Now supports scheduled message cancellation.


## 0.21.1 (2017-04-27)

This wheel package is now built with the azure wheel extension

## 0.21.0 (2017-01-13)

**New Features**

* `str` messages are now accepted in Python 3 and will be encoded in 'utf-8' (will not raise TypeError anymore)
* `broker_properties` can now be defined as a dict, and not only a JSON `str`. datetime, int, float and boolean are converted.
* #902 add `send_topic_message_batch` operation (takes an iterable of messages)
* #902 add `send_queue_message_batch` operation (takes an iterable of messages)

**Bugfixes**

* #820 the code is now more robust to unexpected changes on the SB RestAPI

## 0.20.3 (2016-08-11)

**News**

* #547 Add get dead letter path static methods to Python
* #513 Add renew lock

**Bugfixes**

* #628 Fix custom properties with double quotes

## 0.20.2 (2016-06-28)

**Bugfixes**

* New header in Rest API which breaks the SDK #658 #657

## 0.20.1 (2015-09-14)

**News**

* Create a requests.Session() if the user doesn't pass one in.

## 0.20.0 (2015-08-31)

Initial release of this package, from the split of the `azure` package.
See the `azure` package release note for 1.0.0 for details and previous
history on Service Bus.
