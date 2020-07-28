# Release History

## 7.0.0b5 (Unreleased)

**New Features**

* Added new properties to Message, PeekMessage and ReceivedMessage: `content_type`, `correlation_id`, `label`,
`message_id`, `reply_to`, `reply_to_session_id` and `to`. Please refer to the docstring for further information.
* Added new properties to PeekedMessaged and ReceivedMessage: `enqueued_sequence_number`, `dead_letter_error_description`,
`dead_letter_reason`, `dead_letter_source`, `delivery_count` and `expires_at_utc`. Please refer to the docstring for further information.
* Added support for sending received messages via `ServiceBusSender.send_messages`.

**Breaking Changes**

* Removed/Renamed several properties and instance variables on Message (the changes applied to the inherited Message type PeekMessage and ReceivedMessage).
  - Renamed property `user_properties` to `properties`
      - The original instance variable `properties` which represents the AMQP properties now becomes an internal instance variable `_amqp_properties`.
  - Removed property `enqueue_sequence_number`.
  - Removed property `annotations`.
  - Removed instance variable `header`.

* Removed several properties and instance variables on PeekMessage and ReceivedMessage.
  - Removed proeprty `partition_id` on both type.
  - Removed instance variable `received_timestamp_utc` on both type.
  - Removed property `settled` on `PeekMessage`.
  - Removed property `expired` on `ReceivedMessage`.

* Add `on_lock_renew_failure` as a parameter to `AutoLockRenew.register`, taking a callback for when the lock is lost non-intentially (e.g. not via settling, shutdown, or autolockrenew duration completion)

**Breaking Changes**

* `AutoLockRenew.sleep_time` and `AutoLockRenew.renew_period` have been made internal as `_sleep_time` and `_renew_period` respectively, as it is not expected a user will have to interact with them.
* `AutoLockRenew.shutdown` is now `AutoLockRenew.close` to normalize with other equivelent behaviors.

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
