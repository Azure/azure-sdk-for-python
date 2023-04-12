# EventGrid Client Examples:

```python
    import os
    import asyncio
    from azure.core.credentials import AzureKeyCredential
    from azure.messaging.eventgrid.models import *
    from azure.core.messaging import CloudEvent


    EG_KEY = os.environ.get("EG_KEY")
    EG_ENDPOINT = os.environ.get("EG_ENDPOINT")
    TOPIC_NAME = os.environ.get("TOPIC_NAME")
    ES_NAME = os.environ.get("ES_NAME")
```


# Async Create Client
```python
    from azure.messaging.eventgrid.aio import eventgridClient

    # Create a client
    client = EventGridMessagingClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))
```

# Sync Create Client
```python
    from azure.messaging.eventgrid import EventGridMessagingClient

    # Create a client
    client = EventGridMessagingClient(EG_ENDPOINT, AzureKeyCredential(EG_KEY))
```

# Publish Samples

### Async
```python
    async def main():

        # Publish a CloudEvent
        try:
            cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
            await client.publish(topic_name=TOPIC_NAME, body=cloud_event)
        except Exception as e:
            print(e)


        # Publish a list of CloudEvents
        try:
            list_of_cloud_events = [cloud_event, cloud_event]
            await client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
        except Exception as e:
            print(e)

    asyncio.run(main())
```

### Sync
```python
    # Publish a CloudEvent
    try:
        cloud_event = CloudEvent(data="hello", source="https://example.com", type="example")
        client.publish(topic_name=TOPIC_NAME, body=cloud_event)
    except Exception as e:
        print(e)

    # Publish a list of CloudEvents
    try:
        list_of_cloud_events = [cloud_event, cloud_event]
        client.publish(topic_name=TOPIC_NAME, body=list_of_cloud_events)
    except Exception as e:
        print(e)
```



# Receive Samples

### Async
```python
    async def main():

        # Receive CloudEvents
        try:
            receive_response = await lient.receive(topic_name=TOPIC_NAME,event_subscription_name=ES_NAME,max_events=10,timeout=10)
            print(receive_response)
        except Exception as e:
            print(e)

    asyncio.run(main())
```

### Sync
```python
    # Receive CloudEvents
    try:
        receive_response = client.receive(topic_name=TOPIC_NAME,event_subscription_name=ES_NAME,max_events=10,timeout=10)
        print(receive_response)
    except Exception as e:
        print(e)
```

# Release Samples

### Async
```python
    async def main():

        # Release a LockToken
        try: 
            tokens = [LockToken({'lockToken': 'token'})]
            release = await client.release_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, tokens=tokens)
            print(release)
        except Exception as e:
            print(e)

    asyncio.run(main())
```

### Sync
```python
    # Release a LockToken
    try: 
        tokens = [LockToken({'lockToken': 'token'})]
        release = client.release_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, tokens=tokens)
        print(release)
    except Exception as e:
        print(e)

```

# Acknowledge Samples

### Async

```python
    async def main():

        # Acknowledge a batch of CloudEvents
        try: 
            lock_tokens = LockTokenInput(lock_tokens=["token"])
            ack = await client.acknowledge_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, lock_tokens=lock_tokens)
            print(ack)
        except Exception as e:
            print(e)

    asyncio.run(main())
```

### Sync
```python
    # Acknowledge a batch of CloudEvents
    try: 
        lock_tokens = LockTokenInput(lock_tokens=["token"])
        ack = client.acknowledge_batch_of_cloud_events(topic_name=TOPIC_NAME, event_subscription_name=ES_NAME, lock_tokens=lock_tokens)
        print(ack)
    except Exception as e:
        print(e)
```