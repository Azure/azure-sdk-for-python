# Azure Container Registry client library for Python

Azure Container Registry allows you to store and manage container images and artifacts in a private registry for all types of container deployments.

Use the client library for Azure Container Registry to:

- List images or artifacts in a registry
- Obtain metadata for images and artifacts, repositories and tags
- Set read/write/delete properties on registry items
- Delete images and artifacts, repositories and tags

[Source code][source] | [Package (Pypi)][package] | [API reference documentation][docs] | [REST API documentation][rest_docs] | [Product documentation][product_docs]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_
_Python 3.7 or later is required to use this package. For more details, please refer to [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)._

## Getting started

### Install the package

Install the Azure Container Registry client library for Python with [pip][pip_link]:

```bash
pip install --pre azure-containerregistry
```

### Prerequisites

* Python 3.7 or later is required to use this package.
* You need an [Azure subscription][azure_sub] and a [Container Registry account][container_registry_docs] to use this package.

To create a new Container Registry, you can use the [Azure Portal][container_registry_create_portal],
[Azure PowerShell][container_registry_create_ps], or the [Azure CLI][container_registry_create_cli].
Here's an example using the Azure CLI:

```Powershell
az acr create --name MyContainerRegistry --resource-group MyResourceGroup --location westus --sku Basic
```

### Authenticate the client

The [Azure Identity library][identity] provides easy Azure Active Directory support for authentication. The `DefaultAzureCredential` assumes the `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET` environment variables are set, for more information refer to the [Azure Identity environment variables section](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#environment-variables)

```python
# Create a ContainerRegistryClient that will authenticate through Active Directory
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential

endpoint = "https://mycontainerregistry.azurecr.io"
audience = "https://management.azure.com"
client = ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience=audience)
```

## Key concepts

A **registry** stores Docker images and [OCI Artifacts](https://opencontainers.org/).  An image or artifact consists of a **manifest** and **layers**.  An image's manifest describes the layers that make up the image, and is uniquely identified by its **digest**.  An image can also be "tagged" to give it a human-readable alias.  An image or artifact can have zero or more **tags** associated with it, and each tag uniquely identifies the image.  A collection of images that share the same name but have different tags, is referred to as a **repository**.

For more information please see [Container Registry Concepts](https://docs.microsoft.com/azure/container-registry/container-registry-concepts).


## Examples

The following sections provide several code snippets covering some of the most common ACR Service tasks, including:

- [List repositories](#list-repositories)
- [List tags with anonymous access](#list-tags-with-anonymous-access)
- [Set artifact properties](#set-artifact-properties)
- [Delete images](#delete-images)

Please note that each sample assumes there is a `CONTAINERREGISTRY_ENDPOINT` environment variable set to a string containing the `https://` prefix and the name of the login server, for example "https://myregistry.azurecr.io".

### List repositories

Iterate through the collection of repositories in the registry.

```python
endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]

with ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="https://management.azure.com") as client:
    # Iterate through all the repositories
    for repository_name in client.list_repository_names():
        print(repository_name)
```

### List tags with anonymous access

Iterate through the collection of tags in the repository with anonymous access.

```python
endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]

with ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="https://management.azure.com") as client:
    manifest = client.get_manifest_properties("library/hello-world", "latest")
    print(manifest.repository_name + ": ")
    for tag in manifest.tags:
        print(tag + "\n")
```

### Set artifact properties

Set properties of an artifact.

```python
endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]

with ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="https://management.azure.com") as client:
    # Set permissions on the v1 image's "latest" tag
    client.update_manifest_properties(
        "library/hello-world",
        "latest",
        can_write=False,
        can_delete=False
    )
```

### Delete images

Delete images older than the first three in the repository.

```python
endpoint = os.environ["CONTAINERREGISTRY_ENDPOINT"]

with ContainerRegistryClient(endpoint, DefaultAzureCredential(), audience="https://management.azure.com") as client:
    for repository in client.list_repository_names():
        manifest_count = 0
        for manifest in client.list_manifest_properties(repository, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING):
            manifest_count += 1
            if manifest_count > 3:
                print("Deleting {}:{}".format(repository, manifest.digest))
                client.delete_manifest(repository, manifest.digest)
```

## Troubleshooting

### General
ACR client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging
This library uses the standard
[logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Next steps

- Go further with azure.containerregistry and our [samples][samples].
- Watch a [demo or deep dive video](https://azure.microsoft.com/resources/videos/index/?service=container-registry).
- Read more about the [Azure Container Registry service](https://docs.microsoft.com/azure/container-registry/container-registry-intro).

## Contributing

This project welcomes contributions and suggestions.  Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][coc].
For more information see the [Code of Conduct FAQ][coc_faq]
or contact [opencode@microsoft.com][coc_contact] with any
additional questions or comments.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fcontainerregistry%2Fazure-containerregistry%2FREADME.png)

<!-- LINKS -->
[source]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/containerregistry/azure-containerregistry
[package]: https://pypi.org/project/azure-containerregistry/
[docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-containerregistry/1.0.0b1/index.html
[rest_docs]: https://docs.microsoft.com/rest/api/containerregistry/
[product_docs]:  https://docs.microsoft.com/azure/container-registry
[pip_link]: https://pypi.org
[container_registry_docs]: https://docs.microsoft.com/azure/container-registry/container-registry-intro
[container_registry_create_ps]: https://docs.microsoft.com/azure/container-registry/container-registry-get-started-powershell
[container_registry_create_cli]: https://docs.microsoft.com/azure/container-registry/container-registry-get-started-azure-cli
[container_registry_create_portal]: https://docs.microsoft.com/azure/container-registry/container-registry-get-started-portal
[container_registry_concepts]: https://docs.microsoft.com/azure/container-registry/container-registry-concepts
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[identity]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/containerregistry/azure-containerregistry/samples
[cla]: https://cla.microsoft.com
[coc]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
