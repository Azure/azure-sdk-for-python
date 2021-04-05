# Azure Container Registry client library for Python

Azure Container Registry allows you to store and manage container images and artifacts in a private registry for all types of container deployments.

Use the client library for Azure Container Registry to:

- List images or artifacts in a registry
- Obtain metadata for images and artifacts, repositories and tags
- Set read/write/delete properties on registry items
- Delete images and artifacts, repositories and tags

[Source code][source] | [Package (Pypi)]<!--[package]--> | [API reference documentation]<!--[docs]--> | [REST API documentation][rest_docs] | [Product documentation][product_docs]

## Getting started

### Install the package

Install the Azure Container Registry client library for Python with [pip][pip_link]:

```bash
pip install --pre azure-containerregistry
```

### Prerequisites

You need an [Azure subscription][azure_sub] and a [Container Registry account][container_registry_docs] to use this package.

To create a new Container Registry, you can use the [Azure Portal][container_registry_create_portal],
[Azure PowerShell][container_registry_create_ps], or the [Azure CLI][container_registry_create_cli].
Here's an example using the Azure CLI:

```Powershell
az acr create --name MyContainerRegistry --resource-group MyResourceGroup --location westus --sku Basic
```

### Authenticate the client

The [Azure Identity library][identity] provides easy Azure Active Directory support for authentication.

```python
# Create a ContainerRegistryClient that will authenticate through Active Directory
from azure.containerregistry import ContainerRegistryClient
account_url = "https://MYCONTAINERREGISTRY.azurecr.io"
client = ContainerRegistryClient(account_url, DefaultAzureCredential)
```

## Key concepts

A **registry** stores Docker images and [OCI Artifacts](https://opencontainers.org/).  An image or artifact consists of a **manifest** and **layers**.  An image's manifest describes the layers that make up the image, and is uniquely identified by its **digest**.  An image can also be "tagged" to give it a human-readable alias.  An image or artifact can have zero or more **tags** associated with it, and each tag uniquely identifies the image.  A collection of images that share the same name, but have different manifests and tags, is referred to as a **repository**.

For more information please see [Container Registry Concepts](https://docs.microsoft.com/azure/container-registry/container-registry-concepts).

### Thread safety

We guarantee that all client instance methods are thread-safe and independent of each other ([guideline](https://azure.github.io/azure-sdk/dotnet_introduction.html#dotnet-service-methods-thread-safety)). This ensures that the recommendation of reusing client instances is always safe, even across threads.


## Examples

<!-- Pending Sample Creation -->

## Troubleshooting

All container registry service operations will throw a
[RequestFailedException][RequestFailedException] on failure.

## Next steps

<!-- Pending Sample Creation -->

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
[source]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/containerregistry/azure-containerregistry
[package]: https://pypi.org/azure-containerregistry
<!-- [docs]: https://docs.microsoft.com/en-us/python/api/overview/azure/container-registry?view=azure-python-preview -->
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
[identity]: https://github.com/Azure/azure-sdk-for-net/tree/master/sdk/identity/Azure.Identity/README.md
[RequestFailedException]: https://github.com/Azure/azure-sdk-for-net/tree/master/sdk/core/Azure.Core/src/RequestFailedException.cs
[samples]: https://github.com/Azure/azure-sdk-for-net/blob/master/sdk/containerregistry/Azure.Containers.ContainerRegistry/samples/
[cla]: https://cla.microsoft.com
[coc]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com