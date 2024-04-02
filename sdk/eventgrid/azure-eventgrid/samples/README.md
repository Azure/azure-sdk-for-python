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

## Namespace Sync samples
These code samples show common champion scenario operations with the Azure Event Grid client library.

* Authenticate the client: [sample_authentication.py][python-eg-auth]
* Publish events to a namespace topic:[sample_publish_operation.py][python-eg-client-publish-sample]
* Publish events in binary mode to a namespace topic: [sample_binary_mode.py][python-eg-client-binary-mode-sample]
* Receive events from a namespace topic: [sample_receive_operation.py][python-eg-client-receive-sample]
* Acknowledge events from a namespace topic: [sample_acknowledge_operation.py][python-eg-client-ack-sample]
* Release events from a namespace topic: [sample_release_operation.py][python-eg-client-release-sample]
* Reject events from a namespace topic: [sample_reject_operation.py][python-eg-client-reject-sample]
* Renew locks: [sample_renew_locks_operation.py][python-eg-client-renew-locks-sample]

## Namespace Async samples

* Publish events to a namespace topic:[sample_publish_operation_async.py][python-eg-client-publish-sample-async]
* Publish events in binary mode to a namespace topic: [sample_binary_mode_async.py][python-eg-client-binary-mode-sample-async]
* Receive events from a namespace topic: [sample_receive_operation_async.py][python-eg-client-receive-sample-async]
* Acknowledge events from a namespace topic: [sample_acknowledge_operation_async.py][python-eg-client-ack-sample-async]
* Release events from a namespace topic: [sample_release_operation_async.py][python-eg-client-release-sample-async]
* Reject events from a namespace topic: [sample_reject_operation_async.py][python-eg-client-reject-sample-async]
* Renew locks: [sample_renew_locks_operation_async.py][python-eg-client-renew-locks-sample-async]


## Basic Sync samples
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

## Basic Async samples
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

[python-eg-client-sync-samples]: https://github.com/Azure/azure-sdk-for-python/tree/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples
[python-eg-client-async-samples]:https://github.com/Azure/azure-sdk-for-python/tree/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples

[python-eg-client-ack-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_acknowledge_operation.py

[python-eg-client-all-ops-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_all_operations.py

[python-eg-client-binary-mode-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_binary_mode.py

[python-eg-client-publish-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_publish_operation.py

[python-eg-client-receive-renew-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_publish_receive_renew.py

[python-eg-client-release-receive-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_publish_release_receive.py

[python-eg-client-receive-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_receive_operation.py

[python-eg-client-release-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_release_operation.py


[python-eg-client-reject-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_reject_operation.py

[python-eg-client-renew-locks-sample]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/sync_samples/eventgrid_client_samples/sample_renew_locks_operation.py


[python-eg-client-ack-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_acknowledge_operation_async.py

[python-eg-client-all-ops-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_all_operations_async.py

[python-eg-client-binary-mode-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_binary_mode_async.py

[python-eg-client-publish-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_publish_operation_async.py

[python-eg-client-receive-renew-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_publish_receive_renew_async.py

[python-eg-client-release-receive-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_publish_release_receive_async.py

[python-eg-client-receive-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_receive_operation_async.py

[python-eg-client-release-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_release_operation_async.py


[python-eg-client-reject-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_reject_operation_async.py

[python-eg-client-renew-locks-sample-async]:https://github.com/Azure/azure-sdk-for-python/blob/feature/eventgrid/sdk/eventgrid/azure-eventgrid/samples/async_samples/eventgrid_client_samples/sample_renew_locks_operation_async.py