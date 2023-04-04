# Azure Cognitive Services Health Insights Clinical Matching client library for Python

[Health Insights](https://review.learn.microsoft.com/azure/azure-health-insights/?branch=release-azure-health-insights) is an Azure Applied AI Service built with the Azure Cognitive Services Framework, that leverages multiple Cognitive Services, Healthcare API services and other Azure resources.
The [Clinical Matching model][clinical_matching_docs] receives patients data and clinical trials protocols, and provides relevant clinical trials based on eligibility criteria.

[Source code][hi_source_code] | [Package (PyPI)][hi_pypi] | [API reference documentation][clinical_matching_api_documentation] | [Product documentation][product_docs] | [Samples][hi_samples]

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Cognitive Services Health Insights instance.


### Install the package

```bash
pip install azure-healthinsights-clinicalmatching
```

This table shows the relationship between SDK versions and supported API versions of the service:

| SDK version | Supported API version of service |
|-------------|----------------------------------|
| 1.0.0b1     | 2023-03-01-preview               |


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

#### Create a ClinicalMatchingClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of **AzureKeyCredential**. Use the key as the credential parameter to authenticate the client:

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching import ClinicalMatchingClient

KEY = os.environ["HEALTHINSIGHTS_KEY"]
ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]

trial_matcher_client = ClinicalMatchingClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
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

The following section provides several code snippets covering some of the most common Health Insights - Clinical Matching service tasks, including:

- [Match trials](#match-trials "Match trials")

### Match trials

Finding potential eligible trials for a patient.

```python
import os
import datetime
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.clinicalmatching import ClinicalMatchingClient, models

KEY = os.environ["HEALTHINSIGHTS_KEY"]
ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]

# Create a Trial Matcher client
# <client>
trial_matcher_client = ClinicalMatchingClient(endpoint=ENDPOINT,
                                              credential=AzureKeyCredential(KEY))
# </client>

# Create clinical info list
# <clinicalInfo>
clinical_info_list = [models.ClinicalCodedElement(system="http://www.nlm.nih.gov/research/umls",
                                                  code="C0032181",
                                                  name="Platelet count",
                                                  value="250000"),
                      models.ClinicalCodedElement(system="http://www.nlm.nih.gov/research/umls",
                                                  code="C0002965",
                                                  name="Unstable Angina",
                                                  value="true"),
                      models.ClinicalCodedElement(system="http://www.nlm.nih.gov/research/umls",
                                                  code="C1522449",
                                                  name="Radiotherapy",
                                                  value="false"),
                      models.ClinicalCodedElement(system="http://www.nlm.nih.gov/research/umls",
                                                  code="C0242957",
                                                  name="GeneOrProtein-Expression",
                                                  value="Negative;EntityType:GENEORPROTEIN-EXPRESSION"),
                      models.ClinicalCodedElement(system="http://www.nlm.nih.gov/research/umls",
                                                  code="C1300072",
                                                  name="cancer stage",
                                                  value="2")]

# </clinicalInfo>

# Construct Patient
# <PatientConstructor>
patient_info = models.PatientInfo(sex=models.PatientInfoSex.MALE, birth_date=datetime.date(1965, 12, 26),
                                  clinical_info=clinical_info_list)
patient1 = models.PatientRecord(id="patient_id", info=patient_info)
# </PatientConstructor>

# Create registry filter
registry_filters = models.ClinicalTrialRegistryFilter()
# Limit the trial to a specific patient condition ("Non-small cell lung cancer")
registry_filters.conditions = ["non small cell lung cancer (nsclc)"]
# Specify the clinical trial registry source as ClinicalTrials.Gov
registry_filters.sources = [models.ClinicalTrialSource.CLINICALTRIALS_GOV]
# Limit the clinical trial to a certain location, in this case California, USA
registry_filters.facility_locations = [
    models.GeographicLocation(country_or_region="United States", city="Gilbert", state="Arizona")]
# Limit the trial to a specific recruitment status
registry_filters.recruitment_statuses = [models.ClinicalTrialRecruitmentStatus.RECRUITING]

# Construct ClinicalTrial instance and attach the registry filter to it.
clinical_trials = models.ClinicalTrials(registry_filters=[registry_filters])

# Create TrialMatcherRequest
configuration = models.TrialMatcherModelConfiguration(clinical_trials=clinical_trials)
trial_matcher_data = models.TrialMatcherData(patients=[patient1], configuration=configuration)

poller = trial_matcher_client.begin_match_trials(trial_matcher_data)
trial_matcher_result = poller.result()
if trial_matcher_result.status == models.JobStatus.SUCCEEDED:
    tm_results = trial_matcher_result.results
    for patient_result in tm_results.patients:
        print(f"Inferences of Patient {patient_result.id}")
        for tm_inferences in patient_result.inferences:
            print(f"Trial Id {tm_inferences.id}")
            print(f"Type: {str(tm_inferences.type)}  Value: {tm_inferences.value}")
            print(f"Description {tm_inferences.description}")
else:
    tm_errors = trial_matcher_result.errors
    if tm_errors is not None:
        for error in tm_errors:
            print(f"{error.code} : {error.message}")
```

## Troubleshooting

### General

Health Insights Clinical Matching client library will raise exceptions defined in [Azure Core][azure_core].

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
## Additional documentation

For more extensive documentation on Azure Health Insights Clinical Matching, see the [Clinical Matching documentation][clinical_matching_docs] on docs.microsoft.com.


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
[azure_core]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html#module-azure.core.exceptions
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_sub]: https://azure.microsoft.com/free/
[azure_portal]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesHealthInsights
[azure_cli]: https://learn.microsoft.com/cli/azure/
[clinical_matching_docs]: https://review.learn.microsoft.com/azure/cognitive-services/health-decision-support/trial-matcher/overview?branch=main
[hi_pypi]: https://pypi.org/project/azure-healthinsights-clinicalmatching/
[hi_pypi]: https://pypi.org/
[product_docs]: https://review.learn.microsoft.com/azure/cognitive-services/health-decision-support/trial-matcher/?branch=main
[clinical_matching_api_documentation]: https://review.learn.microsoft.com/rest/api/cognitiveservices/healthinsights/trial-matcher?branch=healthin202303
[hi_samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/samples
[hi_source_code]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-clinicalmatching/azure/healthinsights/clinicalmatching
