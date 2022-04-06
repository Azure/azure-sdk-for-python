---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-containerregistry
urlFragment: containerregistry-samples
---

# Samples for Azure Container Registry

These code samples show common scenario operations with the Azure Container Registry client library. The code samples assume an environment variable `CONTAINERREGISTRY_ENDPOINT` is set, which includes the name of the login server and the `https://` prefix. For more information on using AAD with Azure Container Registry, please see the service's [Authentication Overview](https://docs.microsoft.com/azure/container-registry/container-registry-authentication).
The async versions of the samples require Python 3.6 or later.


|**File Name**|**Description**|
|-------------|---------------|
|[sample_hello_world.py][hello_world] ([sample_hello_world_async.py][hello_world_async]) |Instantiate a `ContainerRegistryClient` object and iterating through the collection of tags in the repository with anonymous access |
|[sample_delete_tags.py][delete_tags] ([sample_delete_tags_async.py][delete_tags_async]) | Delete tags from a repository |
|[sample_delete_images.py][delete_images] ([sample_delete_images_async.py][delete_images_async]) | Delete images from a repository |
|[sample_set_image_properties.py][set_image_properties] ([sample_set_image_properties_async.py][set_image_properties_async]) | Set read/write/delete properties on an image |
|[sample_list_tags.py][list_tags] ([sample_list_tags_async.py][list_tags_async]) | List tags on an image with anonymous access |

### Prerequisites
* Python 3.6 or later is required to use this package.
* You need an [Azure subscription][azure_sub] and a [Container Registry account][container_registry_docs] to use this package.

## Setup

1. Install the Azure Container Registry client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install --pre azure-containerregistry
```
2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_basic_use.py`


## Next steps

Check out the [API reference documentation][rest_docs] to learn more about what you can do with the Azure Container Registry client library.


<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[rest_docs]: https://docs.microsoft.com/rest/api/containerregistry/
[container_registry_docs]: https://docs.microsoft.com/azure/container-registry/container-registry-intro
[hello_world]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/sample_hello_world.py
[hello_world_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/async_samples/sample_hello_world_async.py
[delete_tags]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/sample_delete_tags.py
[delete_tags_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/async_samples/sample_delete_tags_async.py
[delete_images]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/sample_delete_images.py
[delete_images_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/async_samples/sample_delete_images_async.py
[set_image_properties]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/sample_set_image_properties.py
[set_image_properties_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/async_samples/sample_set_image_properties_async.py
[list_tags]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/sample_list_tags.py
[list_tags_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/samples/async_samples/sample_list_tags_async.py
