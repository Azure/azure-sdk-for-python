# Guide for migrating to azure-eventgrid v4.0 from azure-eventgrid v1.3

This guide is intended to assist in the migration to azure-eventgrid v4.0 from azure-eventgrid v1.3. It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the azure-eventgrid v1.3 package is assumed. For those new to the eventgrid client library for Python, please refer to the [README for azure-eventgrid v4.0](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
  - [Cross Service SDK improvements](#cross-service-sdk-improvements)
* [Important Changes](#important-changes)
  - [Support for Cloud Events](#support-for-cloud-events)
  - [Client Constructors](#client-constructors)
  - [Publishing Events](#publishing-events)
  - [Consuming Events](#consuming-events)
* [Additional Samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem. One of the most important is that the client libraries for different Azure services have not had a consistent approach to organization, naming, and API structure. Additionally, many developers have felt that the learning curve was difficult, and the APIs did not offer a good, approachable, and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services, a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created for all languages to drive a consistent experience with established API patterns for all services. A set of [Azure SDK Design Guidelines for Python](https://azure.github.io/azure-sdk/python_design.html) was also introduced to ensure that Python clients have a natural and idiomatic feel with respect to the Python ecosystem. Further details are available in the guidelines for those interested.

### Cross Service SDK improvements

The modern Event Grid client library also provides the ability to share in some of the cross-service improvements made to the Azure development experience, such as
- a unified logging and diagnostics pipeline offering a common view of the activities across each of the client libraries
- using the new [`azure-identity`](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md) library to share a single authentication approach between clients

## Important changes

### Support for Cloud Events

The v4.x major version comes with support for [CloudEvents](https://github.com/cloudevents/spec). Now the cloud native Cloud Events can be directly published using the `CloudEvent` constructor or as a dictionary as follows:

```Python
from azure.core.messaging import CloudEvent

cloud_event = CloudEvent(
    type="Contoso.Items.ItemReceived",
    source="/contoso/items",
    data={
        "itemSku": "Contoso Item SKU #1"
    },
    subject="Door1"
)

# as a dictionary

cloud_event = {
    "type":"a0517898-9fa4-4e70-b4a3-afda1dd68672",
    "source":"/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}",
    "data": {"hello": "world"},
    "subject": "Door1"
    }
```

### Client constructors

* The `EventGridClient` in the v1.3 has been replaced with `EventGridPublisherClient`.
* `EventGridPublisherClient` requires the full endpoint, which is typically in the format of `https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events`

| In v1.3 | Equivalent in v4.0 | Sample |
|---|---|---|
|`EventGridClient(credentials)`|`EventGridPublisherClient(endpoint, credential)`|[Sample for client construction](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py)|

### Publishing Events

The `publish_events` API is replaced with `send` in v4.0. Additionally, `send` API accepts `CloudEvent`, `EventGridEvent` along with their dict representations.

| In v1.3 | Equivalent in v4.0 | Sample |
|---|---|---|
|`EventGridClient(credentials).publish_events(topic_hostname, events)`|`EventGridPublisherClient(endpoint, credential).send(events)`|[Sample for client construction](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py)|

### Consuming Events

The v4.x major version supports deserializing dictionaries into strongly typed objects. The `from_dict` methods in the `CloudEvent` and `EventGridEvent` models can be used for the same.

This example consumes a payload message received from ServiceBus and deserializes it to an EventGridEvent object.

```Python
from azure.eventgrid import EventGridEvent
from azure.servicebus import ServiceBusClient
import os
import json

# all types of EventGridEvents below produce same DeserializedEvent
connection_str = os.environ['SERVICE_BUS_CONN_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connection_str) as sb_client:
    payload =  sb_client.get_queue_receiver(queue_name).receive_messages()

    ## deserialize payload into a list of typed Events
    events = [EventGridEvent.from_dict(json.loads(next(msg.body).decode('utf-8'))) for msg in payload]
```

## Additional samples

More examples can be found at [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/samples)
