---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-farmbeats
urlFragment: farmbeats-samples
---

# Azure FarmBeats samples for Python client

These sample programs demonstrate some common use case scenairos for the [FarmBeats Python client library][python_sdk].

- [sample_hello_world.py][hello_world_sample] demonstrates the most basic operation that can be performed - creation of a Farmer. Use this to understand how to create the client object, how to authenticate it, and make sure your client is set up correctly to call into your FarmBeats endpoint.

- [sample_attachments.py][attachments_sample] demonstrates FarmBeats' capabaility of storing arbitrary files in context to the various [farm hierarchy][farm_hierarchy_docs] objects. We first attach some files onto a farmer and a farm, and then download all existing attachments for the farmer onto a local directory.

Additionally, for each sample, there are corresponding files in the [`samples/async`][async_samples] directory

## Prerequisites

To run the samples, you need:

- A [python][get_python] environment. Supported versions are 2.7 and 3.6+.
- An Azure subscription. Create a free subscription [here][azure_free_sub].
- A FarmBeats resource. See [installation docs][install_farmbeats] to create a new FarmBeats resource.

Additionally, there are some specific prerequisites if you want to leverage third party integrations into FarmBeats:

- A subscription to a [supported weather provider][weather_docs], to run the weather sample.

## How to run the samples

### Install the dependencies

To run the samples, you need the following three dependencies.
```bash
pip install azure-agrifood-farming azure-identity aiohttp
```

### Set up the credentials for authentication

We use [azure-identity][azure_identity]'s [DefaultAzureCredential][azure_identity_default_azure_credential] to authenticate to your FarmBeats instance. If you have followed the [installation docs][install_farmbeats], you should already have an application created, and the appropriate RBAC roles assigned. Set the following environment variables to the appropriate values. 

- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`
- `FARMBEATS_ENDPOINT`

_Note: There are alternate mechanisms of authentication supported by `azure-identity`. Check out the docs [here][azure_identity]_

Once these are set correctly, you can go ahead and run the sample_hello_world.py sample to make sure everything works correctly.

```bash
python sample_hello_world.py
```

If everything worked fine, you should see an output like this:
```
Creating farmer, or updating if farmer already exists... Done
Here are the details of the farmer:
ID: contoso-farmer
Name: Contoso
Description: Contoso is hard working.
Created timestamp: 2021-06-21 10:21:11+00:00
Last modified timestamp: 2021-06-22 21:01:35+00:00
```


<!-- Product docs aka.ms links-->
[farm_hierarchy_docs]: https://aka.ms/FarmBeatsFarmHierarchyDocs
[weather_docs]: https://aka.ms/FarmBeatsWeatherDocs/
[install_farmbeats]: https://aka.ms/FarmBeatsInstallDocumentationPaaS/

<!-- Links to samples files -->
[async_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/agrifood/azure-agrifood-farming/samples/async
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/agrifood/azure-agrifood-farming/samples/sample_hello_world.py
[attachments_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/agrifood/azure-agrifood-farming/samples/sample_attachments.py

<!-- Microsoft/Azure related links -->
[azure_free_sub]: https://azure.microsoft.com/free/
[azure_identity]: https://pypi.org/project/azure-identity/
[azure_identity_default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[python_sdk]: https://pypi.org/project/azure-agrifood-farming/

<!-- Links to external sites -->
[get_python]: https://www.python.org/
