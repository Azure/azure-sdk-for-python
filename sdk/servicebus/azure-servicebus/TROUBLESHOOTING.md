# Troubleshoot Azure Service Bus client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Service Bus client library for Python.

## Table of contents

* [General troubleshooting](#general-troubleshooting)
  * [Enable client logging](#enable-client-logging)
  * [Common exceptions](#common-exceptions)
  * [Timeouts](#timeouts)
* [Troubleshooting authentication issues](#troubleshooting-authentication-issues)
  * [Authentication errors](#authentication-errors)
  * [Authorization errors](#authorization-errors)
  * [Connection string issues](#connection-string-issues)
* [Troubleshooting connectivity issues](#troubleshooting-connectivity-issues)
  * [Connection errors](#connection-errors)
  * [Firewall and proxy issues](#firewall-and-proxy-issues)
  * [Service busy errors](#service-busy-errors)
* [Troubleshooting message handling issues](#troubleshooting-message-handling-issues)
  * [Message lock issues](#message-lock-issues)
  * [Message size issues](#message-size-issues)
  * [Message settlement issues](#message-settlement-issues)
  * [Dead letter queue issues](#dead-letter-queue-issues)
* [Troubleshooting session handling issues](#troubleshooting-session-handling-issues)
  * [Session lock issues](#session-lock-issues)
  * [Session cannot be locked](#session-cannot-be-locked)
* [Troubleshooting sender issues](#troubleshooting-sender-issues)

  * [Batch fails to send](#batch-fails-to-send)

* [Troubleshooting receiver issues](#troubleshooting-receiver-issues)

  * [Message completion behavior](#message-completion-behavior)
  * [Receive operation hangs](#receive-operation-hangs)
  * [Messages not being received](#messages-not-being-received)
* [Troubleshooting quota and capacity issues](#troubleshooting-quota-and-capacity-issues)
  * [Quota exceeded errors](#quota-exceeded-errors)
  * [Entity not found errors](#entity-not-found-errors)

* [Get additional help](#get-additional-help)

## General troubleshooting

Azure Service Bus client library will raise exceptions defined in [Azure Core](https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions) and [azure.servicebus.exceptions](https://docs.microsoft.com/python/api/azure-servicebus/azure.servicebus.exceptions).

### Enable client logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted** headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

To enable client logging and AMQP frame level trace:

```python
import logging
import sys

handler = logging.StreamHandler(stream=sys.stdout)
log_fmt = logging.Formatter(fmt="%(asctime)s | %(threadName)s | %(levelname)s | %(name)s | %(message)s")
handler.setFormatter(log_fmt)
logger = logging.getLogger('azure.servicebus')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

# Enable AMQP frame level trace
from azure.servicebus import ServiceBusClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = ServiceBusClient(fully_qualified_namespace, credential, logging_enable=True)
```

See full Python SDK logging documentation with examples [here](https://learn.microsoft.com/azure/developer/python/azure-sdk-logging).

### Common exceptions

The Service Bus APIs generate the following exceptions in `azure.servicebus.exceptions`:

#### Connection and Authentication Exceptions

- **ServiceBusConnectionError:** An error occurred in the connection to the service. This may have been caused by a transient network issue or service problem. It is recommended to retry.

- **ServiceBusAuthenticationError:** An error occurred when authenticating the connection to the service. This may have been caused by the credentials being incorrect. It is recommended to check the credentials.

- **ServiceBusAuthorizationError:** An error occurred when authorizing the connection to the service. This may have been caused by the credentials not having the right permission to perform the operation. It is recommended to check the permission of the credentials.

#### Operation and Timeout Exceptions

- **OperationTimeoutError:** This indicates that the service did not respond to an operation within the expected amount of time. This may have been caused by a transient network issue or service problem. The service may or may not have successfully completed the request; the status is not known. It is recommended to attempt to verify the current state and retry if necessary.

- **ServiceBusCommunicationError:** Client isn't able to establish a connection to Service Bus. Make sure the supplied host name is correct and the host is reachable. If your code runs in an environment with a firewall/proxy, ensure that the traffic to the Service Bus domain/IP address and ports isn't blocked.

#### Message Handling Exceptions

- **MessageSizeExceededError:** This indicates that the message content is larger than the service bus frame size. This could happen when too many service bus messages are sent in a batch or the content passed into the body of a `Message` is too large. It is recommended to reduce the count of messages being sent in a batch or the size of content being passed into a single `ServiceBusMessage`.

- **MessageAlreadySettled:** This indicates failure to settle the message. This could happen when trying to settle an already-settled message.

- **MessageLockLostError:** The lock on the message has expired and it has been released back to the queue. It will need to be received again in order to settle it. You should be aware of the lock duration of a message and keep renewing the lock before expiration in case of long processing time. `AutoLockRenewer` could help on keeping the lock of the message automatically renewed.

- **MessageNotFoundError:** Attempt to receive a message with a particular sequence number. This message isn't found. Make sure the message hasn't been received already. Check the deadletter queue to see if the message has been deadlettered.

#### Session Handling Exceptions

- **SessionLockLostError:** The lock on the session has expired. All unsettled messages that have been received can no longer be settled. It is recommended to reconnect to the session if receive messages again if necessary. You should be aware of the lock duration of a session and keep renewing the lock before expiration in case of long processing time. `AutoLockRenewer` could help on keeping the lock of the session automatically renewed.

- **SessionCannotBeLockedError:** Attempt to connect to a session with a specific session ID, but the session is currently locked by another client. Make sure the session is unlocked by other clients.

#### Service and Entity Exceptions

- **ServiceBusQuotaExceededError:** The messaging entity has reached its maximum allowable size, or the maximum number of connections to a namespace has been exceeded. Create space in the entity by receiving messages from the entity or its subqueues.

- **ServiceBusServerBusyError:** Service isn't able to process the request at this time. Client can wait for a period of time, then retry the operation.

- **MessagingEntityNotFoundError:** Entity associated with the operation doesn't exist or it has been deleted. Please make sure the entity exists.

- **MessagingEntityDisabledError:** Request for a runtime operation on a disabled entity. Please activate the entity.

#### Auto Lock Renewal Exceptions

- **AutoLockRenewFailed:** An attempt to renew a lock on a message or session in the background has failed. This could happen when the receiver used by `AutoLockRenewer` is closed or the lock of the renewable has expired. It is recommended to re-register the renewable message or session by receiving the message or connect to the sessionful entity again.

- **AutoLockRenewTimeout:** The time allocated to renew the message or session lock has elapsed. You could re-register the object that wants be auto lock renewed or extend the timeout in advance.



### Timeouts

There are various timeouts a user should be aware of within the library:

- **10 minute service side link closure:** A link, once opened, will be closed after 10 minutes idle to protect the service against resource leakage. This should largely be transparent to a user, but if you notice a reconnect occurring after such a duration, this is why. Performing any operations, including management operations, on the link will extend this timeout.

- **max_wait_time:** Provided on creation of a receiver or when calling `receive_messages()`, the time after which receiving messages will halt after no traffic. This applies both to the imperative `receive_messages()` function as well as the length a generator-style receive will run for before exiting if there are no messages. Passing None (default) will wait forever, up until the 10 minute threshold if no other action is taken.

> **NOTE:** If processing of a message or session is sufficiently long as to cause timeouts, as an alternative to calling `receiver.renew_message_lock`/`receiver.session.renew_lock` manually, one can leverage the `AutoLockRenewer` functionality.

## Troubleshooting authentication issues

### Authentication errors

Authentication errors typically occur when the credentials provided are incorrect or have expired.

**Common causes:**
- Incorrect connection string
- Expired SAS token
- Invalid managed identity configuration
- Wrong credential type being used

**Resolution:**
1. Verify your connection string is correct and complete
2. Check if using SAS tokens that they haven't expired
3. For managed identity, ensure the identity is properly configured and has the necessary permissions
4. Test connectivity using a simple connection string first

```python
# Example of proper authentication
from azure.servicebus import ServiceBusClient

# Using connection string
client = ServiceBusClient.from_connection_string("your_connection_string")

# Using Azure Identity
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
client = ServiceBusClient("your_namespace.servicebus.windows.net", credential)
```

### Authorization errors

Authorization errors occur when the authenticated identity doesn't have sufficient permissions.

**Required permissions for Service Bus operations:**
- **Send:** Required to send messages to queues/topics
- **Listen:** Required to receive messages from queues/subscriptions  
- **Manage:** Required for management operations (create/delete entities)

**Resolution:**
1. Check the Access Control (IAM) settings in Azure portal
2. Ensure the identity has the appropriate Service Bus roles:
   - `Azure Service Bus Data Owner`
   - `Azure Service Bus Data Sender`
   - `Azure Service Bus Data Receiver`
3. For connection strings, verify the SAS policy has the correct permissions

### Connection string issues

**Common connection string problems:**
- Missing required components (Endpoint, SharedAccessKeyName, SharedAccessKey)
- Incorrect namespace or entity names
- URL encoding issues with special characters

**Example of correct connection string format:**
```
Endpoint=sb://your-namespace.servicebus.windows.net/;SharedAccessKeyName=your-policy;SharedAccessKey=your-key
```

## Troubleshooting connectivity issues

### Connection errors

Connection errors can occur due to network issues, firewall restrictions, or service problems.

**Common causes:**
- Network connectivity issues
- DNS resolution problems
- Firewall or proxy blocking connections
- Service Bus namespace not accessible from current location

**Resolution:**
1. Test basic network connectivity to `your-namespace.servicebus.windows.net` on port 5671 (AMQP) or 443 (AMQP over WebSockets)
2. Try using AMQP over WebSockets if regular AMQP is blocked:

```python
from azure.servicebus import ServiceBusClient, TransportType
from azure.identity import DefaultAzureCredential

# Using Azure Identity with WebSockets
credential = DefaultAzureCredential()
client = ServiceBusClient(
    "your_namespace.servicebus.windows.net",
    credential,
    transport_type=TransportType.AmqpOverWebsocket
)
```

### Firewall and proxy issues

If your environment has strict firewall rules or requires proxy configuration:

**For firewall:**
- Allow outbound connections to `*.servicebus.windows.net` on ports 5671-5672 (AMQP) and 443 (HTTPS/WebSockets)
- Consider using AMQP over WebSockets (port 443) if AMQP ports are blocked

**For proxy:**
- Service Bus supports HTTP CONNECT proxy for AMQP over WebSockets
- Configure proxy settings in your environment variables or application

### Service busy errors

`ServiceBusServerBusyError` indicates the service is temporarily overloaded.

**Resolution:**
1. Implement exponential backoff retry logic
2. Reduce the frequency of requests
3. Consider scaling up your Service Bus tier if errors persist

## Troubleshooting message handling issues

### Message lock issues

Messages in Service Bus have a lock duration during which they must be settled (completed, abandoned, etc.).

**MessageLockLostError resolution:**
1. Process messages faster or increase lock duration
2. Use `AutoLockRenewer` for long-running processing:

```python
from azure.servicebus import AutoLockRenewer

renewer = AutoLockRenewer()
with receiver:
    received_msgs = receiver.receive_messages(max_message_count=10)
    for message in received_msgs:
        renewer.register(receiver, message, max_lock_renewal_duration=300)
        # Process message
        receiver.complete_message(message)
```

3. Handle lock lost errors gracefully by catching the exception and potentially re-receiving the message

### Message size issues

**MessageSizeExceededError resolution:**
1. Reduce message payload size
2. Use message properties and application properties for metadata instead of body
3. For batch operations, reduce the number of messages in the batch
4. Consider splitting large messages across multiple smaller messages

**Service Bus message size limits:**
- Standard tier: 256 KB per message
- Premium tier: 1 MB per message

For the most up-to-date information on Service Bus limits, refer to the [Azure Service Bus quotas and limits](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quotas) documentation.

### Message settlement issues

**MessageAlreadySettled resolution:**
1. Ensure you're not trying to settle the same message multiple times
2. Check your application logic for race conditions
3. Use try-catch blocks when settling messages

```python
try:
    receiver.complete_message(message)
except MessageAlreadySettled:
    # Message was already settled, this is expected in some scenarios
    pass
```

### Dead letter queue issues

Messages can be moved to the dead letter queue for various reasons:

**Common reasons:**
- Message TTL expired
- Max delivery count exceeded
- Message was explicitly dead lettered
- Message processing failed repeatedly

**Debugging dead letter messages:**
```python
# Receive from dead letter queue
dlq_receiver = servicebus_client.get_queue_receiver(
    queue_name="your_queue", 
    sub_queue=ServiceBusSubQueue.DEAD_LETTER
)

with dlq_receiver:
    messages = dlq_receiver.receive_messages(max_message_count=10)
    for message in messages:
        print(f"Dead letter reason: {message.dead_letter_reason}")
        print(f"Dead letter description: {message.dead_letter_error_description}")
```

## Troubleshooting session handling issues

### Session lock issues

Session-enabled entities require proper session management.

**SessionLockLostError resolution:**
1. Renew session locks before they expire
2. Use `AutoLockRenewer` for automatic session lock renewal
3. Handle session lock lost errors by reconnecting to the session

```python
from azure.servicebus import AutoLockRenewer

renewer = AutoLockRenewer()
with receiver:
    session = receiver.session
    renewer.register(receiver, session, max_lock_renewal_duration=300)
    # Process messages in session
```

### Session cannot be locked

**SessionCannotBeLockedError resolution:**
1. Ensure no other clients are already connected to the same session
2. Wait for the current session lock to expire before reconnecting
3. Use a different session ID if specific session is not required

## Troubleshooting sender issues



### Batch fails to send

**MessageSizeExceededError resolution:**
1. Reduce batch size or message payload
2. Check message size limits: Standard tier (256 KB), Premium tier (1 MB), Batch limit (1 MB regardless of tier)
3. Use message properties for metadata instead of including everything in the message body


## Troubleshooting receiver issues



### Message completion behavior

**Important limitation:** The Python AMQP implementation does not wait for dispositions from the service to acknowledge message completion operations.

**What this means:**
- `complete_message()`, `abandon_message()`, or `dead_letter_message()` return immediately
- The SDK does not wait for confirmation from Service Bus that the message was actually settled
- This can lead to scenarios where local operation succeeds but service operation fails

**Mitigation strategies:**
1. Implement idempotent message processing to handle potential redelivery
2. Use external tracking for critical operations
3. Monitor for redelivered messages (check `delivery_count` property)

### Receive operation hangs

**Resolution:**
1. Set appropriate timeouts: `max_wait_time=30` instead of None
2. For polling scenarios, use shorter timeouts with retry loops

### Messages not being received

**Common causes and resolutions:**
1. Check entity state - verify queue/subscription exists and is active
2. For subscriptions, verify message filters and subscription rules
3. Check for competing consumers on the same queue/subscription
4. Use `peek_messages()` to see if messages exist without receiving them

## Troubleshooting quota and capacity issues

### Quota exceeded errors

**ServiceBusQuotaExceededError resolution:**
1. **For message count limits:** Receive and process messages to reduce queue/subscription size
2. **For size limits:** Remove old messages or increase entity size limits
3. **For connection limits:** Close unused connections or consider scaling to Premium tier

### Entity not found errors

**MessagingEntityNotFoundError resolution:**
1. Verify the queue/topic/subscription name is spelled correctly
2. Ensure the entity exists in the Service Bus namespace
3. Check if the entity was deleted and needs to be recreated
4. Verify you're connecting to the correct namespace





## Get additional help

Additional information on ways to reach out for support can be found in the [SUPPORT.md](https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md) at the root of the repo.

### Filing GitHub issues

When filing GitHub issues for Service Bus, please include:

1. **Environment details:**
   - Python version
   - Azure Service Bus SDK version
   - Operating system

2. **Service Bus configuration:**
   - Namespace tier (Basic, Standard, Premium)
   - Entity configuration (queue, topic, subscription settings)
   - Session-enabled or not

3. **Code sample:** Minimal reproducible code sample

4. **Logs:** DEBUG level logs with transport logging enabled (see [Enable client logging](#enable-client-logging))

5. **Error details:** Complete exception stack trace and error messages

The more information provided, the faster we can help resolve your issue.

Please view the [exceptions reference docs](https://docs.microsoft.com/python/api/azure-servicebus/azure.servicebus.exceptions) for detailed descriptions of our common Exception types.
