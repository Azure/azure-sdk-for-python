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

The following sample programs demonstrate some common use case scenairos for the [FarmBeats Python client library][python_sdk].

| Files                                                               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [sample_hello_world.py][hello_world_sample]                         | This sample demonstrates the most basic operation that can be performed - creation of a Farmer. Use this to understand how to create the client object, how to authenticate it, and make sure your client is set up correctly to call into your FarmBeats endpoint.                                                                                                                                                                                                                                      |
| [sample_farm_hierarchy.py][farm_hierarchy_sample]                   | This sample demonstrates how to create a simple [farm hierarchy][farm_hierarchy_docs], comprising of Farmer, Farm, Field and Boundary.                                                                                                                                                                                                                                                                                                                                                                   |
| [sample_farm_hierarchy_complete.py][farm_hierarchy_complete_sample] | This builds on the previous sample to add to the previous sample, and demonstrate the relationships between Crops, Crop Varities, Seasons and Seasonal Fields and the other farm hierarchy objects.                                                                                                                                                                                                                                                                                                      |
| [sample_satellite_download.py][satellite_download_sample]             | This sample demonstrates FarmBeats' satellite integrations and how to ingest satellite imagery into the platform, and then download them onto a local directory. This demonstrates key concepts of how to create a job in FarmBeats, and how to poll on the completion of the job using the SDK. In the [corresponding async sample][satellite_download_async_sample] we demonstrate how to handle concurrent download of potentially hundreds of files by limiting the max concurrency using semaphores. |
| [sample_attachments.py][attachments_sample]                         | This sample demonstrates FarmBeats' capabaility of storing arbitrary files in context to the various farm hierarchy objects. We first attach some files onto a farmer and a farm, and then download all existing attachments for the farmer onto a local directory.                                                                                                                                                                                                                                      |
| [sample_cascade_delete.py][cascade_delete_sample]                   | This sample demonstrates the usage of cascade delete jobs to perform cleanup of farm hierarchy objects. A cascade delete job handles the recursive deletion of all dependent data for the given parent resource. Use this to clean up the sample resources that you create in the other samples.                                                                                                                                                                                                         |

Additionally, for each sample, there are corresponding files in the [`samples/async`][async_samples] directory that demonstrate the same scenarios using the async FarmBeats client. Using the async approach will offer much better performance when parts of the code can be executed concurrentlly. This is especially important when downloading files, such as in the satellite data download sample, and in the attachments sample.


## Prerequisites

To run the samples, you need:

- A [python][get_python] environment. Supported versions are 2.7 and 3.6+.
- An Azure subscription. Create a free subscription [here][azure_free_sub].
- A FarmBeats resource. See [installation docs][install_farmbeats] to create a new FarmBeats resource.

Additionally, there are some specific prerequisites if you want to leverage third party integrations into FarmBeats:

- A subscription to a [supported weather provider][weather_docs], to run the weather sample.

## How to run the samples

### Install the dependencies

To run the samples, you need to install the following dependencies:
```bash
pip install azure-agrifood-farming azure-identity aiohttp python-dotenv
```
_Note: You can use your preferred async http client to use the async FarmBeats client, instead of using aiohttp._

### Set up the credentials for authentication

We use [azure-identity][azure_identity]'s [DefaultAzureCredential][azure_identity_default_azure_credential] to authenticate to your FarmBeats instance. If you have followed the [installation docs][install_farmbeats], you should already have an application created, and the appropriate RBAC roles assigned.

Set the following variables to the appropriate values either in the [`.env`][dot_env_file] file, or alternatively in your environment variables.

- `AZURE_TENANT_ID`: The tenant ID of your active directory application.
- `AZURE_CLIENT_ID`: The client ID of your active directory application.
- `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
- `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.

_Note: There are alternate mechanisms of authentication supported by `azure-identity`. Check out the docs [here][azure_identity]_.

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
[async_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agrifood/azure-agrifood-farming/samples/async
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/sample_hello_world.py
[attachments_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/sample_attachments.py
[cascade_delete_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/sample_cascade_delete.py
[satellite_download_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/sample_satellite_download.py
[farm_hierarchy_complete_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/sample_farm_hierarchy_complete.py
[farm_hierarchy_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/sample_farm_hierarchy.py
[satellite_download_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/async/sample_satellite_download_async.py
[dot_env_file]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agrifood/azure-agrifood-farming/samples/.env

<!-- Microsoft/Azure related links -->
[azure_free_sub]: https://azure.microsoft.com/free/
[azure_identity]: https://pypi.org/project/azure-identity/
[azure_identity_default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[python_sdk]: https://pypi.org/project/azure-agrifood-farming/

<!-- Links to external sites -->
[get_python]: https://www.python.org/
