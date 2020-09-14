# Azure Digitaltwins client library for Python
# Introduction

Azure Digital Twins is a developer platform for next-generation IoT solutions that lets you create, run, and manage digital representations of your business environment, securely and efficiently in the cloud. With Azure Digital Twins, creating live operational state representations is quick and cost-effective, and digital representations stay current with real-time data from IoT and other data sources. If you are new to Azure Digital Twins and would like to learn more about the platform, please make sure you check out the Azure Digital Twins [official documentation page](https://docs.microsoft.com/azure/digital-twins/overview).

For an introduction on how to program against the Azure Digital Twins service, visit the [coding tutorial page](https://docs.microsoft.com/en-us/azure/digital-twins/tutorial-code) for an easy step-by-step guide. Visit [this tutorial](https://docs.microsoft.com/azure/digital-twins/tutorial-command-line-app) to learn how to interact with an Azure Digital Twin instance using a command-line client application. Finally, for a quick guide on how to build an end-to-end Azure Digital Twins solution that is driven by live data from your environment, make sure you check out [this helpful guide](https://docs.microsoft.com/azure/digital-twins/tutorial-end-to-end).

The guides mentioned above can help you get started with key elements of Azure Digital Twins, such as creating Azure Digital Twins instances, models, twin graphs, etc. Use this samples guide below to familiarize yourself with the various APIs that help you program against Azure Digital Twins.

# Install packages
Install [azure-digitaltwins][pypi_package_keys] and
[azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-digitaltiwns azure-identity
```
[azure-identity][azure_identity] is used for Azure Active Directory
authentication as demonstrated below.

# Digital Twins Samples

You can explore the digital twins APIs (using the client library) using the samples project.

The samples project demonstrates the following:

- Instantiate the client
- Create, get, and decommission models
- Create, query, and delete a digital twin
- Get and update components for a digital twin
- Create, get, and delete relationships between digital twins
- Create, get, and delete event routes for digital twin
- Publish telemetry messages to a digital twin and digital twin component

## Creating the digital twins client

To create a new digital twins client, you need the endpoint to an Azure Digital Twin instance and credentials.
For the samples below, the `AZURE_URL`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` environment variables have to be set.
The client requires an instance of [TokenCredential](https://docs.microsoft.com/en-us/dotnet/api/azure.core.tokencredential?view=azure-dotnet) or [ServiceClientCredentials](https://docs.microsoft.com/en-us/dotnet/api/microsoft.rest.serviceclientcredentials?view=azure-dotnet).
In this samples, we illustrate how to use one derived class: [DefaultAzureCredentials](https://docs.microsoft.com/en-us/dotnet/api/azure.identity.defaultazurecredential?view=azure-dotnet).

> Note: In order to access the data plane for the Digital Twins service, the entity must be given permissions.
> To do this, use the Azure CLI command: `az dt rbac assign-role --assignee '<user-email | application-id>' --role owner -n '<your-digital-twins-instance>'`


#### Create a client
DefaultAzureCredential supports different authentication mechanisms and determines the appropriate credential type based of the environment it is executing in.
It attempts to use multiple credential types in an order until it finds a working credential.

```python Snippet:dt_create_digitaltwins_service_client.py
# DefaultAzureCredential supports different authentication mechanisms and determines the appropriate credential type based of the environment it is executing in.
# It attempts to use multiple credential types in an order until it finds a working credential.

# - AZURE_URL: The tenant ID in Azure Active Directory
url = os.getenv("AZURE_URL")

# DefaultAzureCredential expects the following three environment variables:
# - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
# - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
# - AZURE_CLIENT_SECRET: The client secret for the registered application
credential = DefaultAzureCredential()
serviceClient = DigitalTwinsClient(url, credential)
```



[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[pip]: https://pypi.org/project/pip/
[pypi_package_digitaltwins]: https://pypi.org/project/azure-digitaltwins/






