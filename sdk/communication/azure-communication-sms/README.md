# Azure Communication SMS Package client library for Python

This package contains a Python SDK for Azure Communication Services for SMS.
Read more about Azure Communication Services [here](https://docs.microsoft.com/azure/communication-services/overview)

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-sms) | [Package (Pypi)](https://pypi.org/project/azure-communication-sms/) | [API reference documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/communication/azure-communication-sms) | [Product documentation](https://docs.microsoft.com/azure/communication-services/quickstarts/telephony-sms/send?pivots=programming-language-python)

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites

- Python 3.7 or later is required to use this package.
- A deployed Communication Services resource. You can use the [Azure Portal](https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp) or the [Azure PowerShell](https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice) to set it up.
- You must have a phone number configured that is associated with an Azure subscription

### Install the package

Install the Azure Communication SMS client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-sms
```

## Key concepts

Azure Communication SMS package is used to do following:
- Send a 1:1 SMS Message
- Send a 1:N SMS Message

## Examples

The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

- [Client Initialization](#client-initialization)
- [Send a 1:1 SMS Message](#send-a-11-sms-message)
- [Send a 1:N SMS Message](#send-a-1n-sms-message)

### Client Initialization

To initialize the SMS Client, the connection string can be used to instantiate.
Alternatively, you can also use Active Directory authentication using DefaultAzureCredential.

```Python
from azure.communication.sms import SmsClient
from azure.identity import DefaultAzureCredential

connection_str = "endpoint=ENDPOINT;accessKey=KEY"
sms_client = SmsClient.from_connection_string(connection_string)

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have
# AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
endpoint = "https://<RESOURCE_NAME>.communication.azure.com"
sms_client = SmsClient(endpoint, DefaultAzureCredential())
```

### Send a 1:1 SMS Message

Once the client is initialized, the `send` method can be invoked:

```Python
from azure.communication.sms import SendSmsOptions

sms_responses = sms_client.send(
    from_="<from-phone-number>",
    to="<to-phone-number-1>",
    message="Hello World via SMS",
    enable_delivery_report=True, # optional property
    tag="custom-tag") # optional property
```

- `from_`: An SMS enabled phone number associated with your communication service.
- `to`: The phone number or list of phone numbers you wish to send a message to.
- `message`: The message that you want to send.
- `enable_delivery_report`: An optional parameter that you can use to configure delivery reporting. This is useful for scenarios where you want to emit events when SMS messages are delivered.
- `tag`: An optional parameter that you can use to configure custom tagging.

### Send a 1:N SMS Message

Once the client is initialized, the `send` method can be invoked:

```Python
from azure.communication.sms import SendSmsOptions

sms_responses = sms_client.send(
    from_="<from-phone-number>",
    to=["<to-phone-number-1>", "<to-phone-number-2>", "<to-phone-number-3>"],
    message="Hello World via SMS",
    enable_delivery_report=True, # optional property
    tag="custom-tag") # optional property
```

- `from_`: An SMS enabled phone number associated with your communication service.
- `to`: The phone number or list of phone numbers you wish to send a message to.
- `message`: The message that you want to send.
- `enable_delivery_report`: An optional parameter that you can use to configure delivery reporting. This is useful for scenarios where you want to emit events when SMS messages are delivered.
- `tag`: An optional parameter that you can use to configure custom tagging.


## Troubleshooting
SMS operations will throw an exception if the request to the server fails. The SMS client will raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md). Exceptions will not be thrown if the error is caused by an individual message, only if something fails with the overall request. Please use the successful flag to validate each individual result to verify if the message was sent.

```Python
try:
    sms_responses = sms_client.send(
        from_="<leased-phone-number>",
        to=["<to-phone-number-1>", "<to-phone-number-2>", "<to-phone-number-3>"],
        message="Hello World via SMS")

    for sms_response in sms_responses:
        if (sms_response.successful):
            print("Message with message id {} was successful sent to {}"
            .format(sms_response.message_id, sms_response.to))
        else:
            print("Message failed to send to {} with the status code {} and error: {}"
            .format(sms_response.to, sms_response.http_status_code, sms_response.error_message))
except Exception as ex:
    print('Exception:')
    print(ex)
```

## Next steps
- [Read more about SMS in Azure Communication Services][next_steps]
- For a basic guide on how to configure Delivery Reporting for your SMS messages please refer to the [Handle SMS Events quickstart][handle_sms_events].

### More sample code

Please take a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/communication/azure-communication-sms/samples) directory for detailed examples of how to use this library to send an sms.

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
[handle_sms_events]: https://docs.microsoft.com/azure/communication-services/quickstarts/telephony-sms/handle-sms-events
[next_steps]:https://docs.microsoft.com/azure/communication-services/quickstarts/telephony-sms/send?pivots=programming-language-python