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
  * [Cannot send batch with multiple partition keys](#cannot-send-batch-with-multiple-partition-keys)
  * [Batch fails to send](#batch-fails-to-send)
  * [Message encoding issues](#message-encoding-issues)
* [Troubleshooting receiver issues](#troubleshooting-receiver-issues)
  * [Number of messages returned doesn't match number requested](#number-of-messages-returned-doesnt-match-number-requested)
  * [Message completion behavior](#message-completion-behavior)
  * [Receive operation hangs](#receive-operation-hangs)
  * [Messages not being received](#messages-not-being-received)
* [Troubleshooting quota and capacity issues](#troubleshooting-quota-and-capacity-issues)
  * [Quota exceeded errors](#quota-exceeded-errors)
  * [Entity not found errors](#entity-not-found-errors)
* [Threading and concurrency issues](#threading-and-concurrency-issues)
  * [Thread safety limitations](#thread-safety-limitations)
  * [Async/await best practices](#asyncawait-best-practices)
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

### Cannot send batch with multiple partition keys

When sending to a partition-enabled entity, all messages included in a single send operation must have the same `session_id` if the entity is session-enabled, or the same custom properties that determine partitioning.

**Error symptoms:**
- Messages are rejected or go to different partitions than expected
- Inconsistent message ordering

**Resolution:**
1. **For session-enabled entities, ensure all messages in a batch have the same session ID:**
```python
from azure.servicebus import ServiceBusMessage

# Correct: All messages have the same session_id
messages = [
    ServiceBusMessage("Message 1", session_id="session1"),
    ServiceBusMessage("Message 2", session_id="session1"),
    ServiceBusMessage("Message 3", session_id="session1")
]

with sender:
    sender.send_messages(messages)
```

2. **For partitioned entities, group messages by partition key:**
```python
# Group messages by partition key before sending
partition1_messages = [
    ServiceBusMessage("Message 1", application_properties={"region": "east"}),
    ServiceBusMessage("Message 2", application_properties={"region": "east"})
]

partition2_messages = [
    ServiceBusMessage("Message 3", application_properties={"region": "west"}),
    ServiceBusMessage("Message 4", application_properties={"region": "west"})
]

# Send each group separately
with sender:
    sender.send_messages(partition1_messages)
    sender.send_messages(partition2_messages)
```

### Batch fails to send

The Service Bus service has size limits for message batches and individual messages.

**Error symptoms:**
- `MessageSizeExceededError` when sending batches
- Messages larger than expected failing to send

**Resolution:**
1. **Reduce batch size or message payload:**
```python
from azure.servicebus import ServiceBusMessage
from azure.servicebus.exceptions import MessageSizeExceededError
import json

def send_large_dataset(sender, data_list, max_batch_size=100):
    """Send large datasets in smaller batches"""
    for i in range(0, len(data_list), max_batch_size):
        batch = data_list[i:i + max_batch_size]
        messages = [ServiceBusMessage(json.dumps(item)) for item in batch]
        
        try:
            sender.send_messages(messages)
        except MessageSizeExceededError:
            # If batch is still too large, send individually
            for message in messages:
                sender.send_messages(message)
```

2. **Check message size limits:**
   - Standard tier: 256 KB per message
   - Premium tier: 1 MB per message
   - Batch limit: 1 MB regardless of tier

3. **Use message properties for metadata instead of body:**
```python
# Instead of including metadata in message body
large_message = ServiceBusMessage(json.dumps({
    "data": large_data_payload,
    "metadata": {"source": "app1", "timestamp": "2023-01-01"}
}))

# Use application properties for metadata
optimized_message = ServiceBusMessage(large_data_payload)
optimized_message.application_properties = {
    "source": "app1", 
    "timestamp": "2023-01-01"
}
```

### Message encoding issues

Python string encoding can cause issues when sending messages with special characters.

**Error symptoms:**
- Messages appear corrupted on the receiver side
- Encoding/decoding exceptions

**Resolution:**
1. **Explicitly handle string encoding:**
```python
import json
from azure.servicebus import ServiceBusMessage

# For text messages, ensure proper UTF-8 encoding
text_data = "Message with special characters: ñáéíóú"
message = ServiceBusMessage(text_data.encode('utf-8'))

# For JSON data, use explicit encoding
json_data = {"message": "Data with unicode: ñáéíóú"}
json_string = json.dumps(json_data, ensure_ascii=False)
message = ServiceBusMessage(json_string.encode('utf-8'))

# Set content type to help receivers
message.content_type = "application/json; charset=utf-8"
```

2. **Handle binary data correctly:**
```python
# For binary data, pass bytes directly
binary_data = b"\x00\x01\x02\x03"
message = ServiceBusMessage(binary_data)
message.content_type = "application/octet-stream"
```

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

### Message completion behavior

**Important limitation:** The Pure Python AMQP implementation used by the Azure Service Bus Python SDK does not currently wait for dispositions from the service to acknowledge message completion operations.

**What this means:**
- When you call `complete_message()`, `abandon_message()`, or `dead_letter_message()`, the operation returns immediately
- The SDK does not wait for confirmation from the Service Bus service that the message was actually settled
- This can lead to scenarios where the local operation succeeds but the service operation fails

**Implications:**
1. **Message state uncertainty:**
```python
# This operation may succeed locally but fail on the service
try:
    receiver.complete_message(message)
    print("Message completed successfully")  # This may be misleading
except Exception as e:
    print(f"Local completion failed: {e}")
    # But even if no exception, service operation might have failed
```

2. **Potential message redelivery:**
- If the service doesn't receive the completion acknowledgment, the message may be redelivered
- This can lead to duplicate processing if not handled properly

**Mitigation strategies:**
1. **Implement idempotent message processing:**
```python
import hashlib

processed_messages = set()

def process_message_idempotently(receiver, message):
    """Process messages in an idempotent manner"""
    # Create a unique identifier for the message
    message_id = message.message_id or hashlib.md5(str(message.body).encode()).hexdigest()
    
    if message_id in processed_messages:
        print(f"Message {message_id} already processed, skipping")
        receiver.complete_message(message)
        return
    
    try:
        # Your message processing logic here
        result = process_business_logic(message)
        
        # Record successful processing before completing
        processed_messages.add(message_id)
        receiver.complete_message(message)
        
        return result
    except Exception as e:
        print(f"Processing failed for message {message_id}: {e}")
        receiver.abandon_message(message)
        raise
```

2. **Use external tracking for critical operations:**
```python
import logging

def track_message_completion(receiver, message, tracking_store):
    """Track message completion in external store"""
    message_id = message.message_id
    
    try:
        # Process the message
        result = process_message(message)
        
        # Store completion in external tracking system
        tracking_store.mark_completed(message_id, result)
        
        # Complete the message in Service Bus
        receiver.complete_message(message)
        
        logging.info(f"Message {message_id} processed and completed successfully")
        
    except Exception as e:
        logging.error(f"Failed to process message {message_id}: {e}")
        
        # Check if we should retry or dead letter
        if should_retry(message, e):
            receiver.abandon_message(message)
        else:
            receiver.dead_letter_message(message, reason="ProcessingFailed", error_description=str(e))
```

3. **Monitor for redelivered messages:**
```python
def handle_potential_redelivery(receiver, message):
    """Handle messages that might be redelivered due to completion uncertainty"""
    delivery_count = message.delivery_count
    
    if delivery_count > 1:
        logging.warning(f"Message has been delivered {delivery_count} times. "
                       f"This might indicate completion acknowledgment issues.")
    
    # Process with extra caution for high delivery count messages
    if delivery_count > 3:
        # Consider different processing logic or dead lettering
        logging.error(f"Message delivery count too high ({delivery_count}), dead lettering")
        receiver.dead_letter_message(message, 
                                   reason="HighDeliveryCount",
                                   error_description=f"Delivered {delivery_count} times")
        return
    
    # Normal processing
    process_message_idempotently(receiver, message)
```

### Receive operation hangs

Receive operations may appear to hang when no messages are available.

**Symptoms:**
- `receive_messages()` doesn't return for extended periods
- Application appears unresponsive

**Resolution:**
1. **Set appropriate timeouts:**
```python
# Don't wait indefinitely for messages
messages = receiver.receive_messages(max_message_count=5, max_wait_time=30)

# For polling scenarios, use shorter timeouts
def poll_for_messages(receiver):
    while True:
        messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
        
        if messages:
            for message in messages:
                process_message(message)
                receiver.complete_message(message)
        else:
            print("No messages available, waiting...")
            time.sleep(1)
```

2. **Use async operations with proper cancellation:**
```python
import asyncio

async def receive_with_cancellation(receiver):
    try:
        # Use asyncio timeout for better control
        messages = await asyncio.wait_for(
            receiver.receive_messages(max_message_count=10, max_wait_time=30),
            timeout=35  # Slightly longer than max_wait_time
        )
        return messages
    except asyncio.TimeoutError:
        print("Receive operation timed out")
        return []
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

## Threading and concurrency issues

### Thread safety limitations

**Important:** The Azure Service Bus Python SDK is **not thread-safe or coroutine-safe**. Using the same client instances across multiple threads or tasks without proper synchronization can lead to:

- Connection errors and unexpected exceptions
- Message corruption or loss
- Deadlocks and race conditions
- Unpredictable behavior

**Best practices:**

1. **Use separate client instances per thread/task:**
```python
import threading
from azure.servicebus import ServiceBusClient

def worker_thread(connection_string, queue_name):
    # Create a separate client instance for each thread
    client = ServiceBusClient.from_connection_string(connection_string)
    with client:
        sender = client.get_queue_sender(queue_name)
        with sender:
            # Perform operations...
            pass

# Start multiple threads with separate clients
threads = []
for i in range(5):
    t = threading.Thread(target=worker_thread, args=(connection_string, queue_name))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

2. **Use connection pooling patterns when needed:**
```python
# For high-throughput scenarios, consider using a thread-safe queue
# to manage client instances
import queue
import threading

client_pool = queue.Queue()

def get_client():
    try:
        return client_pool.get_nowait()
    except queue.Empty:
        return ServiceBusClient.from_connection_string(connection_string)

def return_client(client):
    try:
        client_pool.put_nowait(client)
    except queue.Full:
        client.close()
```

3. **Avoid sharing clients across async tasks:**
```python
# DON'T DO THIS
client = ServiceBusClient.from_connection_string(connection_string)

async def bad_async_pattern():
    # Multiple tasks sharing the same client can cause issues
    sender = client.get_queue_sender(queue_name)
    # This can lead to race conditions

# DO THIS INSTEAD
async def good_async_pattern():
    # Each async function should use its own client
    async with ServiceBusClient.from_connection_string(connection_string) as client:
        sender = client.get_queue_sender(queue_name)
        async with sender:
            # Perform operations safely
            pass
```

### Async/await best practices

When using the async APIs in the Python Service Bus SDK:

1. **Always use async context managers properly:**
```python
async def proper_async_usage():
    async with ServiceBusClient.from_connection_string(connection_string) as client:
        async with client.get_queue_sender(queue_name) as sender:
            message = ServiceBusMessage("Hello World")
            await sender.send_messages(message)
        
        async with client.get_queue_receiver(queue_name) as receiver:
            messages = await receiver.receive_messages(max_message_count=10)
            for message in messages:
                await receiver.complete_message(message)
```

2. **Don't mix sync and async code without proper handling:**
```python
# Avoid mixing sync and async incorrectly
async def mixed_code_example():
    # Don't call synchronous methods from async context without wrapping
    # client = ServiceBusClient.from_connection_string(conn_str)  # This is sync
    
    # Instead, create clients within async context or use proper wrapping
    async with ServiceBusClient.from_connection_string(conn_str) as client:
        pass
```

3. **Handle async exceptions properly:**
```python
import asyncio
from azure.servicebus import ServiceBusError

async def handle_async_errors():
    try:
        async with ServiceBusClient.from_connection_string(connection_string) as client:
            async with client.get_queue_receiver(queue_name) as receiver:
                messages = await receiver.receive_messages(max_message_count=1, max_wait_time=5)
                # Process messages...
    except ServiceBusError as e:
        print(f"Service Bus error: {e}")
    except asyncio.TimeoutError:
        print("Operation timed out")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

**Common threading/concurrency mistakes to avoid:**

- Sharing `ServiceBusClient`, `ServiceBusSender`, or `ServiceBusReceiver` instances across threads
- Not properly closing clients and their resources in multi-threaded scenarios
- Using the same connection string with too many concurrent clients (can hit connection limits)
- Mixing blocking and non-blocking operations incorrectly
- Not handling connection failures in multi-threaded scenarios

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
- Using concurrent message processing
- Optimizing your message processing logic
- Using `prefetch_count` to pre-fetch messages
- Scaling out with multiple receivers

### Q: What's the difference between `complete_message()` and `abandon_message()`?

**A:** 
- `complete_message()`: Removes the message from the queue/subscription (successful processing)
- `abandon_message()`: Returns the message to the queue/subscription for reprocessing

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
