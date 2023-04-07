# Troubleshooting Service Bus issues

This troubleshooting guide covers failure investigation techniques, common errors for the credential types in the Azure Service Bus Python client library, and mitigation steps to resolve these errors.

## Table of contents
- [Handle Service Bus Exceptions](#handle-service-bus-exceptions)
  - [Find information about a ServiceBusException](#find-information-about-a-servicebusexception)
  - [Other common exceptions](#other-common-exceptions)
- [Permissions Issues](#permissions-issues)
- [Connectivity issues](#connectivity-issues)
  - [Timeout when connecting to service](#timeout-when-connecting-to-service)
  - [SSL handshake failures](#ssl-handshake-failures)
  - [Socket exhaustion errors](#socket-exhaustion-errors)
  - [Adding components to the connection string does not work](#adding-components-to-the-connection-string-does-not-work)
    - ["Authentication=Managed Identity" Alternative](#authenticationmanaged-identity-alternative)
- [Logging and Diagnostics](#logging-and-diagnostics)
  - [Enable logging](#enable-logging)
- [Troubleshoot sender issues](#troubleshoot-sender-issues)
  - [Cannot set multiple partition keys (or multiple sessions when partitions are enabled) for messages in ServiceBusMessageBatch](#cannot-send-batch-with-multiple-partition-keys)
  - [Batch fails to send](#batch-fails-to-send)
- [Troubleshoot receiver issues](#troubleshoot-receiver-issues)
  - [Number of messages returned doesn't match number requested in batch receive](#number-of-messages-returned-does-not-match-number-requested-in-batch-receive)
  - [Message or session lock is lost before lock expiration time](#message-or-session-lock-is-lost-before-lock-expiration-time)
  - [How to browse scheduled or deferred messages](#how-to-browse-scheduled-or-deferred-messages)
  - [How to browse session messages across all sessions](#how-to-browse-session-messages-across-all-sessions)
  - [Autolock renewal does not appear to be working](#autolock-renewal-is-not-working)
- [Quotas](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-quotas)

## Handle Service Bus Exceptions
All Service Bus exceptions are wrapped in an [ServiceBusError][ServiceBusError]. They often have an underlying AMQP error code which specifies whether an error should be retried. For retryable errors (ie. amqp:connection:forced or amqp:link:detach-forced), the client libraries will attempt to recover from these errors based on the retry options specified when instantiating the client. To configure retry options, look at the [Client Definition][ClientDefinition]. If the error is non-retryable, there is some configuration issue that needs to be resolved.


### Find information about a ServiceBusError

An [ServiceBusError][ServiceBusError] contains three fields which describe the error:

* **message**: The underlying AMQP error message. A description of the errors can be found in the [Exceptions module][ExceptionModule] or the [OASIS AMQP 1.0 spec][AmqpSpec].
* **error**: The error condition if available.
* **details**: The error details, if included in the service response.

By default the producer and consumer clients will retry for error conditions. We recommend that users of the clients use the following keyword arguments during creation of the client to change the retry behavior rather than retrying on their own:
* **retry_total**: The total number of attempts to redo a failed operation when an error occurs. Default
     value is 3
* **retry_backoff_factor**: A backoff factor to apply between attempts after the second try
* **retry_backoff_max**: The maximum back off time. Default value is 120 seconds
* **retry_mode**: The delay behavior between retry attempts. Supported values are 'fixed' or 'exponential', where default is 'exponential'

### Other common exceptions

The Service Bus APIs generate the following exceptions in azure.servicebus.exceptions:

- **ServiceBusConnectionError:** An error occurred in the connection to the service.
This may have been caused by a transient network issue or service problem. It is recommended to retry.
- **ServiceBusAuthorizationError:** An error occurred when authorizing the connection to the service.
This may have been caused by the credentials not having the right permission to perform the operation.
It is recommended to check the permission of the credentials.
- **ServiceBusAuthenticationError:** An error occurred when authenticate the connection to the service.
This may have been caused by the credentials being incorrect. It is recommended to check the credentials.
- **OperationTimeoutError:** This indicates that the service did not respond to an operation within the expected amount of time.
This may have been caused by a transient network issue or service problem. The service may or may not have successfully completed the request; the status is not known.
It is recommended to attempt to verify the current state and retry if necessary.
- **MessageSizeExceededError:** This indicate that the message content is larger than the service bus frame size.
This could happen when too many service bus messages are sent in a batch or the content passed into
the body of a `Message` is too large. It is recommended to reduce the count of messages being sent in a batch or the size of content being passed into a single `ServiceBusMessage`.
- **MessageAlreadySettled:** This indicates failure to settle the message.
This could happen when trying to settle an already-settled message.
- **MessageLockLostError:** The lock on the message has expired and it has been released back to the queue.
It will need to be received again in order to settle it.
You should be aware of the lock duration of a message and keep renewing the lock before expiration in case of long processing time.
`AutoLockRenewer` could help on keeping the lock of the message automatically renewed.
- **SessionLockLostError:** The lock on the session has expired.
All unsettled messages that have been received can no longer be settled.
It is recommended to reconnect to the session if receive messages again if necessary.
You should be aware of the lock duration of a session and keep renewing the lock before expiration in case of long processing time.
`AutoLockRenewer` could help on keeping the lock of the session automatically renewed.
- **MessageNotFoundError:** Attempt to receive a message with a particular sequence number. This message isn't found.
Make sure the message hasn't been received already. Check the deadletter queue to see if the message has been deadlettered.
- **MessagingEntityNotFoundError:** Entity associated with the operation doesn't exist or it has been deleted.
Please make sure the entity exists.
- **MessagingEntityDisabledError:** Request for a runtime operation on a disabled entity. Please Activate the entity.
- **ServiceBusQuotaExceededError:** The messaging entity has reached its maximum allowable size, or the maximum number of connections to a namespace has been exceeded.
Create space in the entity by receiving messages from the entity or its subqueues.
- **ServiceBusServerBusyError:** Service isn't able to process the request at this time. Client can wait for a period of time, then retry the operation.
- **ServiceBusCommunicationError:** Client isn't able to establish a connection to Service Bus.
Make sure the supplied host name is correct and the host is reachable.
If your code runs in an environment with a firewall/proxy, ensure that the traffic to the Service Bus domain/IP address and ports isn't blocked.
- **SessionCannotBeLockedError:** Attempt to connect to a session with a specific session ID, but the session is currently locked by another client.
Make sure the session is unlocked by other clients.
- **AutoLockRenewFailed:** An attempt to renew a lock on a message or session in the background has failed.
This could happen when the receiver used by `AutoLockRenerer` is closed or the lock of the renewable has expired.
It is recommended to re-register the renewable message or session by receiving the message or connect to the sessionful entity again.
- **AutoLockRenewTimeout:** The time allocated to renew the message or session lock has elapsed. You could re-register the object that wants be auto lock renewed or extend the timeout in advance.
- **ServiceBusError:** All other Service Bus related errors. It is the root error class of all the errors described above.

Please view the [exceptions reference docs][exception_reference] for detailed descriptions of our common Exception types.

## Connectivity issues

### Timeout when connecting to service

Depending on the host environment and network, this may present to applications as either a `ServiceBusConnectionError`, `OperationTimeoutError`, or a `ServiceBusError` and most often occurs when the client cannot find a network path to the service.

To troubleshoot:

- Verify that the connection string or fully qualified domain name specified when creating the client is correct. For information on how to acquire a connection string, see: [Get a Service Bus connection string][GetConnectionString].

- Check the firewall and port permissions in your hosting environment and that the AMQP ports 5671 and 5672 are open and that the endpoint is allowed through the firewall.

- See if your network is blocking specific IP addresses. For details, see: [What IP addresses do I need to allow?][ServiceBusIPAddresses].

- If applicable, verify the proxy configuration. For details, see: [Configuring the transport][ProxySample].

- For more information about troubleshooting network connectivity, see: [Troubleshooting guide for Azure Service Bus][TroubleshootingGuide].

### SSL handshake failures

This error can occur when an intercepting proxy is used. To verify, it is recommended that the application be tested in the host environment with the proxy disabled.

### Socket exhaustion errors

Applications should prefer treating the Service Bus types as singletons, creating and using a single instance through the lifetime of the application. This is important as each client type manages its connection; creating a new Service Bus client results in a new AMQP connection, which uses a socket. Additionally, it is essential to be aware that your client is responsible for calling close() when it is finished using a client or to use the with statement for clients so that they are automatically closed after the flow execution leaves that block.

### Adding components to the connection string does not work

The current generation of the Service Bus client library supports connection strings only in the form published by the Azure portal. These are intended to provide basic location and shared key information only; configuring behavior of the clients is done through its options.

Previous generations of the Service Bus clients allowed for some behavior to be configured by adding key/value components to a connection string. These components are no longer recognized and have no effect on client behavior.

#### "Authentication=Managed Identity" Alternative

To authenticate with Managed Identity, see: [Identity and Shared Access Credentials][IdentitySample].

For more information about the `azure.identity` library, see: [Authentication and the Azure SDK][AuthenticationAndTheAzureSDK].

## Logging and diagnostics

The Azure SDK for Python offers a consistent logging story to help troubleshoot application errors and expedite their resolution.  The logs produced will capture the flow of an application before reaching the terminal state to help locate the root issue.

This library uses the standard [Logging] library for logging

- Enable `azure.servicebus` logger to collect traces from the library.

### Enable AMQP transport logging

If enabling client logging is not enough to diagnose your issues. You can enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

For more information, see: [Logging with the Azure SDK for Python][Logging].

## Troubleshoot sender issues

### Cannot send batch with multiple partition keys

When sending to a partition-enabled entity, all messages included in a single send operation must have the same `partition_key`. If your entity is session-enabled, the same requirement holds true for the `session_id` property. In order to send messages with different `partition_key` or `session_id` values, group the messages in separate [ServiceBusMessageBatch][ServiceBusMessageBatch] instances or include them in separate calls to the [send_messages][SendMessages] overload that takes a set of [ServiceBusMessage] instances.

### Batch fails to send

We define a message batch as either [ServiceBusMessageBatch][ServiceBusMessageBatch] containing 2 or more messages, or a call to [send_messages][SendMessages] where 2 or more messages are passed in. The service does not allow a message batch to exceed 1MB. This is true whether or not the [Premium large message support][LargeMessageSupport] feature is enabled. If you intend to send a message greater than 1MB, it must be sent individually rather than grouped with other messages. Unfortunately, the [ServiceBusMessageBatch][ServiceBusMessageBatch] type does not currently support validating that a batch does not contain any messages greater than 1MB as the size is constrained by the service and may change. So if you intend to use the premium large message support feature, you will need to ensure you send messages over 1MB individually. See this [GitHub discussion][GitHubDiscussionOnBatching] for more info.

## Troubleshoot receiver issues

### Number of messages returned does not match number requested in batch receive

When attempting to do a batch receive, i.e. passing a `max_message_count` value of 2 or greater to the [receive_messages][ReceiveMessages] method, you are not guaranteed to receive the number of messages requested, even if the queue or subscription has that many messages available at that time, and even if the entire configured `max_wait_time` has not yet elapsed. To maximize throughput and avoid lock expiration, once the first message comes over the wire, the receiver will wait an additional 20ms for any additional messages before dispatching the messages for processing.  The `max_wait_time` controls how long the receiver will wait to receive the *first* message - subsequent messages will be waited for 20ms. Therefore, your application should not assume that all messages available will be received in one call.

### Message or session lock is lost before lock expiration time

The Service Bus service leverages the AMQP protocol, which is stateful. Due to the nature of the protocol, if the link that connects the client and the service is detached after a message is received, but before the message is settled, the message is not able to be settled on reconnecting the link. Links can be detached due to a short-term transient network failure, a network outage, or due to the service enforced 10-minute idle timeout. The reconnection of the link happens automatically as a part of any operation that requires the link, i.e. settling or receiving messages. Because of this, you may encounter `ServiceBusError`  or `SessionLockLostError` even if the lock expiration time has not yet passed. 

### How to browse scheduled or deferred messages

Scheduled and deferred messages are included when peeking messages. They can be identified by the [ServiceBusReceivedMessage.state] property. Once you have the [sequence_number][SequenceNumber] of a deferred message, you can receive it with a lock via the [receive_deferred_messages][ReceiveDeferredMessages] method.

When working with topics, you cannot peek scheduled messages on the subscription, as the messages remain in the topic until the scheduled enqueue time. As a workaround, you can construct a [ServiceBusReceiver][ServiceBusReceiver] passing in the topic name in order to peek such messages. Note that no other operations with the receiver will work when using a topic name.

### How to browse session messages across all sessions

You can use a regular [ServiceBusReceiver][ServiceBusReceiver] to peek across all sessions. To peek for a specific session you can use the [ServiceBusSessionReceiver][ServiceBusSessionReceiver], but you will need to obtain a session lock.

## Troubleshoot receiver issues

### Autolock renewal is not working

Autolock renewal relies on the system time to determine when to renew a lock for a message or session. If your system time is not accurate, e.g. your clock is slow, then lock renewal may not happen before the lock is lost. Ensure that your system time is accurate if autolock renewal is not working.

## Quotas

Information about Service Bus quotas can be found [here][ServiceBusQuotas].

[ServiceBusError]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.exceptions.servicebuserror?view=azure-python
[ClientDefinition]: https://learn.microsoft.com/en-us/python/api/azure-servicebus/azure.servicebus.servicebusclient?view=azure-python
[exception_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#module-azure.servicebus.exceptions
[ServiceBusQuotas]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-quotas
[ProxySample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/servicebus/azure-servicebus/samples/sync_samples/proxy.py
[AmqpSpec]: https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-types-v1.0-os.html
[GetConnectionString]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-quickstart-portal#get-the-connection-string
[AuthorizeSAS]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-sas
[RBAC]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-managed-service-identity
[TroubleshootingGuide]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-troubleshooting-guide
[ServiceBusIPAddresses]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-faq#what-ip-addresses-do-i-need-to-add-to-allowlist-
[ServiceBusReceiver]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebusreceiver?view=azure-python
[ServiceBusSender]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebussender?view=azure-python
[ServiceBusMessageBatch]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebusmessagebatch?view=azure-python
[ServiceBusMessage]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebusreceivedmessage?view=azure-python
[SendMessages]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebussender?view=azure-python#azure-servicebus-servicebussender-send-messages
[ReceiveMessages]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebusreceiver?view=azure-python#azure-servicebus-servicebusreceiver-receive-messages
[ReceiveDeferredMessages]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebusreceiver?view=azure-python#azure-servicebus-servicebusreceiver-receive-deferred-messages
[SequenceNumber]: https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.servicebusreceivedmessage?view=azure-python#azure-servicebus-servicebusreceivedmessage-sequence-number
[Logging]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[CrossEntityTransactions]: https://github.com/Azure/azure-sdk-for-net/blob/main/sdk/servicebus/Azure.Messaging.ServiceBus/samples/Sample06_Transactions.md#transactions-across-entities
[LargeMessageSupport]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-premium-messaging#large-messages-support
[GitHubDiscussionOnBatching]: https://github.com/Azure/azure-sdk-for-net/issues/25381#issuecomment-1227917960
[BackgroundService]: https://docs.microsoft.com/dotnet/api/microsoft.extensions.hosting.backgroundservice?view=dotnet
[AuthenticationAndTheAzureSDK]: https://devblogs.microsoft.com/azure-sdk/authentication-and-the-azure-sdk
[IdentitySample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/servicebus/azure-servicebus/samples/sync_samples/client_identity_authentication.py
[Throttling]: https://learn.microsoft.com/azure/service-bus-messaging/service-bus-throttling