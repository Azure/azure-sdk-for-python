# Release History

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
* For full API changes, please see updated [reference documentation](https://docs.microsoft.com/python/api/overview/azure/servicebus/client?view=azure-python).

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
