## **AzureML v2 Reference Documentation Guide**

When updating the codebase, please note the following guidelines for creating user-friendly docstrings. These are in alignment with the [Azure SDK for Python documentation guidelines](https://azure.github.io/azure-sdk/python_documentation.html#docstrings).
 
#### Principles 

1. **Accuracy**: The documentation accurately reflects the features and functionality of the product.
2. **Completeness**: The documentation covers all relevant features and functionality of the product.
3. **Clarity**: The documentation is written in clear, concise language that is easy to understand.  
4. **Consistency**: The documentation has a consistent format and structure, making it easy to navigate and follow.  
5. **Relevance**: The documentation is up-to-date and relevant to the current version of the product. 
6. **Coverage**: Every public object must have a docstring. Docstrings are encouraged, but not required for private objects. 
7. **Demonstration**: Every docstring should include an up-to-date code snippet that demonstrates how to use the product effectively. 


##### Accuracy 

- No broken links are allowed in reference documentation, and all links must be location/language neutral (e.g. no /en-us/ in links).
- Docstring details should be aligned with type hints.
- Any code snippets should be defined in the samples directory in this folder so that they are tested during every CI run.
- Constructors (`def __init__`) should return None, per [PEP 484 standards](https://peps.python.org/pep-0484/#the-meaning-of-annotations).

 
##### Completeness 

- Be sure to warn of any edge cases or note special circumstances, if applicable. This can be done using an admonition in the docstring. Sphinx provides classes for other types of messages that you should feel free to use if appropriate: 

    ```markdown
    .. admonition:: Additional Note 

       :class: note 

       This is a note admonition. 
    
    .. admonition:: Warning 

       :class: warning 

       This is a warning admonition. 
    
    .. admonition:: Important 

       :class: danger 

       This is an important admonition. 
    
    .. admonition:: Information 

       :class: info 

       This is an informational admonition. 
    ```
 

##### Clarity 

 - Use Union/Optional when appropriate in function declaration, and note the default value in the docstring (e.g. “Defaults to 0.”).
 - For classes, include docstring in definition only. If you include a docstring in both the class definition and the constructor (init method) docstrings, it will show up twice in the reference docs.
 - When referencing an AzureML v2 class as a type in a docstring, use the full path to the class and prepend it with a "~". This will create a link when the documentation is rendered on learn.microsoft.com that will take the user to the class reference documentation for more information.

```python
"""
:param sampling_algorithm: Sampling algorithm for sweep job.
:type sampling_algorithm: ~azure.ai.ml.sweep.SamplingAlgorithm
"""
```

 
##### Consistency 

 - All docstrings should be written in [Sphinx style](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html#the-sphinx-docstring-format) noting all types and if any exceptions are raised. The [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) VSCode extension or GitHub Copilot can help autocomplete in this style for you. 

 

##### Relevance

- If you deprecate an object, make sure it’s documented in the reference docs. 
- If you change how an object should be used, ensure that all code snippets in the samples directory in this folder are updated accordingly.

 

##### Coverage 

- AzureML v2 is working to get 95% documentation coverage of the entire codebase. ALL new code that you write or existing code that you edit must include a docstring following all of the guidelines. This will be enforced via the interrogate Python package in CI in the future. In the meantime, you can use [interrogate](https://interrogate.readthedocs.io/en/latest/) locally to keep yourself honest. 

```bash
$ pip install interrogate
$ interrogate -vv [PATH TO REPO/MODULE/FILE]
```

 

##### Demonstration 

- Unless the object is not meant to be used directly, a code snippet should be added. The samples directory in this folder should be updated to include your new examples – these can be taken from a notebook in [azureml-examples](https://github.com/Azure/azureml-examples), a test scenario, or you can create your own. You should test them locally, but they will also be tested during CI. See [this guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md) for more information. 
- The code snippet should be comprehensive enough to show understand how the object works; however, keep it concise – this is still a reference documentation page, not a sample repository. 


##### Previewing Docs Before Release
The Azure SDK for Python repository automatically generates a documentation build with every CI run. To preview your documentation changes before merging into main, create a pull request, go to the CI run, and download the output of the "documentation" folder in the Artifacts.

After a PR is merged, you should double-check your changes the next day at on [review.learn.microsoft.com](https://review.learn.microsoft.com/python/api/azure-ai-ml/azure.ai.ml) where a daily build based off the main branch is hosted. Every release, the official reference documentation is updated on [learn.microsoft.com](https://learn.microsoft.com/python/api/azure-ai-ml/azure.ai.ml) for public consumption.
