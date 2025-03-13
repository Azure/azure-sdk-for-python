---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-projects
urlFragment: projects-samples
---

# Samples for Azure Projects client library for Python

These code samples show common scenario operations with the Azure Projects client library.

Please note that some of these samples will provision resources to your Azure Subscription which may incur charges. See the description at the top of each sample for details.


|**File Name**|**Description**|
|-------------|---------------|
|[sample_helloworld.py][helloworld]|A demonstration of the basic features of Azure Projects using Azure Blob Storage as an example. This includes creating an `AzureApp`, provisioning resources and customizing infrastructure.|
<!-- |[sample_resource_references.py][resource_references]|Demonstrates how existing resources can be accessed.| -->


### Prerequisites
* Python 3.9 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/).
* You must have [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/) installed and authenticated.
* Some of the samples require existing resources to be deployed, please see the description at the beginning of each sample for details.

## Setup

1. Install the Azure Projects client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install --pre azure-projects
```
2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_helloworld.py`


<!-- LINKS -->

[helloworld]:https://github.com/Azure/azure-sdk-for-python/tree/feature/azure-projects/sdk/projects/azure-projects/samples/sample_helloworld.py

[resource_references]:https://github.com/Azure/azure-sdk-for-python/tree/feature/azure-projects/sdk/projects/azure-projects/samples/sample_resource_references.py
