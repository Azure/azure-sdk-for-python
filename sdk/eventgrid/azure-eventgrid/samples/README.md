---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-event-grid
urlFragment: eventgrid-samples
---

# Azure Event Grid Client Library Python Samples

## Sync samples
These code samples show common champion scenario operations with the Azure Event Grid client library.

* Generate Shared Access Signature: [sample_generate_sas.py][python-eg-generate-sas]

* Authenticate the client: [sample_authentication.py][python-eg-auth]

* Publish events to a topic using SAS: [sample_publish_events_to_a_topic_using_sas_credential_async.py][python-eg-sample-send-using-sas]
* Publish Event Grid Events to a topic: [sample_publish_eg_events_to_a_topic.py][python-eg-sample-eg-event]
* Publish EventGrid Events to a domain topic: [sample_publish_eg_events_to_a_domain_topic.py][python-eg-sample-eg-event-to-domain]
* Publish a Cloud Event: [sample_publish_events_using_cloud_events_1.0_schema.py][python-eg-sample-send-cloudevent]
* Publish a Custom Schema: [sample_publish_custom_schema_to_a_topic.py][python-eg-publish-custom-schema]

To publish events, dict representation of the models could also be used as follows:
* Publish EventGridEvent as dict like representation: [sample_publish_eg_event_using_dict.py][python-eg-sample-send-eg-as-dict]
* Publish CloudEvent as dict like representation: [sample_publish_cloud_event_using_dict.py][python-eg-sample-send-cloudevent-as-dict]

* Consume a Custom Payload of raw cloudevent data: [sample_consume_custom_payload.py][python-eg-sample-consume-custom-payload]

## Async samples
These code samples show common champion scenario operations with the Azure Event Grid client library using the async client.

* Authenticate the client: [sample_authentication_async.py][python-eg-auth-async]

* Publish events to a topic using SAS: [sample_publish_events_to_a_topic_using_sas_credential_async.py][python-eg-sample-send-using-sas-async]
* Publish EventGrid Events to a topic: [sample_publish_eg_events_to_a_topic_async.py][python-eg-sample-eg-event-async]
* Publish EventGrid Events to a domain topic: [sample_publish_eg_events_to_a_domain_topic_async.py][python-eg-sample-eg-event-to-domain-async]
* Publish a Cloud Event: [sample_publish_events_using_cloud_events_1.0_schema_async.py][python-eg-sample-send-cloudevent-async]
* Publish a Custom Schema: [sample_publish_custom_schema_to_a_topic_async.py][python-eg-publish-custom-schema-async]

To publish events, dict representation of the models could also be used as follows:
* Publish EventGridEvent as dict like representation: [sample_publish_eg_event_using_dict_async.py][python-eg-sample-send-eg-as-dict-async]
* Publish CloudEvent as dict like representation: [sample_publish_cloud_event_using_dict_async.py][python-eg-sample-send-cloudevent-as-dict-async]

## More Samples

* More samples related to the send scenario can be seen [here][python-eg-publish-samples].
* To see more samples related to consuming a payload from different messaging services as a typed object, please visit [Consume Samples][python-eg-consume-samples]

[python-eg-auth]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_authentication.py
[python-eg-generate-sas]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_generate_sas.py
[python-eg-sample-send-using-sas]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_to_a_topic_using_sas_credential.py
[python-eg-sample-eg-event]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_events_to_a_topic.py
[python-eg-sample-eg-event-to-domain]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_events_to_a_domain.py
[python-eg-sample-send-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py
[python-eg-publish-custom-schema]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_custom_schema_to_a_topic.py
[python-eg-sample-send-eg-as-dict]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_event_using_dict.py
[python-eg-sample-send-cloudevent-as-dict]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_cloud_event_using_dict.py

[python-eg-auth-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_authentication_async.py
[python-eg-sample-send-using-sas-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_events_to_a_topic_using_sas_credential_async.py
[python-eg-sample-eg-event-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_eg_events_to_a_topic_async.py
[python-eg-sample-eg-event-to-domain-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_eg_events_to_a_domain_async.py
[python-eg-sample-send-cloudevent-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_events_using_cloud_events_1.0_schema_async.py
[python-eg-publish-custom-schema-async]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_custom_schema_to_a_topic_async.py
[python-eg-sample-send-eg-as-dict-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_eg_event_using_dict_async.py
[python-eg-sample-send-cloudevent-as-dict-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_cloud_event_using_dict_async.py

[python-eg-publish-samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/publish_samples
[python-eg-consume-samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/consume_samples

[python-eg-sample-consume-custom-payload]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_consume_custom_payload.py

[publisher-service-doc]: https://docs.microsoft.com/azure/event-grid/concepts
