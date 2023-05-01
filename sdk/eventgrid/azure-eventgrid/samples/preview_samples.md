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

# Publish Samples

### Async
```python
    async def main():

        # Publish a CloudEvent
        try:
            cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
            await client.publish(topic_name=TOPIC_NAME, body=cloud_event)
        except HttpResponseError:
            raise


        # Publish a list of CloudEvents
        try:
            list_of_cloud_events = [cloud_event, cloud_event]
            await client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
        except HttpResponseError:
            raise

    asyncio.run(main())
```

### Sync
```python
    # Publish a CloudEvent
    try:
        cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
        client.publish(topic_name=TOPIC_NAME, body=cloud_event)
    except HttpResponseError:
        raise

    # Publish a list of CloudEvents
    try:
        list_of_cloud_events = [cloud_event, cloud_event]
        client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
    except HttpResponseError:
        raise
```



# Receive Samples

### Async
```python
    async def main():

        # Receive CloudEvents
        try:
            receive_response = await client.receive(topic_name=TOPIC_NAME,event_subscription_name=EVENT_SUBSCRIPTION_NAME,max_events=10,timeout=10)
            print(receive_response)
        except HttpResponseError:
            raise

    asyncio.run(main())
```

### Sync
```python
    # Receive CloudEvents
    try:
        receive_response = client.receive(topic_name=TOPIC_NAME,event_subscription_name=EVENT_SUBSCRIPTION_NAME,max_events=10,timeout=10)
        print(receive_response)
    except HttpResponseError:
        raise
```

# Release Samples

### Async
```python
    async def main():

        # Release a LockToken
        try: 
            tokens = [LockToken({'lockToken': 'token'})]
            release = await client.release_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, tokens=tokens)
            print(release)
        except HttpResponseError:
            raise

    asyncio.run(main())
```

### Sync
```python
    # Release a LockToken
    try: 
        tokens = [LockToken({'lockToken': 'token'})]
        release = client.release_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, tokens=tokens)
        print(release)
    except HttpResponseError:
        raise

```

# Acknowledge Samples

### Async

```python
    async def main():

        # Acknowledge a batch of CloudEvents
        try: 
            lock_tokens = LockTokenInput(lock_tokens=["token"])
            ack = await client.acknowledge_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=lock_tokens)
            print(ack)
        except HttpResponseError:
            raise

    asyncio.run(main())
```

### Sync
```python
    # Acknowledge a batch of CloudEvents
    try: 
        lock_tokens = LockTokenInput(lock_tokens=["token"])
        ack = client.acknowledge_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=EVENT_SUBSCRIPTION_NAME, lock_tokens=lock_tokens)
        print(ack)
    except HttpResponseError:
        raise
```