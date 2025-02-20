---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-maps-search
---

# Samples for Azure Maps Search client library for Python

These code samples show common scenario operations with the Azure Maps Search client library.

Authenticate the client with a Azure Maps Search [API Key Credential](https://learn.microsoft.com/azure/azure-maps/how-to-manage-account-keys):

Then for common Azure Maps Search operations:

* Perform geocode search: [sample_geocode.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_geocode.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_geocode_async.py))

* Perform geocode batch search: [sample_geocode_batch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_geocode_batch.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_geocode_batch_async.py))

* Perform reverse geocode search: [sample_reverse_geocode.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_reverse_geocode.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_reverse_geocode_async.py))

* Perform reverse batch geocode search: [sample_reverse_geocode_batch.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_reverse_geocode_batch.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_reverse_geocode_batch_async.py))

* Perform polygon search: [sample_get_polygon.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/sample_get_polygon.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-search/samples/async_samples/sample_get_polygon_async.py))


## Prerequisites

* Python 3.8 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/)
* A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

## Setup

1. Install the Azure Maps Search client library for Python with [pip](https://pypi.org/project/pip/):

   ```bash
   pip install azure-maps-search --pre
   ```

2. Clone or download [this repository](https://github.com/Azure/azure-sdk-for-python)
3. Open this sample folder in [Visual Studio Code](https://code.visualstudio.com) or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_geocode.py`

## Next steps

Check out the [API reference documentation](https://learn.microsoft.com/rest/api/maps/search)
to learn more about what you can do with the Azure Maps Search client library.

<!-- LINKS -->
[azure_portal]: https://portal.azure.com
[azure_cli]: https://learn.microsoft.com/cli/azure
