# Azure Cognitive Services Health Insights Radiology Insights client library for Python
[Health Insights][health_insights] is an Azure Applied AI Service built with the Azure Cognitive Services Framework, that leverages multiple Cognitive Services, Healthcare API services and other Azure resources.

[Radiology Insights][radiology_insights_docs] is a model that aims to provide quality checks as feedback on errors and inconsistencies (mismatches) and ensures critical findings are identified and communicated using the full context of the report. Follow-up recommendations and clinical findings with measurements (sizes) documented by the radiologist are also identified.

## Getting started

### Prequisites

- [Python 3.8+][python] is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Cognitive Services Health Insights instance.

For more information about creating the resource or how to get the location and sku information see [here][cognitive_resource_cli].

### Installing the module

```bash
python -m pip install azure-healthinsights-radiologyinsights
```
This table shows the relationship between SDK versions and supported API versions of the service:

| SDK version | Supported API version of service |
|-------------|----------------------------------|
| 1.0.0b1     | 2023-09-01-preview               |


### Authenticate the client

#### Get the endpoint

You can find the endpoint for your Health Insights service resource using the [Azure Portal][azure_portal] or [Azure CLI][azure_cli]


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

#### Create a RadiologyInsightsClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of **AzureKeyCredential**. Use the key as the credential parameter to authenticate the client:

<!-- SNIPPET:sample_critical_result_inference_async.create_radiology_insights_client-->
```Python 
import os
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.radiologyinsights import RadiologyInsightsClient

KEY = os.environ["AZURE_HEALTH_INSIGHTS_API_KEY"]
ENDPOINT = os.environ["AZURE_HEALTH_INSIGHTS_ENDPOINT"]

radiology_insights_client = RadiologyInsightsClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
```
<!-- SNIPPET:sample_critical_result_inference_async.create_radiology_insights_client-->

### Long-Running Operations

Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that support healthcare analysis, custom text analysis, or multiple analyses are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns a poller object. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Key concepts

Once you've initialized a 'RadiologyInsightsClient', you can use it to analyse document text by displaying inferences found within the text.
* Age Mismatch
* Laterality Discrepancy
* Sex Mismatch
* Complete Order Discrepancy
* Limited Order Discrepancy
* Finding
* Critical Result
* Follow-up Recommendation
* Communication
* Radiology Procedure
Radiology Insights currently supports one document from one patient. Please take a look [here][inferences] for more detailed information about the inferences this service produces. 

## Examples

For each inference samples are available that show how to retrieve the information either in a synchronous (block until operation is complete, slower) or in an asynchronous way (non-blocking, faster).
For an example how to create a client, a request and get the result see the example in the [sample folder][sample_folder].

* [Age Mismatch](#get-age-mismatch-inference-information)
* [Complete Order Discrepancy](#get-complete-order-discrepancy-inference-information)
* [Critical Result](#get-critical-result-inference-information)
* [Finding](#get-finding-information)
* [Follow-up Communication](#get-follow-up-communication-information)
* [Follow-up Recommendation](#get-follow-up-recommendation-information)
* [Laterality Descripancy](#get-laterality-discrepancy-information)
* [Limited Order Descripancy](#get-limited-order-discrepancy-information)
* [Radiology Procedure](#get-radiology-procedure-information)
* [Sex Mismatch](#get-sex-mismatch-information)

### Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.

### Get Age Mismatch Inference information

<!-- SNIPPET:sample_age_mismatch_inference_async.display_age_mismatch-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.AGE_MISMATCH:
            print(f"Age Mismatch Inference found")
```
<!-- SNIPPET:sample_age_mismatch_inference_async.display_age_mismatch-->

### Get Complete Order Discrepancy Inference information

<!-- SNIPPET:sample_complete_order_discrespancy_inference_async.display_complete_order_discrepancy-->
```Python
for patient_result in radiology_insights_result.patient_results:
            for ri_inference in patient_result.inferences:
                if ri_inference.kind == models.RadiologyInsightsInferenceType.COMPLETE_ORDER_DISCREPANCY:
                    print(f"Complete Order Discrepancy Inference found")
```
<!-- SNIPPET:sample_complete_order_discrespancy_inference_async.display_complete_order_discrepancy-->

### Get Critical Result Inference information

<!-- SNIPPET:sample_critical_result_inference_async.display_critical_results-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.CRITICAL_RESULT:
            critical_result = ri_inference.result
                print(
                f"Critical Result Inference found: {critical_result.description}")
```
<!-- SNIPPET:sample_critical_result_inference_async.display_critical_results-->

### Get Finding Inference information

<!-- SNIPPET:sample_finding_inference_async.display_finding-->
```Python
for patient_result in radiology_insights_result.patient_results:
            counter = 0
            for ri_inference in patient_result.inferences:
                if ri_inference.kind == models.RadiologyInsightsInferenceType.FINDING:
                    counter += 1
                    print(f"Finding Inference found")
```
<!-- SNIPPET:sample_finding_inference_async.display_finding-->

### Get Follow-up Communication information

<!-- SNIPPET:sample_followup_communication_inference_async.display_followup_communication-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.FOLLOWUP_COMMUNICATION:
            print(f"Follow-up Communication Inference found")
```
<!-- SNIPPET:sample_followup_communication_inference_async.display_followup_communication-->

### Get Follow-up Recommendation information

<!-- SNIPPET:sample_followup_recommendation_inference_async.display_followup_recommendation-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.FOLLOWUP_RECOMMENDATION:
            print(f"Follow-up Recommendation Inference found") 
```
<!-- SNIPPET:sample_followup_recommendation_inference_async.display_followup_recommendation-->

### Get Laterality Discrepancy information

<!-- SNIPPET:sample_laterality_discrepancy_inference_async.display_laterality_discrepancy-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.LATERALITY_DISCREPANCY:
            print(f"Laterality Discrepancy Inference found")
```
<!-- SNIPPET:sample_laterality_discrepancy_inference_async.display_laterality_discrepancy-->

### Get Limited Order Discrepancy information

<!-- SNIPPET:sample_limited_order_discrepancy_inference_async.display_limited_order_discrepancy-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.LIMITED_ORDER_DISCREPANCY:
            print(f"Limited Order Discrepancy Inference found")
```
<!-- SNIPPET:sample_limited_order_discrepancy_inference_async.display_limited_order_discrepancy-->

### Get Radiology Procedure information

<!-- SNIPPET:sample_radiology_procedure_inference_async.display_radiology_procedure-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.RADIOLOGY_PROCEDURE:
            print(f"Radiology Procedure Inference found")
```
<!-- SNIPPET:sample_radiology_procedure_inference_async.display_radiology_procedure-->

### Get Sex Mismatch information

<!-- SNIPPET:sample_sex_mismatch_inference_async.display_sex_mismatch-->
```Python
for patient_result in radiology_insights_result.patient_results:
    for ri_inference in patient_result.inferences:
        if ri_inference.kind == models.RadiologyInsightsInferenceType.SEX_MISMATCH:
            print(f"Sex Mismatch Inference found")
```
<!-- SNIPPET:sample_sex_mismatch_inference_async.display_sex_mismatch-->

For detailed conceptual information of this and other inferences please read more [here][inferences].

## Troubleshooting

### General

Health Insights Radiology Insights client library will raise exceptions defined in [Azure Core][azure_core].

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here](https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging).

## Next steps

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact <opencode@microsoft.com> with any
additional questions or comments.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com
[health_insights]: https://learn.microsoft.com/azure/azure-health-insights/overview
[radiology_insights_docs]: https://learn.microsoft.com/azure/azure-health-insights/radiology-insights/
[azure_sub]: https://azure.microsoft.com/free/
[cognitive_resource_cli]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli
[azure_portal]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesHealthInsights
[azure_cli]: https://learn.microsoft.com/cli/azure/
[inferences]: https://learn.microsoft.com/azure/azure-health-insights/radiology-insights/inferences
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[python]: https://www.python.org/downloads/
[sample_folder]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthinsights/azure-healthinsights-radiologyinsights/samples