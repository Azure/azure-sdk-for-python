---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
urlFragment: metricsadvisor-samples
---

# Samples for Azure Metrics Advisor client library for Python

These code samples show common scenario operations with the Azure Metrics Advisor client library.
The async versions of the samples require Python 3.5 or later.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async]|Authenticate the clients|
|[sample_data_feeds.py][sample_data_feeds] and [sample_data_feeds_async.py][sample_data_feeds_async]|Create, list, get, update, and delete data feeds|
|[sample_ingestion.py][sample_ingestion] and [sample_ingestion_async.py][sample_ingestion_async]|Check on the data feed ingestion progress, list ingestion statuses, and refresh data feed ingestion|
|[sample_anomaly_detection_configuration.py][sample_anomaly_detection_configuration] and [sample_anomaly_detection_configuration_async.py][sample_anomaly_detection_configuration_async]|Create, list, get, update, and delete anomaly detection configurations|
|[sample_anomaly_alert_configuration.py][sample_anomaly_alert_configuration] and [sample_anomaly_alert_configuration_async.py][sample_anomaly_alert_configuration_async]|Create, list, get, update, and delete anomaly alert configurations. Also list alerts and anomalies for a specific alert configuration.|
|[sample_hooks.py][sample_hooks] and [sample_hooks_async.py][sample_hooks_async]|Create, list, get, update, and delete notification hooks|
|[sample_feedback.py][sample_feedback] and [sample_feedback_async.py][sample_feedback_async]|Add, get, and list feedback for the anomaly detection result|
|[sample_queries.py][sample_queries] and [sample_queries_async.py][sample_queries_async]|Query dimensions/data/status/etc.|


## Prerequisites
* Python 2.7, or 3.5 or later is required to use this package (3.5 or later if using asyncio)
* You must have an [Azure subscription][azure_subscription] and an
[Azure Metrics Advisor account][portal_metrics_advisor_account] to run these samples.

## Setup

1. Install the Azure Metrics Advisor client library for Python with [pip][pip]:

```bash
pip install azure-ai-metricsadvisor --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_data_feeds.py`

## Next steps

Check out the [reference documentation][reference_documentation] to learn more about
what you can do with the Azure Metrics Advisor client library.

[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[portal_metrics_advisor_account]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesMetricsAdvisor
[reference_documentation]: https://aka.ms/azsdk/python/metricsadvisor/docs

[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_authentication_async.py
[sample_data_feeds]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_data_feeds.py
[sample_data_feeds_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_data_feeds_async.py
[sample_ingestion]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_ingestion.py
[sample_ingestion_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_ingestion_async.py
[sample_anomaly_detection_configuration]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_detection_configuration.py
[sample_anomaly_detection_configuration_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_detection_configuration_async.py
[sample_anomaly_alert_configuration]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_alert_configuration.py
[sample_anomaly_alert_configuration_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_alert_configuration_async.py
[sample_hooks]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_hooks.py
[sample_hooks_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_hooks_async.py
[sample_feedback]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_feedback.py
[sample_feedback_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_feedback_async.py
[sample_queries]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/sample_queries.py
[sample_queries_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/metricsadvisor/azure-ai-metricsadvisor/samples/async_samples/sample_queries_async.py
