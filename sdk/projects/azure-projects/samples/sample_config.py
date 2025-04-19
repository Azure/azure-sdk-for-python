# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_config.py

DESCRIPTION:
    This sample demonstrates how to use a Configuration Store with AzureApp and AzureInfrastructure.

    This sample includes provisioning the following Azure resources which may incur charges:
    - Azure Resource Group
    - Azure User-Assigned Managed Identity
    - Azure Storage (SKU: Standard_GRS)
    - Azure App Configuration (SKU: Free)


    See pricing: https://azure.microsoft.com/pricing/.

USAGE:
    python sample_config.py

    Running the samples requires that Azure Developer CLI be installed and authenticated:
    For more information: https://learn.microsoft.com/azure/developer/azure-developer-cli/
"""
import asyncio
import time
import logging

from azure.projects import deprovision

unique_suffix = int(time.time())


async def main():
    from azure.storage.blob import BlobServiceClient
    from azure.projects import AzureApp

    class SampleApp(AzureApp):
        data: BlobServiceClient

    # The AzureApp base class has a default field called 'config_store', of type Mapping[str, Any].
    # An Azure Projects deployment will by default include an Azure App Configuration resource
    # that will be automatically populated with the resource settings and passed into the AzureApp
    # instance. Note that this is used only for endpoint and resource name/id information, and no secrets
    # are stored there.
    with SampleApp.provision(location="eastus") as app:
        print("\n01. App configuration:")
        for key, value in app.config_store.items():
            print(f"{key}={value}")

    # When calling the load() class method, a config_store Mapping can be passed in to be used for the
    # construction of any client instances. If provided, this will replace any configuration store automatically
    # derived from the deployment infrastructure. In addition to this, when building clients, the constructor will
    # also attempt to load an AZD .env file from a previously provisioned deployment for this app, and read from
    # environment variables.
    # If the settings required to build the clients cannot be resolved, a RuntimeError will be raised.
    with SampleApp.load(config_store={"AZURE_BLOBS_ENDPOINT": "https://alternative.blob.core.windows.net/"}) as app:
        print("\n02. App configuration:")
        for key, value in app.config_store.items():
            print(f"{key}={value}")

    # The default Mapping instance used is a static dict loaded from the config store.
    # If you wish to make more extensive use of the config store beyond resource endpoints, you may
    # could use a dynamic mapping with automatic refresh capabilities, like the
    # AzureAppConfigurationProvider. To change the config_store, just overwrite the field (though note
    # that any change to the type must still support the Mapping protocol).
    from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
    from azure.appconfiguration.provider.aio import AzureAppConfigurationProvider

    class SampleApp(AzureApp):  # type: ignore[no-redef]
        config_store: AzureAppConfigurationProvider
        data: AsyncBlobServiceClient

    async with SampleApp.load() as app:
        print("\n03. App configuration:")
        for key, value in app.config_store.items():
            print(f"{key}={value}")

        deprovision(app, purge=True)

    # If you wish to update the default deployment for the ConfigStore, or add additional settings,
    # this can be done by specifying an AzureInfrastructure definition.
    # You can either overwrite the field definition on the class, or pass in your own custom instance.
    from azure.projects import AzureInfrastructure, field
    from azure.projects.resources.storage.blobs import BlobStorage
    from azure.projects.resources.appconfig import ConfigStore

    class SampleInfra(AzureInfrastructure):
        storage: BlobStorage = BlobStorage()

    # You can use an existing App Configuration Store, though in order to add settings to this store
    # a tole assignment needs to be added to the resource group - so you will need permissions to do that
    # in order for the deployment to succeed.
    # If you don't have such permisisons, you can still use the existing config store, but it will need to
    # be added as a separate field to the Infrastructure definition, and new settings will not be able to be
    # deployed to it.
    infra = SampleInfra(config_store=ConfigStore.reference(name="MyAppConfig", resource_group="MyResourceGroup"))

    # You can also use the config store for other settings relevant to your app
    from azure.projects.resources.appconfig.setting import ConfigSetting

    class SampleInfraLogging(AzureInfrastructure):
        log_level: str = field()
        debug_setting: ConfigSetting = ConfigSetting(name="LOGGING_LEVEL", value=log_level)
        storage: BlobStorage = BlobStorage()

    infra_with_logging = SampleInfraLogging(log_level="INFO")

    async with SampleApp.provision(infra_with_logging) as app:
        print("\n04. App configuration:")
        for key, value in app.config_store.items():
            print(f"{key}={value}")

        logger = logging.getLogger()
        logger.setLevel(app.config_store["LOGGING_LEVEL"])

        deprovision(app, purge=True)

    # If you wish to disable to default Configuration Store resource, this can be done by specifying
    # an AzureInfrastructure defintion, and either overwriting the default field for config_store, or
    # setting the value to None at construction.
    class SampleInfra(AzureInfrastructure):  # type: ignore[no-redef]
        storage: BlobStorage = BlobStorage()

    infra = SampleInfra(config_store=None)

    with SampleApp.provision(infra) as app:
        print("\n05.App configuration:", app.config_store)
        for key, value in app.config_store.items():
            print(f"{key}={value}")

        deprovision(app, purge=True)


if __name__ == "__main__":
    asyncio.run(main())
