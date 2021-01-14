---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-eventgrid
urlFragment: azure-eventgrid-samples
---

# Azure Event Grid Client Library Python Samples

These code samples show common champion scenario operations with the Azure Event Grid client library.
Both [sync version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub/samples/sync_samples) and [async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhub/samples/async_samples) of publish samples are provided, async samples require Python 3.5 or later. Only the sync versions of consume samples are provided, since the EventGridConsumer does not interact with the service and does not provide asynchronous support.

* [cs1_publish_custom_events_to_a_topic.py][python-eg-sample-customevent] ([async_version][python-eg-sample-customevent-async]) - Publishes Event Grid Events to a custom topic.
* [cs1b_publish_custom_events_to_a_topic_with_signature.py][python-eg-sample-customevent-signature] ([async_version][python-eg-sample-customevent-signature-async]) - Publishes Event Grid Events to a custom topic using a shared access signature for authentication.
* [cs2_publish_custom_events_to_a_domain_topic.py][python-eg-sample-customevent-to-domain] ([async_version][python-eg-sample-customevent-to-domain-async]) - Publishes Event Grid Events to domain topics.
* [cs3_consume_system_events.py][python-eg-sample-consume-systemevent] - Deserializes a System Event.
* [cs4_consume_custom_events.py][python-eg-sample-consume-customevent] - Deserializes a custom Event Grid Event.
* [cs5_publish_events_using_cloud_events_1.0_schema.py][python-eg-sample-send-cloudevent] ([async_version][python-eg-sample-send-cloudevent-async]) - Publishes Cloud Events to a custom topic.
* [cs6_consume_events_using_cloud_events_1.0_schema.py][python-eg-sample-consume-cloudevent] -  Deserializes a Cloud Event.

[python-eg-sample-customevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs1_publish_custom_events_to_a_topic.py
[python-eg-sample-customevent-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/champion_scenarios/cs1_publish_custom_events_to_a_topic_async.py
[python-eg-sample-customevent-signature]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs1b_publish_custom_events_to_a_topic_with_signature.py
[python-eg-sample-customevent-signature-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/champion_scenarios/cs1b_publish_custom_events_to_a_topic_with_signature_async.py
[python-eg-sample-customevent-to-domain]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs2_publish_custom_events_to_a_domain_topic.py
[python-eg-sample-customevent-to-domain-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/champion_scenarios/cs2_publish_custom_events_to_a_domain_topic_async.py
[python-eg-sample-consume-systemevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs3_consume_system_events.py
[python-eg-sample-consume-customevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs4_consume_custom_events.py
[python-eg-sample-send-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs5_publish_events_using_cloud_events_1.0_schema.py
[python-eg-sample-send-cloudevent-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/champion_scenarios/cs5_publish_events_using_cloud_events_1.0_schema_async.py
[python-eg-sample-consume-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/champion_scenarios/cs6_consume_events_using_cloud_events_1.0_schema.py
[publisher-service-doc]: https://docs.microsoft.com/azure/event-grid/concepts
