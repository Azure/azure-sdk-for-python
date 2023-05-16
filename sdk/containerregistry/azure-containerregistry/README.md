# Azure Container Registry client library for Python

Azure Container Registry allows you to store and manage container images and artifacts in a private registry for all types of container deployments.

Use the client library for Azure Container Registry to:

- List images or artifacts in a registry
- Obtain metadata for images and artifacts, repositories and tags
- Set read/write/delete properties on registry items
- Delete images and artifacts, repositories and tags

[Source code][source]
| [Package (Pypi)][package]
| [Package (Conda)](https://anaconda.org/microsoft/azure-containerregistry/)
| [API reference documentation][docs]
| [REST API documentation][rest_docs]
| [Product documentation][product_docs]

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

- Registry operations:
  - [List repositories](#list-repositories)
  - [List tags with anonymous access](#list-tags-with-anonymous-access)
  - [Set artifact properties](#set-artifact-properties)
  - [Delete images](#delete-images)
- Blob and manifest operations:
  - [Upload images](#upload-images)
  - [Download images](#download-images)
  - [Delete manifest](#delete-manifest)
  - [Delete blob](#delete-blob)

Please note that each sample assumes there is a `CONTAINERREGISTRY_ENDPOINT` environment variable set to a string containing the `https://` prefix and the name of the login server, for example "https://myregistry.azurecr.io". Anonymous access samples are getting endpoint value from environment variable`CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT`.

### List repositories

Iterate through the collection of repositories in the registry.

<!-- SNIPPET:sample_delete_tags.list_repository_names -->

```python
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    # Iterate through all the repositories
    for repository_name in client.list_repository_names():
        print(repository_name)
```

<!-- END SNIPPET -->

### List tags with anonymous access

Iterate through the collection of tags in the repository with anonymous access.

<!-- SNIPPET:sample_list_tags.list_tags_anonymous -->

```python
endpoint = os.environ.get("CONTAINERREGISTRY_ANONREGISTRY_ENDPOINT")
with ContainerRegistryClient(endpoint) as anon_client:
    manifest = anon_client.get_manifest_properties("library/hello-world", "latest")
    print(f"Tags of {manifest.repository_name}: ")
    # Iterate through all the tags
    for tag in manifest.tags:
        print(f"{tag}\n")
```

<!-- END SNIPPET -->

### Set artifact properties

Set properties of an artifact.

<!-- SNIPPET:sample_set_image_properties.update_manifest_properties -->

```python
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    # Set permissions on image "library/hello-world:v1"
    client.update_manifest_properties(
        "library/hello-world",
        "v1",
        can_write=False,
        can_delete=False
    )
```

<!-- END SNIPPET -->

### Delete images

Delete images older than the first three in the repository.

<!-- SNIPPET:sample_delete_images.delete_manifests -->

```python
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    for repository in client.list_repository_names():
        # Keep the three most recent images, delete everything else
        manifest_count = 0
        for manifest in client.list_manifest_properties(
            repository, order_by=ArtifactManifestOrder.LAST_UPDATED_ON_DESCENDING
        ):
            manifest_count += 1
            if manifest_count > 3:
                # Make sure will have the permission to delete the manifest later
                client.update_manifest_properties(
                    repository,
                    manifest.digest,
                    can_write=True,
                    can_delete=True
                )
                print(f"Deleting {repository}:{manifest.digest}")
                client.delete_manifest(repository, manifest.digest)
```

<!-- END SNIPPET -->

### Upload images

To upload a full image, we need to upload individual layers and configuration. After that we can upload a manifest which describes an image or artifact and assign it a tag.

<!-- SNIPPET:sample_set_get_image.upload_blob_and_manifest -->

```python
self.repository_name = "sample-oci-image"
layer = BytesIO(b"Sample layer")
config = BytesIO(json.dumps(
    {
        "sample config": "content",
    }).encode())
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    # Upload a layer
    layer_digest, layer_size = client.upload_blob(self.repository_name, layer)
    print(f"Uploaded layer: digest - {layer_digest}, size - {layer_size}")
    # Upload a config
    config_digest, config_size = client.upload_blob(self.repository_name, config)
    print(f"Uploaded config: digest - {config_digest}, size - {config_size}")
    # Create an oci image with config and layer info
    oci_manifest = {
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": config_digest,
            "sizeInBytes": config_size,
        },
        "schemaVersion": 2,
        "layers": [
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar",
                "digest": layer_digest,
                "size": layer_size,
                "annotations": {
                    "org.opencontainers.image.ref.name": "artifact.txt",
                },
            },
        ],
    }
    # Set the image with tag "latest"
    manifest_digest = client.set_manifest(self.repository_name, oci_manifest, tag="latest")
    print(f"Uploaded manifest: digest - {manifest_digest}")
```

<!-- END SNIPPET -->

### Download images

To download a full image, we need to download its manifest and then download individual layers and configuration.

<!-- SNIPPET:sample_set_get_image.download_blob_and_manifest -->

```python
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    # Get the image
    get_manifest_result = client.get_manifest(self.repository_name, "latest")
    received_manifest = get_manifest_result.manifest
    print(f"Got manifest:\n{received_manifest}")
    
    # Download and write out the layers
    for layer in received_manifest["layers"]:
        # Remove the "sha256:" prefix from digest
        layer_file_name = layer["digest"].split(":")[1]
        try:
            stream = client.download_blob(self.repository_name, layer["digest"])
            with open(layer_file_name, "wb") as layer_file:
                for chunk in stream:
                    layer_file.write(chunk)
        except DigestValidationError:
            print(f"Downloaded layer digest value did not match. Deleting file {layer_file_name}.")
            os.remove(layer_file_name)
        print(f"Got layer: {layer_file_name}")
    # Download and write out the config
    config_file_name = "config.json"
    try:
        stream = client.download_blob(self.repository_name, received_manifest["config"]["digest"])
        with open(config_file_name, "wb") as config_file:
            for chunk in stream:
                config_file.write(chunk)
    except DigestValidationError:
        print(f"Downloaded config digest value did not match. Deleting file {config_file_name}.")
        os.remove(config_file_name)
    print(f"Got config: {config_file_name}")
```

<!-- END SNIPPET -->

### Delete manifest

<!-- SNIPPET:sample_set_get_image.delete_manifest -->

```python
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    get_manifest_result = client.get_manifest(self.repository_name, "latest")
    # Delete the image
    client.delete_manifest(self.repository_name, get_manifest_result.digest)
```

<!-- END SNIPPET -->

### Delete blob

<!-- SNIPPET:sample_set_get_image.delete_blob -->

```python
with ContainerRegistryClient(self.endpoint, self.credential) as client:
    get_manifest_result = client.get_manifest(self.repository_name, "latest")
    received_manifest = get_manifest_result.manifest
    # Delete the layers
    for layer in received_manifest["layers"]:
        client.delete_blob(self.repository_name, layer["digest"])
    # Delete the config
    client.delete_blob(self.repository_name, received_manifest["config"]["digest"])
```

<!-- END SNIPPET -->


## Troubleshooting

For infomation about troubleshooting, refer to the [troubleshooting guide].
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
[troubleshooting guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/TROUBLESHOOTING.md
