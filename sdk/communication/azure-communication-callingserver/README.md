# Azure Communication CallingServer Package client library for Python

This package contains a Python SDK for Azure Communication Services for CallingServer.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview)


## Getting started

### Prerequisites

- Python 2.7, or 3.6 or later is required to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
- You must have a phone number configured that is associated with an Azure subscription

### Install the package

Install the Azure Communication CallingServer client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-callingserver
```

## Key concepts

`CallingServerClient` provides the functionality to make call connection, join call connection or initialize a server call.

## Examples

The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

- [Client Initialization](#client-initialization)
- [Make a call to a phone number recipient](#make-a-call-to-a-phone-number-recipient)

### Client Initialization

To initialize the CallingServer Client, the connection string can be used to instantiate.

```Python
from azure.communication.callingserver import CallingServerClient

connection_str = "endpoint=ENDPOINT;accessKey=KEY"
callingserver_client = CallingServerClient.from_connection_string(connection_string)

```

### Make a call to a phone number recipient

Once the client is initialized, the `createCallConnection` method can be invoked:

```Python
from azure.communication.callingserver import CreateCallOptions

sms_responses = callingserver_client.createCallConnection(
    source="<from-phone-number>",
    targets="<to-phone-number-1>",
    createCallOptions=Something)
```

- `from_`: Something.
- `to`: Something.
- `createCallOptions`: Something.


## Troubleshooting

Running into issues? This section should contain details as to what to do there.

## Next steps

More sample code should go here, along with links out to the appropriate example tests.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the
PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
