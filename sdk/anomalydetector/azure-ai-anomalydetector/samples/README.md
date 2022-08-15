---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-anomaly-detector
urlFragment: anomalydetector-samples
---

# Samples for Azure Anomaly Detector client library for Python

These code samples show common scenario operations with the Anomaly Detector client library.

These sample programs show common scenarios for the Anomaly Detector client's offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_detect_entire_series_anomaly.py][sample_detect_entire_series_anomaly] |Detecting anomalies in the entire time series.|
|[sample_detect_last_point_anomaly.py][sample_detect_last_point_anomaly] |Detecting the anomaly status of the latest data point.|
|[sample_detect_change_point.py][sample_detect_change_point] |Detecting change points in the entire time series.|
|[sample_multivariate_detect.py][sample_multivariate_detect] |Detecting anomalies in the multivariate time series.|

## Prerequisites
* Python 2.7 or 3.5 or higher is required to use this package.
* The Pandas data analysis library.
* You must have an [Azure subscription][azure_subscription] and an
[Azure Anomaly Detector account][azure_anomaly_detector_account] to run these samples.

## Setup

1. Install the Azure Anomaly Detector client library for Python with [pip][pip]:

```bash
pip install azure-ai-anomalydetector
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_detect_entire_series_anomaly.py`

## Next steps

Check out the [API reference documentation][python-fr-ref-docs] to learn more about
what you can do with the Azure Anomaly Detector client library.

[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/cognitive-services
[azure_anomaly_detector_account]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesAnomalyDetector
[python-fr-ref-docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-cognitiveservices-anomalydetector/0.3.0/index.html

[sample_detect_entire_series_anomaly]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_detect_entire_series_anomaly.py
[sample_detect_last_point_anomaly]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_detect_last_point_anomaly.py
[sample_detect_change_point]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_detect_change_point.py
[sample_multivariate_detect]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_multivariate_detect.py