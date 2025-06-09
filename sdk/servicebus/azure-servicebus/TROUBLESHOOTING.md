# Troubleshoot Azure Service Bus client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Service Bus client library for Python.

## Table of contents

* [General troubleshooting](#general-troubleshooting)
  * [Enable client logging](#enable-client-logging)
  * [Common exceptions](#common-exceptions)
  * [Timeouts](#timeouts)
* [Threading and concurrency issues](#threading-and-concurrency-issues)
  * [Thread safety limitations](#thread-safety-limitations)
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
* [Troubleshooting session handling issues](#troubleshooting-session-handling-issues)
  * [Session lock issues](#session-lock-issues)
  * [Session cannot be locked](#session-cannot-be-locked)
* [Troubleshooting receiver issues](#troubleshooting-receiver-issues)
  * [Number of messages returned doesn't match number requested](#number-of-messages-returned-doesnt-match-number-requested)
  * [Messages not being received](#messages-not-being-received)
  * [Dead letter queue issues](#dead-letter-queue-issues)
  * [Mixing sync and async code](#mixing-sync-and-async-code)
* [Troubleshooting quota and capacity issues](#troubleshooting-quota-and-capacity-issues)
  * [Quota exceeded errors](#quota-exceeded-errors)
  * [Entity not found errors](#entity-not-found-errors)
* [Frequently asked questions](#frequently-asked-questions)
* [Get additional help](#get-additional-help)

## General troubleshooting

Azure Service Bus client library will raise exceptions defined in [Azure Core](https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions) and Service Bus-specific exceptions in `azure.servicebus.exceptions`.

### Enable client logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.

Basic information about AMQP operations (connections, links, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including AMQP frame tracing and **unredacted** headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

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

The Service Bus client library raises the following exceptions defined in `azure.servicebus.exceptions`:

#### Connection and Authentication Exceptions

- **ServiceBusConnectionError:** Connection to the service failed. Check network connectivity and retry.
- **ServiceBusAuthenticationError:** Authentication failed. Verify credentials are correct.
- **ServiceBusAuthorizationError:** Authorization failed. Check that credentials have the required permissions.

#### Operation and Timeout Exceptions

- **OperationTimeoutError:** Service did not respond within the expected time. Retry the operation.
- **ServiceBusCommunicationError:** Unable to establish connection to Service Bus. Check network connectivity and firewall settings. For firewall configuration, see [What ports do I need to open on the firewall?](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-faq#what-ports-do-i-need-to-open-on-the-firewall--).

#### Message Handling Exceptions

- **MessageSizeExceededError:** Message content exceeds size limits. Reduce message size or batch count.
- **MessageAlreadySettled:** Attempt to settle an already-settled message.
- **MessageLockLostError:** Message lock expired. Use `AutoLockRenewer` or process messages faster.
- **MessageNotFoundError:** Message with specified sequence number not found. Check if message was already processed.

#### Session Handling Exceptions

- **SessionLockLostError:** Session lock expired. Reconnect to the session or use `AutoLockRenewer`.
- **SessionCannotBeLockedError:** Session is locked by another client. Wait for lock to expire.

#### Service and Entity Exceptions

- **ServiceBusQuotaExceededError:** Entity has reached maximum size or connection limit. Create space by receiving messages.
- **ServiceBusServerBusyError:** Service is temporarily overloaded. Implement exponential backoff retry.
- **MessagingEntityNotFoundError:** Entity does not exist or has been deleted.
- **MessagingEntityDisabledError:** Entity is disabled. Enable the entity to perform operations.

#### Auto Lock Renewal Exceptions

- **AutoLockRenewFailed:** Lock renewal failed. Re-register the renewable message or session.
- **AutoLockRenewTimeout:** Lock renewal timeout exceeded. Extend timeout or re-register the object.

### Timeouts

There are various timeouts a user should be aware of within the library:

- **10 minute service side link closure:** A link, once opened, will be closed after 10 minutes idle to protect the service against resource leakage. This should largely be transparent to a user, but if you notice a reconnect occurring after such a duration, this is why. Performing any operations, including management operations, on the link will extend this timeout.

- **max_wait_time:** Provided on creation of a receiver or when calling `receive_messages()`, the time after which receiving messages will halt after no traffic. This applies both to the imperative `receive_messages()` function as well as the length a generator-style receive will run for before exiting if there are no messages. Passing None (default) will wait forever, up until the 10 minute threshold if no other action is taken.

> **NOTE:** If processing of a message or session is sufficiently long as to cause timeouts, as an alternative to calling `receiver.renew_message_lock`/`receiver.session.renew_lock` manually, one can leverage the `AutoLockRenewer` functionality.

## Threading and concurrency issues

### Thread safety limitations

**Important:** The Azure Service Bus Python SDK is **not thread-safe or coroutine-safe**. Using the same client instances across multiple threads or tasks without proper synchronization can lead to:

- Connection errors and unexpected exceptions
- Message corruption or loss
- Deadlocks and race conditions
- Unpredictable behavior

It is up to the running application to use these classes in a thread-safe and coroutine-safe manner. Note: If sending concurrently, ensure that locks are used.

**Synchronous concurrent sending with locks:**
```python
import threading
from azure.servicebus import ServiceBusClient, ServiceBusMessage

FULLY_QUALIFIED_NAMESPACE = "your-namespace.servicebus.windows.net"
QUEUE_NAME = "your-queue"
CONNECTION_STRING = "your-connection-string"

# Lock for thread-safe operations
lock = threading.Lock()

def send_messages_sync(connection_string, queue_name):
    """Send messages using synchronous API with locks"""
    with lock:
        with ServiceBusClient.from_connection_string(connection_string) as client:
            with client.get_queue_sender(queue_name) as sender:
                messages = [ServiceBusMessage(f"Message {i}") for i in range(10)]
                sender.send_messages(messages)

# Create and start multiple threads
threads = []
for i in range(3):
    t = threading.Thread(target=send_messages_sync, args=(CONNECTION_STRING, QUEUE_NAME))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()
```

**Asynchronous concurrent sending with locks:**
```python
import asyncio
from azure.identity.aio import DefaultAzureCredential
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

FULLY_QUALIFIED_NAMESPACE = ".servicebus.windows.net"
QUEUE_NAME = "<queue name>"

lock = asyncio.Lock()

async def send_messages(client):
    async with lock:
        async with client.get_queue_sender(QUEUE_NAME) as sender:
            await asyncio.gather(*(sender.send_messages(ServiceBusMessage("hello")) for _ in range(10)))

async def main():
    credential = DefaultAzureCredential()
    async with ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential) as client:
        await send_messages(client)

if __name__ == "__main__":
    asyncio.run(main())
```

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
- Service Bus supports HTTP proxy for AMQP over WebSockets
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

## Troubleshooting receiver issues

### Number of messages returned doesn't match number requested

When calling `receive_messages()` with `max_message_count` > 1, you may receive fewer messages than requested.

**Cause:** Service Bus waits briefly (20ms) for additional messages after the first. `max_wait_time` only applies to the first message.

**Resolution:** Call `receive_messages()` in a loop to get all available messages:

```python
all_messages = []
while True:
    messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
    if not messages:
        break
    all_messages.extend(messages)
    for message in messages:
        receiver.complete_message(message)
```

### Messages not being received

**Common causes:**
- Entity doesn't exist or is disabled
- No messages in the queue/subscription
- Message filters excluding messages (subscriptions)
- Lock duration too short

**Resolution:**
1. Verify entity exists: `ServiceBusAdministrationClient.get_queue()` or `get_subscription()`
2. Check entity is enabled
3. For subscriptions, verify filter rules allow your messages
4. Increase `max_wait_time` or check message count

### Dead letter queue issues

Messages move to the dead letter queue due to TTL expiration, max delivery count exceeded, or explicit dead lettering.

**Resolution:**
```python
# Access dead letter queue to inspect messages
dlq_receiver = client.get_queue_receiver(
    queue_name="your_queue", 
    sub_queue=ServiceBusSubQueue.DEAD_LETTER
)

messages = dlq_receiver.receive_messages(max_message_count=10)
for message in messages:
    print(f"Reason: {message.dead_letter_reason}")
    print(f"Description: {message.dead_letter_error_description}")
```

### Mixing sync and async code

Mixing synchronous and asynchronous Service Bus operations can cause issues such as async operations hanging indefinitely due to the event loop being blocked. Ensure that blocking calls are not made when receiving and message processing.

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

## Frequently asked questions

### Q: Why am I getting connection timeout errors?

**A:** Connection timeouts can occur due to:
- Network connectivity issues
- Firewall blocking AMQP ports (5671-5672)
- DNS resolution problems

Try using AMQP over WebSockets (port 443) or check your network configuration.

### Q: How do I handle transient errors?

**A:** Implement retry logic with exponential backoff for transient errors like:
- `ServiceBusConnectionError`
- `OperationTimeoutError`
- `ServiceBusServerBusyError`

### Q: Why are my messages going to the dead letter queue?

**A:** Common reasons include:
- Message TTL expiration
- Maximum delivery count exceeded
- Explicit dead lettering in message processing logic
- Poison message detection

Check the `dead_letter_reason` and `dead_letter_error_description` properties on dead lettered messages.

### Q: How do I process messages faster?

**A:** Consider:
- Using concurrent message processing (with separate client instances per thread/task)
- Optimizing your message processing logic
- Using `prefetch_count` to pre-fetch messages (use with caution - see note below)
- Scaling out with multiple receivers (on different clients)

**Note on prefetch_count:** Be careful when using `prefetch_count` as it can cause message lock expiration if processing takes too long. The client cannot extend locks for prefetched messages.

### Q: What's the difference between `complete_message()` and `abandon_message()`?

**A:** 
- `complete_message()`: Removes the message from the queue/subscription (successful processing)
- `abandon_message()`: Returns the message to the queue/subscription for reprocessing

**Important:** Due to Python AMQP implementation limitations, these operations return immediately without waiting for service acknowledgment. Implement idempotent processing to handle potential redelivery.

### Q: How do I handle message ordering?

**A:** 
- Use **sessions** for guaranteed message ordering within a session
- For partitioned entities, messages with the same partition key maintain order
- Regular queues do not guarantee strict FIFO ordering

```python
# Using sessions for ordered processing
with client.get_queue_receiver(queue_name, session_id="order_123") as session_receiver:
    messages = session_receiver.receive_messages(max_message_count=10)
    
    # Messages within this session are processed in order
    for message in messages:
        process_message_in_order(message)
        session_receiver.complete_message(message)
```

### Q: How do I implement retry logic for transient failures?

**A:**
```python
import time
import random
from azure.servicebus.exceptions import ServiceBusError

def exponential_backoff_retry(operation, max_retries=3):
    """Implement exponential backoff retry for Service Bus operations"""
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except ServiceBusError as e:
            if attempt == max_retries:
                raise
            
            # Check if error is retryable
            if hasattr(e, 'reason'):
                retryable_reasons = ['ServiceTimeout', 'ServerBusy', 'ServiceCommunicationProblem']
                if e.reason not in retryable_reasons:
                    raise
            
            # Calculate backoff delay
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

# Usage example
def send_with_retry(sender, message):
    return exponential_backoff_retry(lambda: sender.send_messages(message))
```

### Q: How do I monitor message processing performance?

**A:**
```python
import time
import logging
from contextlib import contextmanager

@contextmanager
def message_processing_timer(message_id):
    """Context manager to time message processing"""
    start_time = time.time()
    try:
        yield
    finally:
        processing_time = time.time() - start_time
        logging.info(f"Message {message_id} processed in {processing_time:.3f}s")

# Usage
def process_with_monitoring(receiver, message):
    with message_processing_timer(message.message_id):
        # Your processing logic
        result = process_message(message)
        receiver.complete_message(message)
        return result
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
