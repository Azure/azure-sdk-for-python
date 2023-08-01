---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai-ml
urlFragment: ml-samples
---

# Azure Machine Learning Client Library for Python Samples

These are code samples that show common scenario operations with the Azure Machine Learning Client Library for Python.

These samples provide example code for additional scenarios commonly encountered while working with Machine Learning Library:

* [ml_samples_authentication_sovereign_cloud.py](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ml/azure-ai-ml/samples/ml_samples_authentication_sovereign_cloud.py) - Examples for creating MLClient for non public cloud:
  * Set up a MLClient
  * List workspaces in the subscription.

## Prerequisites

* Python 3.7 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/) to run these samples.

## Setup

1. Install the Azure Machine Learning Client Library for Python with [pip](https://pypi.org/project/pip/):

   ```bash
    pip install azure-ai-ml
    pip install azure-identity
    ```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python ml_samples_authentication_sovereign_cloud.py`

## Next steps

Check out the [API reference documentation](https://learn.microsoft.com/python/api/overview/azure/ai-ml-readme?view=azure-python) to learn more about what you can do with the Azure Machine Learning Client Library.
