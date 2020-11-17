# Azure App Configuration client library for Python SDK Training

Azure App Configuration is a managed service that helps developers centralize their application configurations simply and securely.

Modern programs, especially programs running in a cloud, generally have many components that are distributed in nature. Spreading configuration settings across these components can lead to hard-to-troubleshoot errors during an application deployment. Use App Configuration to securely store all the settings for your application in one place.

Use the client library for App Configuration to create and manage application configuration settings.

## Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You need an [Azure subscription][azure_sub], and a [Configuration Store][configuration_store] to use this package.

To create a Configuration Store, you can use the Azure Portal or [Azure CLI][azure_cli].

After that, create the Configuration Store:

```Powershell
az appconfig create --name <config-store-name> --resource-group <resource-group-name> --location eastus
```


## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.
