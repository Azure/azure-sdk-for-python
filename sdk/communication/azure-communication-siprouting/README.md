# Azure Communication SIP routing Package client library for Python

This package contains a Python SDK for Azure Communication Services for SIP.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview).

This package has been tested with Python 2.7, 3.6, 3.7 and 3.8.

For a more complete set of Azure libraries, see https://aka.ms/azsdk/python/all.

# Getting started

### Prerequisites

- Python 2.7, or 3.6 or later is required to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
- You must have a phone number configured that is associated with an Azure subscription

### Install the package

Install the Azure Communication SIP client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-siprouting
```

# Key concepts

Azure Communication SIP package is used to do the following:

- Retrieve SIP configuration
- Update SIP configuration

# Examples

The following section provides several code snippets covering some of the most common SIP configuration tasks, including:

- [Client Initialization](#client-initialization)
- [Retrieve SIP configuration](#retrieve-sip-configuration)
- [Update SIP configuration](#update-sip-configuration)


### Client Initialization: {#client-initialization}

Initialize client with the service endpoint and azure credentials:

```python
from azure.communication.siprouting import SipRoutingClient
from azure.identity import DefaultAzureCredential
# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
endpoint = "https://<RESOURCE_NAME>.communication.azure.com"
sip_client = SipRoutingClient(endpoint,DefaultAzureCredential())
```

Or initialize the client from connection string:

```python
from azure.communication.siprouting import SipRoutingClient
connection_string = "endpoint=ENDPOINT;accessKey=KEY"
sip_client = SipRoutingClient.from_connection_string(connection_string)
```

### Retrieve SIP configuration: {#retrieve-sip-configuration}

Get the current SIP configuration:

```python
result = sip_client.get_sip_configuration()
print(result.trunks)
print(result.routes)
```

### Update SIP configuration: {#update-sip-configuration}

Set new SIP configuration trunks and routes:

```python
result = sip_client.update_sip_configuration(SipConfiguration(NEW_TRUNKS_CONFIGURATION,NEW_ROUTES_CONFIGURATION))
```

### Update SIP trunks: {#update-sip-trunks}

Set new SIP configuration trunks:

```python
result = sip_client.update_sip_configuration(trunks=NEW_TRUNKS_CONFIGURATION)
```

### Update SIP routes: {#update-sip-routes}

Set new SIP configuration routes:

```python
result = sip_client.update_sip_configuration(routes=NEW_ROUTES_CONFIGURATION)
```

# Troubleshooting

The SIP configuration client will raise exceptions defined in [Azure Core][azure_core].

# Next steps

Please take a look at the samples directory for detailed examples of how to use this library.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
