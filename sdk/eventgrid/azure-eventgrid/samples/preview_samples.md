# EventGrid Client Examples:

```python
    import os
    import asyncio
    from azure.core.credentials import AzureKeyCredential
    from azure.eventgrid.models import *
    from azure.core.messaging import CloudEvent
    from azure.core.exceptions import HttpResponseError


    EVENTGRID_KEY = os.environ.get("EVENTGRID_KEY")
    EVENTGRID_ENDPOINT = os.environ.get("EVENTGRID_ENDPOINT")
    TOPIC_NAME = os.environ.get("TOPIC_NAME")
    EVENT_SUBSCRIPTION_NAME = os.environ.get("EVENT_SUBSCRIPTION_NAME")
```


# Async Create Client
```python
    from azure.eventgrid.aio import EventGridClient

    # Create a client
    client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))
```

# Sync Create Client
```python
    from azure.eventgrid import EventGridClient

    # Create a client
    client = EventGridClient(EVENTGRID_ENDPOINT, AzureKeyCredential(EVENTGRID_KEY))
```

# Publish Cloud Events

### Async
```python
    async def main():
        cloud_event_reject = CloudEvent(data="reject", source="https://example.com", type="example")
        cloud_event_release = CloudEvent(data="release", source="https://example.com", type="example")
        cloud_event_ack = CloudEvent(data="acknowledge", source="https://example.com", type="example")

        # Publish a CloudEvent
        try:
            await client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event_reject)
        except HttpResponseError:
            raise


        # Publish a list of CloudEvents
        try:
            list_of_cloud_events = [cloud_event_release, cloud_event_ack]
            await client.publish_cloud_events(topic_name=TOPIC_NAME, body=list_of_cloud_events)
        except HttpResponseError:
            raise

    asyncio.run(main())
```

### Sync
```python
    cloud_event_reject = CloudEvent(data="reject", source="https://example.com", type="example")
    cloud_event_release = CloudEvent(data="release", source="https://example.com", type="example")
    cloud_event_ack = CloudEvent(data="acknowledge", source="https://example.com", type="example")

    # Publish a CloudEvent
    try:
        client.publish_cloud_events(topic_name=TOPIC_NAME, body=cloud_event_reject)
    except HttpResponseError:
        raise

    # Publish a list of CloudEvents
    try:
        list_of_cloud_events = [cloud_event_release, cloud_event_ack]
        client.publish_cloud_events(topic_name=TOPIC_NAME, body=list_of_cloud_events)
    except HttpResponseError:
        raise
```

# Receive Published Cloud Events

### Async
```python
    try:
        async with client:
            receive_results = await client.receive_cloud_events(
                topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=10, max_wait_time=10
            )
    except HttpResponseError:
        raise

```

### Sync
```python
    try:
        receive_results = client.receive_cloud_events(
            topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, max_events=10, max_wait_time=10
        )
    except HttpResponseError:
        raise
```

# Iterate through the results and collect the lock tokens for events we want to release/acknowledge/reject:

### Async and Sync
```python
    release_events = []
    acknowledge_events = []
    reject_events = []

    for detail in receive_results.get("value"):
        cloud_event = detail.get("event")
        broker_properties = detail.get("brokerProperties")
        if cloud_event.data == "release":
            release_events.append(broker_properties.get("lockToken"))
        elif cloud_event.data == "acknowledge"
            acknowledge_events.append(broker_properties.get("lockToken"))
        else:
            reject_events.append(broker_properties.get("lockToken"))
```
# Release/Acknowledge/Reject events

### Async
```python

if len(release_events) > 0:
    try:
        release_result = await client.release_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=release_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in release_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")

if len(acknowledge_events) > 0:
    try:
        ack_result = await client.acknowledge_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=acknowledge_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in ack_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")

if len(reject_events) > 0:
    try:
        reject_result = await client.reject_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=reject_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in reject_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")
```

### Sync
```python

if len(release_events) > 0:
    try:
        release_result = client.release_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=release_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in release_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")

if len(acknowledge_events) > 0:
    try:
        ack_result = client.acknowledge_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=acknowledge_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in ack_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")

if len(reject_events) > 0:
    try:
        reeject_result = client.reject_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=reject_events)
    except HttpResponseError:
        raise

    for succeeded_lock_token in reject_result.get("succeeded_lock_tokens"):
        print(f"Succeeded Lock Token:{succeeded_lock_token}")
```
