# Guide for migrating azure-eventhub to v5 from v1

This guide is intended to assist in the migration to `azure-eventhub` v5 from v1. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-eventhub` v1 package is assumed. For those new to the Event Hubs client library for Python, please refer to the [README for `azure-eventhub`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
    - [Cross Service SDK improvements](#cross-service-sdk-improvements)
* [Important changes](#important-changes)
    - [Client hierarchy](#client-hierarchy)
    - [Client constructors](#client-constructors)
    - [Sending](#sending-events)
    - [Receiving](#receiving-events)
    - [Receiving with checkpoints](#receiving-with-checkpoints)
* [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python_introduction.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Event Hubs client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as 
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library to share a single authentication approach between clients
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries

## Important changes

### Client hierarchy
In the interest of simplifying the API surface, we've made two distinct clients, rather than having a single `EventHubClient`:
* `EventHubProducerClient` for sending events. 
* `EventHubConsumerClient` for receiving events. 

We've also merged the functionality from `EventProcessorHost` into `EventHubConsumerClient`. 

#### Approachability
By having a single entry point for sending, the `EventHubProducerClient` helps with the discoverability of the API
as you can explore all available features for sending events through methods from a single client, as opposed to searching
through documentation or exploring namespace for the types that you can instantiate.

Similarly, by having a single entry point for receiving of any type (from single partition, all partitions, or with load balancing and checkpointing features) within Event Hubs, the `EventHubConsumerClient` helps with the discoverability of the API as you can explore all available features for receiving events through methods from a single client, as opposed to searching
through documentation or exploring namespace for the types that you can instantiate.

#### Consistency
We now have methods with similar names, signature and location for sending and receiving.
This provides consistency and predictability on the various features of the library.

### Client constructors

- While we continue to support connection strings when constructing a client, the main difference is when using Azure Active Directory.
We now use the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library
to share a single authentication solution between clients of different Azure services.

In v1:
```python
    # Authenticate with address
    eventhub_client = EventHubClient(address)

    # Authenticate with connection string
    eventhub_client = EventHubClient.from_connection_string(conn_str) 
```
In v5:
```python
    # Authenticate with connection string
    producer_client = EventHubProducerClient.from_connection_string(conn_str) 
    consumer_client = EventHubConsumerClient.from_connection_string(conn_str) 

    # Authenticate with Active Directory
    from azure.identity import EnvironmentCredential
    producer_client = EventHubProducerClient(fully_qualified_namespace, eventhub_name, credential=EnvironmentCredential())
    consumer_client = EventHubConsumerClient(fully_qualified_namespace, eventhub_name, consumer_group='$Default', credential=EnvironmentCredential())

    # Authenticate consumer with connection string and checkpoint
    from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
    checkpoint_store = BlobCheckpointStore.from_connection_string(storage_conn_str, container_name)
    consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group='$Default', checkpoint_store=checkpoint_store)
```
### Sending events
* `add_sender`, `run`, and `stop` methods are replaced by `from_connection_string` method on `EventGridProducerClient` to more approachably open a connection ready for sending.
* `send` method is replaced by `send_batch` method on `EventGridProducerClient` to clarify that, instead of single `EventData`, either an `EventDataBatch` or list of `EventData` are sent in one call not exceeding the event hub frame size limit.
* `EventDataBatch` is created using the `create_batch` method and `EventData` messages are added to the batch using the `add` method, until the size limit is reached.

In v1:
```python
    client = EventHubClient(address)
    sender = client.add_sender()
    client.run()
    sender.send(EventData('Single message'))
    client.stop()
```

In v5:
```python
    producer_client = EventHubProducerClient.from_connection_string(conn_str, eventhub_name)

    # Send EventDataBatch
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData('Single message'))
    producer.send_batch(event_data_batch)

    # Send list of EventData
    event_data_batch = [EventData('Single message')]
    producer.send_batch(event_data_batch)
```

### Receiving events 
* `add_receiver`, `run`, and `stop` methods are replaced by `from_connection_string` method on `EventGridConsumerClient` to more approachably open a connection ready for receiving.
* `receive` method is renamed `receive_batch` on `EventGridConsumerClient` to be more consistent in the usage of `batch` suffix in other methods on the producer and consumer when receiving or sending batches.
* `receive` method on `EventGridConsumerClient` now receives only a single event as opposed to previously receiving a batch of events to more clearly reflect the naming, in which `batch` is not used as a suffix.

In v1:
```python
    client = EventHubClient(address)
    receiver = client.add_receiver(consumer_group, partition)
    client.run()
    batch = receiver.receive()
    client.stop()
```

In v5:
```python
    # Receive
    def on_event(partition_context, event):
        print("Received event from partition: {}.".format(partition_context.partition_id))
    
    consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group, eventhub_name=eh_name)
    with consumer_client:
        consumer_client.receive(on_event=on_event)

    # Receive batch
    def on_event_batch(partition_context, event_batch):
        print("Partition {}, Received count: {}".format(partition_context.partition_id, len(event_batch)))
        
    consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group, eventhub_name=eh_name)
    with consumer_client:
        consumer_client.receive_batch(on_event_batch=on_event_batch)
```

### Receiving with checkpoints
Consuming events and saving checkpoints using a checkpoint store was not available in v1.

In v5:
```python
    # Receive with checkpoint
    from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

    def on_event(partition_context, event):
        print("Received event from partition: {}.".format(partition_context.partition_id))
        partition_context.update_checkpoint(event)
    
    checkpoint_store = BlobCheckpointStore.from_connection_string(storage_conn_str, container_name)
    consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group, checkpoint_store=checkpoint_store)
    with consumer_client:
        consumer_client.receive(on_event=on_event)

    # Receive batch with checkpoint
    from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

    def on_event_batch(partition_context, event_batch):
        print("Partition {}, Received count: {}".format(partition_context.partition_id, len(event_batch)))
        # TODO: find out whether anything should be passed in, and if so, pass it in
        partition_context.update_checkpoint()
        
    checkpoint_store = BlobCheckpointStore.from_connection_string(storage_conn_str, container_name)
    consumer_client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group, checkpoint_store=checkpoint_store)
    with consumer_client:
        consumer_client.receive_batch(on_event_batch=on_event_batch)
```

## Additional samples

More examples can be found at [Samples for azure-eventhub](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub/samples)