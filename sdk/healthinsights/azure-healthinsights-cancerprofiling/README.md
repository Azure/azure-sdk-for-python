# Azure Cognitive Services Health Insights Cancer Profiling client library for Python

[Health Insights](https://review.learn.microsoft.com/azure/azure-health-insights/?branch=release-azure-health-insights) is an Azure Applied AI Service built with the Azure Cognitive Services Framework, that leverages multiple Cognitive Services, Healthcare API services and other Azure resources.

The [Cancer Profiling model][cancer_profiling_docs] receives clinical records of oncology patients and outputs cancer staging, such as clinical stage TNM categories and pathologic stage TNM categories as well as tumor site, histology.


[Source code][hi_source_code] | [Package (PyPI)][hi_pypi] | [API reference documentation][cancer_profiling_api_documentation] | [Product documentation][product_docs] | [Samples][hi_samples]

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Cognitive Services Health Insights instance.


### Install the package

```bash
pip install azure-healthinsights-cancerprofiling
```

This table shows the relationship between SDK versions and supported API versions of the service:

|SDK version|Supported API version of service |
|-------------|---------------|
|1.0.0b1 | 2023-03-01-preview|


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

#### Create a CancerProfilingClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of **AzureKeyCredential**. Use the key as the credential parameter to authenticate the client:

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.cancerprofiling.aio import CancerProfilingClient

KEY = os.environ["HEALTHINSIGHTS_KEY"]
ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]

cancer_profiling_client = CancerProfilingClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
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

The Cancer Profiling model allows you to infer cancer attributes such as tumor site, histology, clinical stage TNM categories and pathologic stage TNM categories from unstructured clinical documents.

## Examples

The following section provides several code snippets covering some of the most common Health Insights - Cancer Profiling service tasks, including:
- [Cancer Profiling](#cancer-profiling "Cancer Profiling")

### Cancer Profiling

Infer key cancer attributes such as tumor site, histology, clinical stage TNM categories and pathologic stage TNM categories from a patient's unstructured clinical documents.

```python
import asyncio
import os
import datetime
from azure.core.credentials import AzureKeyCredential
from azure.healthinsights.cancerprofiling.aio import CancerProfilingClient
from azure.healthinsights.cancerprofiling import models

KEY = os.environ["HEALTHINSIGHTS_KEY"]
ENDPOINT = os.environ["HEALTHINSIGHTS_ENDPOINT"]

# Create an Onco Phenotype client
# <client>
cancer_profiling_client = CancerProfilingClient(endpoint=ENDPOINT,
                                                credential=AzureKeyCredential(KEY))
# </client>

# Construct patient
# <PatientConstructor>
patient_info = models.PatientInfo(sex=models.PatientInfoSex.FEMALE, birth_date=datetime.date(1979, 10, 8))
patient1 = models.PatientRecord(id="patient_id", info=patient_info)
# </PatientConstructor>

# Add document list
# <DocumentList>
doc_content1 = """
            15.8.2021
            Jane Doe 091175-8967
            42 year old female, married with 3 children, works as a nurse
            Healthy, no medications taken on a regular basis.
            PMHx is significant for migraines with aura, uses Mirena for contraception.
            Smoking history of 10 pack years (has stopped and relapsed several times).
            She is in c/o 2 weeks of productive cough and shortness of breath.
            She has a fever of 37.8 and general weakness.
            Denies night sweats and rash. She denies symptoms of rhinosinusitis, asthma, and heartburn.
            On PE:
            GENERAL: mild pallor, no cyanosis. Regular breathing rate.
            LUNGS: decreased breath sounds on the base of the right lung. Vesicular breathing. 
                No crackles, rales, and wheezes. Resonant percussion.
            PLAN:
            Will be referred for a chest x-ray.
            ======================================
            CXR showed mild nonspecific opacities in right lung base.
            PLAN:
            Findings are suggestive of a working diagnosis of pneumonia. The patient is referred to a
            follow-up CXR in 2 weeks."""

patient_document1 = models.PatientDocument(type=models.DocumentType.NOTE,
                                           id="doc1",
                                           content=models.DocumentContent(
                                               source_type=models.DocumentContentSourceType.INLINE,
                                               value=doc_content1),
                                           clinical_type=models.ClinicalDocumentType.IMAGING,
                                           language="en",
                                           created_date_time=datetime.datetime(2021, 8, 15))

doc_content2 = """
            Oncology Clinic
            20.10.2021
            Jane Doe 091175-8967
            42-year-old healthy female who works as a nurse in the ER of this hospital.
            First menstruation at 11 years old. First delivery- 27 years old. She has 3 children.
            Didn't breastfeed.
            Contraception- Mirena.
            Smoking- 10 pack years.
            Mother- Belarusian. Father- Georgian. 
            About 3 months prior to admission, she stated she had SOB and was febrile.
            She did a CXR as an outpatient which showed a finding in the base of the right lung-
            possibly an infiltrate.
            She was treated with antibiotics with partial response.
            6 weeks later a repeat CXR was performed- a few solid dense findings in the right lung.
            Therefore, she was referred for a PET-CT which demonstrated increased uptake in the right
            breast, lymph nodes on the right a few areas in the lungs and liver.
            On biopsy from the lesion in the right breast- triple negative adenocarcinoma. Genetic
            testing has not been done thus far.
            Genetic counseling- the patient denies a family history of breast, ovary, uterus,
            and prostate cancer. Her mother has chronic lymphocytic leukemia (CLL).
            She is planned to undergo genetic tests because the aggressive course of the disease,
            and her young age.
            Impression:
            Stage 4 triple negative breast adenocarcinoma.
            Could benefit from biological therapy.
            Different treatment options were explained- the patient wants to get a second opinion."""

patient_document2 = models.PatientDocument(type=models.DocumentType.NOTE,
                                           id="doc2",
                                           content=models.DocumentContent(
                                               source_type=models.DocumentContentSourceType.INLINE,
                                               value=doc_content2),
                                           clinical_type=models.ClinicalDocumentType.PATHOLOGY,
                                           language="en",
                                           created_date_time=datetime.datetime(2021, 10, 20))

doc_content3 = """
            PATHOLOGY REPORT
                                    Clinical Information
            Ultrasound-guided biopsy; A. 18 mm mass; most likely diagnosis based on imaging:  IDC
                                        Diagnosis
            A.  BREAST, LEFT AT 2:00 4 CM FN; ULTRASOUND-GUIDED NEEDLE CORE BIOPSIES:
            - Invasive carcinoma of no special type (invasive ductal carcinoma), grade 1
            Nottingham histologic grade:  1/3 (tubules 2; nuclear grade 2; mitotic rate 1;
            total score; 5/9)
            Fragments involved by invasive carcinoma:  2
            Largest measurement of invasive carcinoma on a single fragment:  7 mm
            Ductal carcinoma in situ (DCIS):  Present
            Architectural pattern:  Cribriform
            Nuclear grade:  2-
                            -intermediate
            Necrosis:  Not identified
            Fragments involved by DCIS:  1
            Largest measurement of DCIS on a single fragment:  Span 2 mm
            Microcalcifications:  Present in benign breast tissue and invasive carcinoma
            Blocks with invasive carcinoma:  A1
            Special studies: Pending"""

patient_document3 = models.PatientDocument(type=models.DocumentType.NOTE,
                                           id="doc3",
                                           content=models.DocumentContent(
                                               source_type=models.DocumentContentSourceType.INLINE,
                                               value=doc_content3),
                                           clinical_type=models.ClinicalDocumentType.PATHOLOGY,
                                           language="en",
                                           created_date_time=datetime.datetime(2022, 1, 1))

patient_doc_list = [patient_document1, patient_document2, patient_document3]
patient1.data = patient_doc_list
# <\DocumentList>

# Set configuration to include evidence for the cancer staging inferences
configuration = models.OncoPhenotypeModelConfiguration(include_evidence=True)

# Construct the request with the patient and configuration
cancer_profiling_data = models.OncoPhenotypeData(patients=[patient1], configuration=configuration)

poller = await cancer_profiling_client.begin_infer_cancer_profile(cancer_profiling_data)
cancer_profiling_result = await poller.result()
if cancer_profiling_result.status == models.JobStatus.SUCCEEDED:
    results = cancer_profiling_result.results
    for patient_result in results.patients:
        print(f"\n==== Inferences of Patient {patient_result.id} ====")
        for inference in patient_result.inferences:
            print(
                f"\n=== Clinical Type: {str(inference.type)} Value: {inference.value}\
                    ConfidenceScore: {inference.confidence_score} ===")
            for evidence in inference.evidence:
                data_evidence = evidence.patient_data_evidence
                print(
                    f"Evidence {data_evidence.id} {data_evidence.offset} {data_evidence.length}\
                        {data_evidence.text}")
else:
    errors = cancer_profiling_result.errors
    if errors is not None:
        for error in errors:
            print(f"{error.code} : {error.message}")
```

## Troubleshooting

### General

Health Insights Cancer Profiling client library will raise exceptions defined in [Azure Core][azure_core].

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
For more extensive documentation on Azure Health Insights Cancer Profiling, see the [Cancer Profiling documentation][cancer_profiling_docs] on docs.microsoft.com.

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
[cancer_profiling_docs]: https://review.learn.microsoft.com/azure/cognitive-services/health-decision-support/oncophenotype/overview?branch=main
[cancer_profiling_api_documentation]: https://review.learn.microsoft.com/rest/api/cognitiveservices/healthinsights/onco-phenotype?branch=healthin202303
[hi_pypi]: https://pypi.org/project/azure-healthinsights-cancerprofiling/
[hi_pypi]: https://pypi.org/
[product_docs]:https://review.learn.microsoft.com/azure/cognitive-services/health-decision-support/oncophenotype/?branch=main
[hi_samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-cancerprofiling/samples
[hi_source_code]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/healthinsights/azure-healthinsights-cancerprofiling/azure/healthinsights/cancerprofiling
