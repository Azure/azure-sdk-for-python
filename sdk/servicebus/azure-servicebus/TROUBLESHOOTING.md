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

- **ServiceBusCommunicationError:** Client isn't able to establish a connection to Service Bus. Make sure the supplied host name is correct and the host is reachable. If your code runs in an environment with a firewall/proxy, ensure that the traffic to the Service Bus domain/IP address and ports isn't blocked. For information about required ports, see [What ports do I need to open on the firewall?](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-faq#what-ports-do-i-need-to-open-on-the-firewall--).

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

#### Python-Specific Considerations

- **ImportError/ModuleNotFoundError:** Common when Azure Service Bus dependencies are not properly installed. Ensure you have installed the correct package version:
```bash
pip install azure-servicebus
```

- **TypeError:** Often occurs when passing incorrect data types to Service Bus methods:
```python
# Incorrect: passing string instead of ServiceBusMessage
sender.send_messages("Hello World")  # This will fail

# Correct: create ServiceBusMessage objects
from azure.servicebus import ServiceBusMessage
message = ServiceBusMessage("Hello World")
sender.send_messages(message)
```

- **ConnectionError/socket.gaierror:** Network-level errors that may require checking DNS resolution and network connectivity:
```python
import socket
try:
    # Test DNS resolution
    socket.gethostbyname("your-namespace.servicebus.windows.net")
except socket.gaierror as e:
    print(f"DNS resolution failed: {e}")
```

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

When attempting to receive multiple messages using `receive_messages()` with `max_message_count` greater than 1, you're not guaranteed to receive the exact number requested.

**Why this happens:**
- Service Bus optimizes for throughput and latency
- After the first message is received, the receiver waits only a short time (typically 20ms) for additional messages
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

### Messages not being received

Messages might not be received due to various configuration or state issues.

**Common causes and resolutions:**

1. **Check entity state:**
```python
# Verify the queue/subscription exists and is active
try:
    # This will fail if entity doesn't exist
    receiver = client.get_queue_receiver(queue_name)
    messages = receiver.receive_messages(max_message_count=1, max_wait_time=5)
    
    if not messages:
        print("No messages available - check if messages are being sent")
    
except MessagingEntityNotFoundError:
    print("Queue/subscription does not exist")
except MessagingEntityDisabledError:
    print("Queue/subscription is disabled")
```

2. **Verify message filters (for subscriptions):**
```python
# For topic subscriptions, check if messages match subscription filters
from azure.servicebus.management import ServiceBusAdministrationClient

admin_client = ServiceBusAdministrationClient.from_connection_string(connection_string)

# Check subscription rules
rules = admin_client.list_rules(topic_name, subscription_name)
for rule in rules:
    print(f"Rule: {rule.name}, Filter: {rule.filter}")
```

3. **Check for competing consumers:**
```python
# Multiple receivers on the same queue will compete for messages
# Ensure this is intended behavior or use topic/subscription pattern

# For debugging, temporarily use peek to see if messages exist
messages = receiver.peek_messages(max_message_count=10)
print(f"Found {len(messages)} messages in queue without receiving them")
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

Please view the [exceptions reference docs](https://docs.microsoft.com/python/api/azure-servicebus/azure.servicebus.exceptions) for detailed descriptions of our common Exception types.
