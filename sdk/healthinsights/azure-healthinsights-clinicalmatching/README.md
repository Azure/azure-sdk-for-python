# Azure Cognitive Services Health Insights Clinical Matching client library for Python
Remove comment
<!--
[Health Insights](https://review.learn.microsoft.com/en-us/azure/cognitive-services/health-decision-support/overview?branch=main) is an Azure Applied AI Service built with the Azure Cognitive Services Framework, that leverages multiple Cognitive Services, Healthcare API services and other Azure resources.
The [Clinical Matching model](https://review.learn.microsoft.com/en-us/azure/cognitive-services/health-decision-support/trial-matcher/overview?branch=main) receives patients data and clinical trials protocols, and provides relevant clinical trials based on eligibility criteria.
-->

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Cognitive Services Health Insights instance.


### Install the package

```bash
python -m pip install azure-healthinsights-clinicalmatching
```

This table shows the relationship between SDK versions and supported API versions of the service:

|SDK version|Supported API version of service |
|-------------|---------------|
|1.0.0b1 | 2023-03-01-preview|


### Authenticate the client

#### Get the endpoint

You can find the endpoint for your Health Insights service resource using the
***[Azure Portal](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesHealthInsights)
or [Azure CLI](https://learn.microsoft.com/cli/azure/):

```bash
# Get the endpoint for the Health Insights service resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

#### Get the API Key

You can get the **API Key** from the Health Insights service resource in the Azure Portal.
Alternatively, you can use **Azure CLI** snippet below to get the API key of your resource.

```PowerShell
az cognitiveservices account keys list --resource-group <your-resource-group-name> --name <your-resource-name>
```

#### Create a CancerProfilingClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of **AzureKeyCredential**. Use the key as the credential parameter
to authenticate the client:

```python
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching import ClinicalMatchingClient

credential = AzureKeyCredential("<api_key>")
client = ClinicalMatchingClient(endpoint="https://<resource-name>.cognitiveservices.azure.com/", credential=credential)
```

### Long-Running Operations

Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that support healthcare analysis, custom text analysis, or multiple analyses are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns a poller object. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Key concepts

Trial Matcher provides the user of the services two main modes of operation: patients centric and clinical trial centric.
- On patient centric mode, the Trial Matcher model bases the patient matching on the clinical condition, location, priorities, eligibility criteria, and other criteria that the patient and/or service users may choose to prioritize. The model helps narrow down and prioritize the set of relevant clinical trials to a smaller set of trials to start with, that the specific patient appears to be qualified for.
- On clinical trial centric, the Trial Matcher is finding a group of patients potentially eligible to a clinical trial. The Trial Matcher narrows down the patients, first filtered on clinical condition and selected clinical observations, and then focuses on those patients who met the baseline criteria, to find the group of patients that appears to be eligible patients to a trial.

## Examples

- [Match Trials - Find potential eligible trials for a patient](#match-trials)

### Match trials

Finding potential eligible trials for a patient.

```python
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching import ClinicalMatchingClient

KEY = os.environ["HEALTHINSIGHTS_KEY"]
ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]
TIME_SERIES_DATA_PATH = os.path.join("sample_data", "request-data.csv")
client = ClinicalMatchingClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))

poller = client.begin_match_trials(data)
response = poller.result()

if response.status == JobStatus.SUCCEEDED:
    results = response.results
    for patient_result in results.patients:
        print(f"Inferences of Patient {patient_result.id}")
        for tm_inferences in patient_result.inferences:
            print(f"Trial Id {tm_inferences.id}")
            print(f"Type: {str(tm_inferences.type)}  Value: {tm_inferences.value}")
            print(f"Description {tm_inferences.description}")
else:
    errors = response.errors
    if errors is not None:
        for error in errors:
            print(f"{error.code} : {error.message}")

```

## Troubleshooting

### General

Health Insights Clinical Matching client library will raise exceptions defined in [Azure Core](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html#module-azure.core.exceptions).

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
<!--
This code sample show common scenario operation with the Azure Health Insights Clinical Matching library. More samples can be found under the [samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/samples/) directory.

- Match Trials FHIR: [sample_match_trials_fhir.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/samples/sample_match_trials_fhir.py)

- Match Trials Structured Coded Elements: [sample_match_trials_structured_coded_elements.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/samples/sample_match_trials_structured_coded_elements.py)

- Match Trials Structured Coded Elements Sync: [sample_match_trials_structured_coded_elements_sync.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/samples/sample_match_trials_structured_coded_elements_sync.py)

- Match Trials Unstructured Clinical Note: [sample_match_trials_unstructured_clinical_note.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/samples/sample_match_trials_unstructured_clinical_note.py)
-->
### Additional documentation
<!--
For more extensive documentation on Azure Health Insights Clinical Matching, see the [Clinical Matching documentation](https://review.learn.microsoft.com/en-us/azure/cognitive-services/health-decision-support/trial-matcher/?branch=main) on docs.microsoft.com.
-->

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/