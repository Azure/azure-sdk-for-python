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
Their main purpose is to be used in inline examples for class and methods throughout the codebase that render alongside our reference documentation on [learn.microsoft.com](https://learn.microsoft.com/python/api/azure-ai-ml/?view=azure-python).

```markdown
.. admonition:: Example:

    .. literalinclude:: ../samples/ml_samples_authentication.py
        :start-after: [START create_ml_client_from_config_default]
        :end-before: [END create_ml_client_from_config_default]
        :language: python
        :dedent: 8
        :caption: Creating an MLClient from a file named "config.json"
            in directory "src".
```

If adding or updating a public class or method, please add or update the example as well. Double-check that you have the correct path for `literalinclude::`. In the Sphinx build, each module is only one directory level away from azure-ai-ml, so the `literalinclude` path should always be `../samples/<sample file name>`.

Each samples file is run during the azure-sdk-for-python Build CI to ensure that examples are up-to-date and functioning.


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
3. Follow the usage described in the file, e.g. `python ml_samples_authentication.py`

## Next steps

Check out the [API reference documentation](https://learn.microsoft.com/python/api/overview/azure/ai-ml-readme?view=azure-python) to learn more about what you can do with the Azure Machine Learning Client Library.
