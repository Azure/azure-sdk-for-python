# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_helloworld.py

DESCRIPTION:
    This sample demonstrates basic usage of the AzureApp base class.

    This sample includes provisioning the following Azure resources which may incur charges:
    - Azure Resource Group
    - Azure User-Assigned Managed Identity
    - Azure Storage (SKU: Standard_GRS)
    - Azure Storage (SKU: Standard_LRS)
    - Azure Blob Container

    See pricing: https://azure.microsoft.com/pricing/details/storage/blobs/.

USAGE:
    python sample_helloworld.py

    Running the samples requires that Azure Developer CLI be installed and authenticated:
    For more information: https://learn.microsoft.com/azure/developer/azure-developer-cli/
"""
import asyncio
import time

unique_suffix = int(time.time())


async def main():

    # Getting started with a simple app to work with Azure Blob Storage.
    from azure.projects import AzureApp
    from azure.storage.blob import BlobServiceClient

    class MyFirstApp(AzureApp):
        data: BlobServiceClient

    # Next, we can provision some resources for the app client to use.
    # This will create a default resource group, default managed identity, and default storage account
    # with the correct user access roles.
    # The resources will be provisioned by AZD in a new environment named with the app class name.
    # When first provisioning, AZD will prompt you to select a seubscription and default deploy location.
    with MyFirstApp.provision() as first_app:
        container = first_app.data.create_container("samplecontainer")
        container.upload_blob("sampleblob.txt", b"Hello World", overwrite=True)

        # Provisioning an app will automatically create the underlying infrastructure derived
        # from the type hints. To see what resources have been detected, you can inspect the 'infra'
        # attribute.
        print(f"Deployed infrastructure: {first_app.infra}")

    # Onces the resources have been provisioned, we can reload the same environment:
    with MyFirstApp.load() as first_app:
        for container in first_app.data.list_containers():
            first_app.data.delete_container(container)

        # If no longer needed, the infrastructure can be deprovisioned.
        first_app.infra.down()

    # An AzureApp class functions similar to a Python dataclass, so defaults or factories can be provided.
    # Unlike dataclasses, additional keyword-argments can be provided to the field specifier which
    # will be passed into the client constructor (or default factory if provided).
    # The type annotations can use any combination of synchronous or asynchronous clients.
    from azure.projects import field
    from azure.storage.blob.aio import ContainerClient

    class MySecondApp(AzureApp):
        images: ContainerClient = field(logging_enable=True)

    # If we want to configure the underlying infrastructure, we can create an AzureInfrastructure class.
    from azure.projects import AzureInfrastructure
    from azure.projects.resources.resourcegroup import ResourceGroup
    from azure.projects.resources.storage import StorageAccount
    from azure.projects.resources.storage.blobs.container import BlobContainer

    # You can also see and update the default configuration that the resources are deployed with.
    StorageAccount.DEFAULTS["sku"]["name"] = "Standard_LRS"
    print(f"Default Storage configuration: {StorageAccount.DEFAULTS}")

    class MyStorage(AzureInfrastructure):
        blob_storage: StorageAccount = StorageAccount(
            enable_hierarchical_namespace=True, allow_blob_public_access=False, managed_identities=None
        )
        blob_container: BlobContainer = BlobContainer(name="images", metadata={"az_samples": "storage"})

    # Each AzureInfrastructure class comes with a new default resource group and user-assigned managed
    # identity. These can be overridden in the class definition, or overidding values can be provided
    # when the object is constructed.
    infra = MyStorage(
        # Here we will provide a named resource group to create instead of the default one.
        # The default provisioning location can also be overridden per resource.
        resource_group=ResourceGroup(name=f"sampleresourcegroup{unique_suffix}", location="eastus"),
        # We don't need a managed identity for this deployment, so we can override it with None.
        identity=None,
    )

    # We can now specify the exact infrastructure definition to build our app on top of.
    # By default, the class will attempt to map resources in the infrastructure to the client attributes
    # on the app, however you can also provide a mapping, which allows for more fine-grained control, especially
    # if multiple clients are pointing to the same resource.
    app = MySecondApp.provision(infra, attr_map={"images": "blob_container"})

    # An AzureApp instance can be opened in either a synchronous or an asynchronous context manager. On closing
    # the context, all clients in the app will be closed (regardless of whether they are synchronous or asynchronous).
    async with app:
        all_images = [image async for image in app.images.list_blobs()]
        print(f"Container holds {len(all_images)} image files.")

        app.infra.down()


if __name__ == "__main__":
    asyncio.run(main())
