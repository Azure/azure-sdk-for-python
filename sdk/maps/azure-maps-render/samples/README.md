---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-maps-render
---

# Samples for Azure Maps Render client library for Python

These code samples show common scenario operations with the Azure Maps Render client library.

Authenticate the client with a Azure Maps Render [API Key Credential](https://docs.microsoft.com/azure/azure-maps/how-to-manage-account-keys):

[samples authentication](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-render/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-render/samples/async_samples/sample_authentication_async.py))

Then for common Azure Maps Render operations:

* Perform fuzzy render: [sample_fuzzy_render.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-render/samples/sample_fuzzy_render.py) ([async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/maps/azure-maps-render/samples/async_samples/sample_fuzzy_render_async.py))

## Prerequisites

* Python 3.6 or later is required to use this package
* You must have an [Azure subscription](https://azure.microsoft.com/free/)
* A deployed Maps Services resource. You can create the resource via [Azure Portal][azure_portal] or [Azure CLI][azure_cli].

## Setup

1. Install the Azure Maps Render client library for Python with [pip](https://pypi.org/project/pip/):

   ```bash
   pip install azure-maps-render --pre
   ```

2. Clone or download [this repository](https://github.com/Azure/azure-sdk-for-python)
3. Open this sample folder in [Visual Studio Code](https://code.visualstudio.com) or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_fuzzy_render.py`

## Next steps

Check out the [API reference documentation](https://docs.microsoft.com/rest/api/maps/render)
to learn more about what you can do with the Azure Maps Render client library.

<!-- LINKS -->
[azure_portal]: https://portal.azure.com
[azure_cli]: https://docs.microsoft.com/cli/azure
