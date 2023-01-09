# Cognitive Services Anomaly Detector client library for Python

[Anomaly Detector](https://learn.microsoft.com/azure/cognitive-services/Anomaly-Detector/overview) is an AI service with a set of APIs, which enables you to monitor and detect anomalies in your time series data with little machine learning (ML) knowledge, either batch validation or real-time inference.

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Cognitive Services Anomaly Detector instance.

### Install the package

```bash
python -m pip install azure-ai-anomalydetector
```

> Note: This version of the client library defaults to the `3.0.0b6` version of the service.

This table shows the relationship between SDK versions and supported API versions of the service:

|SDK version|Supported API version of service |
|-------------|---------------|
|3.0.0b6 | 1.1|
|3.0.0b4, 3.0.0b5| 1.1-preview-1|
|3.0.0b3 | 1.1-preview|
|3.0.0b1, 3.0.0b2  | 1.0 |

### Authenticate the client

#### Get the endpoint

You can find the endpoint for your Anomaly Detector service resource using the
[Azure Portal](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesAnomalyDetector)
or [Azure CLI](https://learn.microsoft.com/cli/azure/):

```bash
# Get the endpoint for the Anomaly Detector service resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

#### Get the API Key

You can get the **API Key** from the Anomaly Detector service resource in the Azure Portal.
Alternatively, you can use **Azure CLI** snippet below to get the API key of your resource.

```PowerShell
az cognitiveservices account keys list --resource-group <your-resource-group-name> --name <your-resource-name>
```

#### Create a AnomalyDetectorClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of **AzureKeyCredential**. Use the key as the credential parameter
to authenticate the client:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector import AnomalyDetectorClient

credential = AzureKeyCredential("<api_key>")
client = AnomalyDetectorClient(endpoint="https://<resource-name>.cognitiveservices.azure.com/", credential=credential)
```

## Key concepts

With the Anomaly Detector, you can either detect anomalies in one variable using **Univariate Anomaly Detection**, or detect anomalies in multiple variables with **Multivariate Anomaly Detection**.

|Feature  |Description  |
|---------|---------|
|Univariate Anomaly Detection | Detect anomalies in one variable, like revenue, cost, etc. The model was selected automatically based on your data pattern. |
|Multivariate Anomaly Detection| Detect anomalies in multiple variables with correlations, which are usually gathered from equipment or other complex system. The underlying model used is Graph attention network.|

### Univariate Anomaly Detection

The Univariate Anomaly Detection API enables you to monitor and detect abnormalities in your time series data without having to know machine learning. The algorithms adapt by automatically identifying and applying the best-fitting models to your data, regardless of industry, scenario, or data volume. Using your time series data, the API determines boundaries for anomaly detection, expected values, and which data points are anomalies.

Using the Anomaly Detector doesn't require any prior experience in machine learning, and the REST API enables you to easily integrate the service into your applications and processes.

With the Univariate Anomaly Detection, you can automatically detect anomalies throughout your time series data, or as they occur in real-time.

|Feature  |Description  |
|---------|---------|
| Streaming detection| Detect anomalies in your streaming data by using previously seen data points to determine if your latest one is an anomaly. This operation generates a model using the data points you send, and determines if the target point is an anomaly. By calling the API with each new data point you generate, you can monitor your data as it's created. |
| Batch detection | Use your time series to detect any anomalies that might exist throughout your data. This operation generates a model using your entire time series data, with each point analyzed with the same model.         |
| Change points detection | Use your time series to detect any trend change points that exist in your data. This operation generates a model using your entire time series data, with each point analyzed with the same model.    |

### Multivariate Anomaly Detection

The **Multivariate Anomaly Detection** APIs further enable developers by easily integrating advanced AI for detecting anomalies from groups of metrics, without the need for machine learning knowledge or labeled data. Dependencies and inter-correlations between up to 300 different signals are now automatically counted as key factors. This new capability helps you to proactively protect your complex systems such as software applications, servers, factory machines, spacecraft, or even your business, from failures.

With the Multivariate Anomaly Detection, you can automatically detect anomalies throughout your time series data, or as they occur in real-time. There are three processes to use Multivariate Anomaly Detection.

- **Training**: Use Train Model API to create and train a model, then use Get Model Status API to get the status and model metadata.
- **Inference**:
  - Use Async Inference API to trigger an asynchronous inference process and use Get Inference results API to get detection results on a batch of data.
  - You could also use Sync Inference API to trigger a detection on one timestamp every time.
- **Other operations**: List Model API and Delete Model API are supported in Multivariate Anomaly Detection model for model management.

### Thread safety

We guarantee that all client instance methods are thread-safe and independent of each other ([guideline](https://azure.github.io/azure-sdk/dotnet_introduction.html#dotnet-service-methods-thread-safety)). This ensures that the recommendation of reusing client instances is always safe, even across threads.

## Examples

The following section provides several code snippets covering some of the most common Anomaly Detector service tasks, including:

- [Univariate Anomaly Detection - Batch detection](#batch-detection)
- [Univariate Anomaly Detection - Streaming detection](#streaming-detection)
- [Univariate Anomaly Detection - Detect change points](#detect-change-points)
- [Multivariate Anomaly Detection](#multivariate-anomaly-detection-sample)

### Batch detection

```python
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *


SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]
TIME_SERIES_DATA_PATH = os.path.join("sample_data", "request-data.csv")
client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

series = []
data_file = pd.read_csv(TIME_SERIES_DATA_PATH, header=None, encoding="utf-8", parse_dates=[0])
for index, row in data_file.iterrows():
    series.append(TimeSeriesPoint(timestamp=row[0], value=row[1]))

request = UnivariateDetectionOptions(
    series=series,
    granularity=TimeGranularity.DAILY,
)


if any(response.is_anomaly):
    print("An anomaly was detected at index:")
    for i, value in enumerate(response.is_anomaly):
        if value:
            print(i)
else:
    print("No anomalies were detected in the time series.")

```

### Streaming Detection

```python
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *


SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]
TIME_SERIES_DATA_PATH = os.path.join("sample_data", "request-data.csv")
client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

series = []
data_file = pd.read_csv(TIME_SERIES_DATA_PATH, header=None, encoding="utf-8", parse_dates=[0])
for index, row in data_file.iterrows():
    series.append(TimeSeriesPoint(timestamp=row[0], value=row[1]))

request = UnivariateDetectionOptions(
    series=series,
    granularity=TimeGranularity.DAILY,
)
print("Detecting the anomaly status of the latest data point.")

if response.is_anomaly:
    print("The latest point is detected as anomaly.")
else:
    print("The latest point is not detected as anomaly.")
```

### Detect change points

```python
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *


SUBSCRIPTION_KEY = os.environ["ANOMALY_DETECTOR_KEY"]
ANOMALY_DETECTOR_ENDPOINT = os.environ["ANOMALY_DETECTOR_ENDPOINT"]
TIME_SERIES_DATA_PATH = os.path.join("sample_data", "request-data.csv")
client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

series = []
data_file = pd.read_csv(TIME_SERIES_DATA_PATH, header=None, encoding="utf-8", parse_dates=[0])
for index, row in data_file.iterrows():
    series.append(TimeSeriesPoint(timestamp=row[0], value=row[1]))

request = UnivariateChangePointDetectionOptions(
    series=series,
    granularity=TimeGranularity.DAILY,
)


if any(response.is_change_point):
    print("An change point was detected at index:")
    for i, value in enumerate(response.is_change_point):
        if value:
            print(i)
else:
    print("No change point were detected in the time series.")

```

### Multivariate Anomaly Detection Sample

To see how to use Anomaly Detector library to conduct Multivariate Anomaly Detection, see this [sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_multivariate_detect.py).

To get more details of Anomaly Detector package, refer to this [azure.ai.anomalydetector package](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-anomalydetector/latest/azure.ai.anomalydetector.html#).

## Troubleshooting

### General

Anomaly Detector client library will raise exceptions defined in [Azure Core](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html#module-azure.core.exceptions).

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here](https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging).

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html) describes available configurations for retries, logging, transport protocols, and more.

## Next steps

These code samples show common scenario operations with the Azure Anomaly Detector library. More samples can be found under the [samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/) directory.

- Univariate Anomaly Detection - Batch Detection: [sample_detect_entire_series_anomaly.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_detect_entire_series_anomaly.py)

- Univariate Anomaly Detection - Streaming Detection: [sample_detect_last_point_anomaly.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_detect_last_point_anomaly.py)

- Univariate Anomaly Detection - Change Point Detection: [sample_detect_change_point.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_detect_change_point.py)

- Multivariate Anomaly Detection: [sample_multivariate_detect.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/anomalydetector/azure-ai-anomalydetector/samples/sample_multivariate_detect.py)

### Additional documentation

For more extensive documentation on Azure Anomaly Detector, see the [Anomaly Detector documentation](https://learn.microsoft.com/azure/cognitive-services/anomaly-detector/overview) on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [CLA homepage](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/
