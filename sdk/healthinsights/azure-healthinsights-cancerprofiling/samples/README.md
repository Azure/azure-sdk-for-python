---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-health-insights
urlFragment: healthinsights-cancerprofiling-samples
---

# Samples for Health Insights Cancer Profiling client library for Python

These code samples show common scenario operations with the Health Insights Cancer Profiling client library.

These sample programs show common scenarios for the Health Insights Cancer Profiling client's offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_infer_cancer_profiling.py][sample_infer_cancer_profiling] and [sample_infer_cancer_profiling_async.py][sample_infer_cancer_profiling_async]|Infer cancer profiling.|

## Prerequisites
* Python 3.7 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and an [Azure Health Insights account][azure_healthinsights_account] to run these samples.

## Setup

1. Install the Azure Health Insights Cancer Profiling client library for Python with [pip][pip]:

```bash
pip install azure-healthinsights-cancerprofiling
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_infer_cancer_profiling.py`

## Next steps

Check out the [API reference documentation][python-fr-ref-docs] to learn more about
what you can do with the Health Insights client library.

[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/cognitive-services
[azure_healthinsights_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[sample_infer_cancer_profiling]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-cancerprofiling/samples/sample_infer_cancer_profiling.py
[sample_infer_cancer_profiling_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-cancerprofiling/samples/async_samples/sample_infer_cancer_profiling_async.py

