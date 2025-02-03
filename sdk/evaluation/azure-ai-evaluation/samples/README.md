---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-ai-evaluation
urlFragment: evaluation-samples
---

# Azure AI Evaluation Client Library for Python Samples

These are code samples that show common scenario operations with the Azure AI Evaluation Client Library for Python.
Their main purpose is to be used in inline examples for class and methods throughout the codebase that render alongside our reference documentation on [learn.microsoft.com](https://learn.microsoft.com/python/api/azure-ai-evaluation/azure.ai.evaluation?view=azure-python-preview).

```markdown
    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_simulate.py
            :start-after: [START direct_attack_simulator]
            :end-before: [END direct_attack_simulator]
            :language: python
            :dedent: 8
            :caption: Run the DirectAttackSimulator to produce 2 results with 3 conversation turns each (6 messages in each result).
```

If adding or updating a public class or method, please add or update the example as well. Double-check that you have the correct path for `literalinclude::`. In the Sphinx build, each module is only one directory level away from azure-ai-evaluation, so the `literalinclude` path should always be `../samples/<sample file name>`. Follow [this guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md) for information on how to build docs locally to verify your sample renders correctly.

Each samples file is run during the azure-sdk-for-python Build CI to ensure that examples are up-to-date and functioning.


## Prerequisites

* Python 3.9, 3.10, 3.11, or 3.12 is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/) to run these samples.
* You must have an Azure AI project and a model deployment.

## Setup

1. Install the Azure AI Evaluation Client Library for Python with [pip](https://pypi.org/project/pip/):

   ```bash
    pip install azure-ai-evaluation
    ```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python evaluation_samples_common.py`

## Next steps

Check out the [API reference documentation](https://learn.microsoft.com/python/api/azure-ai-evaluation/azure.ai.evaluation?view=azure-python-preview) to learn more about what you can do with the Azure AI Evaluation Client Library.
