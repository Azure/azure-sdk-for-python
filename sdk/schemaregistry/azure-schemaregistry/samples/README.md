---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-event-hubs
urlFragment: schemaregistry-samples
---

# Azure Schema Registry client library for Python Samples

These are code samples that show common scenario operations with the Schema Registry client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations.

Several Schema Registry Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Schema Registry:

* [schema_registry.py][schema_registry_sample] ([async version][schema_registry_async_sample]) - Examples for common Schema Registry tasks:
    * Register a schema
    * Get schema by id
    * Get schema id

## Prerequisites
- Python 3.6 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Schema Registry, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Schema Registry client library and Azure Identity client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-schemaregistry
```

To run samples utilizing the Azure Active Directory for authentication, please install the azure-identity library:

```bash
pip install azure-identity
```

2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python schema_registry.py`

## Next steps

Check out the [API reference documentation][api_reference] to learn more about
what you can do with the Azure Schema Registry client library.

<!-- LINKS -->
[schema_registry_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry/samples/sync_samples/schema_registry.py
[schema_registry_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/schemaregistry/azure-schemaregistry/samples/async_samples/schema_registry_async.py
[api_reference]: https://docs.microsoft.com/python/api/overview/azure/schemaregistry-readme
