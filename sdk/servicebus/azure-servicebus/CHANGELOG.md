# Release History

## 0.50.3 (2020-05-20)

> **NOTE**: Starting with the GA release of version 7.0.0 (currently in preview), this package will be deprecated.
> Users can get a head-start on transitioning by installing or upgrading via `pip install azure-servicebus --pre` and reviewing our [migration guide](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/migration_guide.md)

**Features**

* Added support for retry sending if connection gets closed due to long time inactivity.
* Added support for `message.dead_letter` accepting `reason`.

**BugFixes**

* Added associated-link-keepalive functionality to management operations such as renewing a message lock, to ensure service-side link termination does not interfere with long-duration processing.
* Fixed bug in setting `description` when dead lettering messages (issue #9242).
* Increments UAMQP dependency min version to 1.2.8, as a component of fixing the aformentioned dead letter issue.

## 0.50.2 (2019-12-9)

**Features**

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

**Features**

* New API supports message send and receive via AMQP with improved performance and stability.
* New asynchronous APIs (using `asyncio`) for send, receive and message handling.
* Support for message and session auto lock renewal via background thread or async operation.
* Now supports scheduled message cancellation.


## 0.21.1 (2017-04-27)

This wheel package is now built with the azure wheel extension

## 0.21.0 (2017-01-13)

**Features**

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
