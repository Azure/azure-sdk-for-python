# Troubleshoot Azure Service Bus client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Service Bus client library for Python.

## Table of contents

* [General troubleshooting](#general-troubleshooting)
  * [Enable client logging](#enable-client-logging)
  * [Common exceptions](#common-exceptions)
    * [Authentication exceptions](#authentication-exceptions)
    * [Connection and timeout exceptions](#connection-and-timeout-exceptions)
    * [Message and session handling exceptions](#message-and-session-handling-exceptions)
    * [Service and entity exceptions](#service-and-entity-exceptions)
    * [Auto lock renewal exceptions](#auto-lock-renewal-exceptions)
* [Threading and concurrency issues](#threading-and-concurrency-issues)
  * [Thread safety limitations](#thread-safety-limitations)
* [Troubleshooting authentication and authorization issues](#troubleshooting-authentication-and-authorization-issues)
* [Troubleshooting connectivity issues](#troubleshooting-connectivity-issues)
  * [Timeout when connecting to service](#timeout-when-connecting-to-service)
  * [SSL handshake failures](#ssl-handshake-failures)
  * [Specifying AMQP over websockets](#specifying-amqp-over-websockets)
  * [Using Service Bus with Azure Identity](#using-service-bus-with-azure-identity)
  * [Entity not found errors](#entity-not-found-errors)
* [Troubleshooting message handling issues](#troubleshooting-message-handling-issues)
  * [Message and session lock issues](#message-and-session-lock-issues)
  * [Message size issues](#message-size-issues)
* [Troubleshooting receiver issues](#troubleshooting-receiver-issues)
  * [Number of messages returned doesn't match number requested](#number-of-messages-returned-doesnt-match-number-requested)
  * [Mixing sync and async code](#mixing-sync-and-async-code)
  * [Dead letter queue issues](#dead-letter-queue-issues)
* [Get additional help](#get-additional-help)
  * [Filing GitHub issues](#filing-github-issues)

## General troubleshooting

Azure Service Bus client library will raise exceptions defined in [azure.core](https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions) and [azure.servicebus.exceptions](https://docs.microsoft.com/python/api/azure-servicebus/azure.servicebus.exceptions).

### Enable client logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.

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

The Service Bus client library will surface exceptions when an error is encountered by a service operation or within the client. For scenarios specific to Service Bus, a [ServiceBusError](https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.exceptions.servicebuserror?view=azure-python) will be raised; this is the most common exception type that applications will encounter.

ServiceBusErrors often have an underlying AMQP error code which specifies whether an error should be retried. For retryable errors (ie. `amqp:connection:forced` or `amqp:link:detach-forced`), the client library will attempt to recover from these errors based on the retry options specified using the following keyword arguments when instantiating the client:

* `retry_total`: The total number of attempts to redo a failed operation when an error occurs
* `retry_backoff_factor`: A backoff factor to apply between attempts after the second try
* `retry_backoff_max`: The maximum back off time
* `retry_mode`: The delay behavior between retry attempts. Supported values are 'fixed' or 'exponential'
When an exception is surfaced to the application, either all retries were applied unsuccessfully, or the exception was considered non-transient.

#### Authentication exceptions

- **ServiceBusAuthenticationError:** An error occurred when authenticating the connection to the service. This may have been caused by the credentials being incorrect. It is recommended to check the credentials.

- **ServiceBusAuthorizationError:** An error occurred when authorizing the connection to the service. This may have been caused by the credentials not having the right permission to perform the operation, or could be transient due to clock skew or service issues. The client will retry these errors automatically. If you continue to see this exception, it means all configured retries were exhausted - check the permission of the credentials and consider adjusting [retry configuration](#common-exceptions).

See the [Troubleshooting Authentication issues](#troubleshooting-authentication-issues) section to troubleshoot authentication/permission issues.

#### Connection and timeout exceptions

- **ServiceBusConnectionError:** An error occurred in the connection to the service. This may have been caused by a transient network issue or service problem. The client automatically retries these errors - if you see this exception, all configured retries were exhausted. Consider adjusting [retry configuration](#common-exceptions) rather than implementing additional retry logic.

- **OperationTimeoutError:** This indicates that the service did not respond to an operation within the expected amount of time. This may have been caused by a transient network issue or service problem. The service may or may not have successfully completed the request; the status is not known. The client automatically retries these errors - if you see this exception, all configured retries were exhausted. Consider verifying the current state and adjusting retry configuration if necessary.

- **ServiceBusCommunicationError:** Client isn't able to establish a connection to Service Bus. Make sure the supplied host name is correct and the host is reachable. If your code runs in an environment with a firewall/proxy, ensure that the traffic to the Service Bus domain/IP address and ports isn't blocked. For details on which ports need to be open, see the [Azure Service Bus FAQ: What ports do I need to open on the firewall?](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-faq#what-ports-do-i-need-to-open-on-the-firewall--). You can also try setting the [WebSockets transport type](#specifying-amqp-over-websockets) which often works around port/firewall issues.

See the [Troubleshooting Connectivity issues](#troubleshooting-connectivity-issues) section to troubleshoot connection and timeout issues. More information on AMQP errors in Azure Service Bus can be found [here](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-amqp-troubleshoot).

#### Message and session handling exceptions

- **MessageSizeExceededError:** This indicates that the max message size has been exceeded. The message size includes the body of the message, as well as any associated metadata and system overhead. The best approach for resolving this error is to reduce the number of messages being sent in a batch or the size of the body included in the message. Because size limits are subject to change, please refer to [Service Bus quotas](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quotas) for specifics.

- **MessageAlreadySettled:** This indicates failure to settle the message. This could happen when trying to settle an already-settled message.

- **MessageNotFoundError:** This occurs when attempting to receive a deferred message by sequence number for a message that either doesn't exist in the entity, or is currently locked.

- **MessageLockLostError:** Indicates that the lock on the message is lost. Callers should attempt to receive and process the message again. This exception only applies to entities that don't use sessions. This error occurs if processing takes longer than the lock duration and the message lock isn't renewed. This error can also occur when the link is detached due to a transient network issue or when the link is idle for 10 minutes, as enforced by the service. `AutoLockRenewer` could help on keeping the lock of the message automatically renewed.

- **SessionLockLostError:** The lock on the session has expired. All unsettled messages that have been received can no longer be settled. It is recommended to reconnect to the session if receive messages again if necessary. You should be aware of the lock duration of a session and keep renewing the lock before expiration in case of long processing time. `AutoLockRenewer` could help on keeping the lock of the session automatically renewed.

- **SessionCannotBeLockedError:** Attempt to connect to a session with a specific session ID, but the session is currently locked by another client. Make sure the session is unlocked by other clients.

See the [Troubleshooting message handling issues](#troubleshooting-message-handling-issues) section to troubleshoot message and session lock issues.

#### Service and entity exceptions

- **ServiceBusQuotaExceededError:** This typically indicates that there are too many active receive operations for a single entity. In order to avoid this error, reduce the number of potential concurrent receives. You can use batch receives to attempt to receive multiple messages per receive request. Please see [Service Bus quotas](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quotas) for more information.

- **ServiceBusServerBusyError:** Service isn't able to process the request at this time. Client can wait for a period of time, then retry the operation. For more information about quotas and limits, see [Service Bus quotas](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quotas).

- **MessagingEntityNotFoundError:** Entity associated with the operation doesn't exist or it has been deleted. Please make sure the entity exists.

- **MessagingEntityDisabledError:** Request for a runtime operation on a disabled entity. Please activate the entity.

#### Auto lock renewal exceptions

- **AutoLockRenewFailed:** An attempt to renew a lock on a message or session in the background has failed. This could happen when the receiver used by `AutoLockRenewer` is closed or the lock of the renewable has expired. It is recommended to re-register the renewable message or session by receiving the message or connect to the sessionful entity again.

- **AutoLockRenewTimeout:** The time allocated to renew the message or session lock has elapsed. You could re-register the object that wants be auto lock renewed or extend the timeout in advance.

See the [Troubleshooting message handling issues](#troubleshooting-message-handling-issues) to help troubleshoot `AutoLockRenewer` errors.

## Threading and concurrency issues

### Thread safety limitations

> **IMPORTANT:** We do not guarantee that the `ServiceBusClient`, `ServiceBusSender`, and `ServiceBusReceiver` are thread-safe or coroutine-safe. We do not recommend reusing these instances across threads or sharing them between coroutines.

The data model type, `ServiceBusMessageBatch` is not thread-safe or coroutine-safe. It should not be shared across threads nor used concurrently with client methods.

Using the same client instances across multiple threads or tasks without proper synchronization can lead to:

- Connection errors and unexpected exceptions
- Message corruption or loss
- Deadlocks and race conditions
- Unpredictable behavior

It is up to the running application to use these classes in a concurrency-safe manner.

For scenarios requiring concurrent sending in asyncio applications, ensure proper coroutine-safety management using mechanisms like `asyncio.Lock()`.

```python
import asyncio
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential

SERVICE_BUS_NAMESPACE = "<your-namespace>.servicebus.windows.net"
QUEUE_NAME = "<your-queue-name>"

lock = asyncio.Lock()

async def send_batch(sender_id, sender):
    async with lock:
        messages = [ServiceBusMessage(f"Message {i} from sender {sender_id}") for i in range(10)]
        await sender.send_messages(messages)
        print(f"Sender {sender_id} sent messages.")

credential = DefaultAzureCredential()
client = ServiceBusClient(fully_qualified_namespace=SERVICE_BUS_NAMESPACE, credential=credential)

async with client:
    sender = client.get_queue_sender(queue_name=QUEUE_NAME)
    async with sender:
        await asyncio.gather(*(send_batch(i, sender) for i in range(5)))
```

For scenarios requiring concurrent sending from multiple threads, ensure proper thread-safety management using mechanisms like `threading.Lock()`. 

> **NOTE:** Native async APIs should be used instead of running in a `ThreadPoolExecutor`, if possible.

```python
import threading
from concurrent.futures import ThreadPoolExecutor
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential

SERVICE_BUS_NAMESPACE = "<your-namespace>.servicebus.windows.net"
QUEUE_NAME = "<your-queue-name>"

lock = threading.Lock()

def send_batch(sender_id, sender):
    with lock:
        messages = [ServiceBusMessage(f"Message {i} from sender {sender_id}") for i in range(10)]
        sender.send_messages(messages)
        print(f"Sender {sender_id} sent messages.")

credential = DefaultAzureCredential()
client = ServiceBusClient(fully_qualified_namespace=SERVICE_BUS_NAMESPACE, credential=credential)

with client:
    sender = client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in range(5):
                executor.submit(send_batch, i, sender)
```

## Troubleshooting authentication and authorization issues

Authentication errors typically occur when the credentials provided are incorrect or have expired. Authorization errors occur when the authenticated identity doesn't have sufficient permissions.

The following verification steps are recommended, depending on the type of authorization provided when constructing the client:

- [Verify the connection string is correct](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quickstart-portal#get-the-connection-string)

- [Verify the SAS token was generated correctly](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-sas)

- [Verify the correct RBAC roles were granted](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-managed-service-identity) - Indicated by errors: `Send/Listen claim(s) are required to perform this operation.` In this case, ensure that the appropriate roles were assigned: `Azure Service Bus Data Owner`, `Azure Service Bus Data Sender`, or `Azure Service Bus Data Receiver`.

## Troubleshooting connectivity issues

### Timeout when connecting to service

Depending on the host environment and network, this may present to applications as timeout or operation exceptions. This most often occurs when the client cannot find a network path to the service.

To troubleshoot:

- Verify that the connection string or fully qualified domain name specified when creating the client is correct. For information on how to acquire a connection string, see: [Get a Service Bus connection string](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quickstart-portal#get-the-connection-string).

- Check the firewall and port permissions in your hosting environment and that the AMQP ports 5671 and 5672 are open and that the endpoint is allowed through the firewall.

- Try using the Web Socket transport option, which connects using port 443. This can be done by passing the [`transport_type=TransportType.AmqpOverWebsocket`](https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.transporttype?view=azure-python) to the client.

- See if your network is blocking specific IP addresses. For details, see: [What IP addresses do I need to allow?](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-faq#what-ip-addresses-do-i-need-to-add-to-allowlist-).

- If applicable, verify the proxy configuration. For details, see: [Proxy sample](https://github.com/Azure/azure-sdk-for-python/blob/fb9f99e09a0968e51839f8456ad69b0354837f95/sdk/servicebus/azure-servicebus/samples/sync_samples/proxy.py).

### SSL handshake failures

This error can occur when an intercepting proxy is used. To verify, it is recommended that the application be tested in the host environment with the proxy disabled. Note that intercepting proxies are not a supported scenario.

### Specifying AMQP over websockets

To configure web socket use, pass the [`transport_type=TransportType.AmqpOverWebsocket`](https://learn.microsoft.com/python/api/azure-servicebus/azure.servicebus.transporttype?view=azure-python) to the `ServiceBusClient`.

### Using Service Bus with Azure Identity

To authenticate with Azure Identity, see: [Client Identity Authentication](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/servicebus/azure-servicebus/samples/sync_samples/client_identity_authentication.py).

For more information about the `azure-identity` library, see: [Azure Identity client library for Python][https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python].

### Entity not found errors

**MessagingEntityNotFoundError resolution:**
1. Verify the queue/topic/subscription name is spelled correctly
2. Ensure the Service Bus namespace and entity exist
3. Check if the entity was deleted and needs to be recreated

## Troubleshooting message handling issues

### Message and session lock issues

Messages, sessionful and non-sessionful, in Service Bus have a lock duration during which they must be settled (completed, abandoned, etc.).

**MessageLockLostError and SessionLockLostError resolution:**
1. Process messages faster or increase lock duration
2. If setting `prefetch_count` to a large number, consider setting it lower as the lock timer starts running when the message is fetched, even though not visible to the application and the client cannot extend locks for prefetched messages.
3. Use `AutoLockRenewer` for long-running processing.
    * When running the async `AutoLockRenewer`, ensure that the event loop is not blocked during message processing. (e.g. `time.sleep(60)` --> `await asyncio.sleep(60)`). Otherwise, the `AutoLockRenewer` will be prevented from running in the background.

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

### Message size issues

**MessageSizeExceededError resolution:**
1. Reduce message payload size.
2. Consider splitting large messages across multiple smaller messages. For the most up-to-date information on Service Bus message size limits, refer to the [Azure Service Bus quotas and limits](https://learn.microsoft.com/azure/service-bus-messaging/service-bus-quotas) documentation.

## Troubleshooting receiver issues

### Number of messages returned doesn't match number requested

When attempting to receive multiple messages using `receive_messages()` with `max_message_count` greater than 1, you're not guaranteed to receive the exact number requested.

**Why this happens:**
- Service Bus optimizes for throughput and latency
- After the first message is received, the receiver prioritizes processing it and does not attempt to build a batch of the requested size
- The `max_wait_time` controls how long to wait for the **first** message, not subsequent ones

**Resolution:**
1. **Don't assume all available messages will be received in one call:**
```python
import time
from azure.servicebus.exceptions import MessagingEntityNotFoundError, MessagingEntityDisabledError

def receive_all_available_messages(receiver, total_expected=None):
    """Receive all available messages from a queue/subscription"""
    all_messages = []
    
    while True:
        # Receive in batches
        messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        
        if not messages:
            break  # No more messages available
            
        all_messages.extend(messages)
        
        # Process messages immediately to avoid lock expiration
        for message in messages:
            try:
                # Process message logic here
                print(f"Processing: {message}")
                receiver.complete_message(message)
            except Exception as e:
                print(f"Error processing message: {e}")
                receiver.abandon_message(message)
    
    return all_messages
```

2. **Use continuous receiving for stream processing:**
```python
import time

def continuous_message_processing(receiver):
    """Continuously process messages as they arrive"""
    while True:
        try:
            messages = receiver.receive_messages(max_message_count=1, max_wait_time=60)
            
            for message in messages:
                # Process immediately
                try:
                    process_message(message)
                    receiver.complete_message(message)
                except Exception as e:
                    print(f"Processing failed: {e}")
                    receiver.abandon_message(message)
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Receive error: {e}")
            time.sleep(5)  # Brief pause before retry
```

### Mixing sync and async code

Mixing synchronous and asynchronous Service Bus operations can cause issues such as the `AutoLockRenewer` hanging indefinitely because the event loop is blocked. Ensure that blocking calls are not made when receiving and processing messages asynchronously.

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
