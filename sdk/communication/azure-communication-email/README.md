# Azure Communication Email client library for Python

This package contains a Python SDK for Azure Communication Services for Email.

## Key concepts

The Azure Communication Email package is used to send emails to multiple types of recipients.

## Getting started

### Prerequisites

You need an [Azure subscription][azure_sub], a [Communication Service Resource][communication_resource_docs], and an [Email Communication Resource][email_resource_docs] with an active [Domain][domain_overview].

To create these resource, you can use the [Azure Portal][communication_resource_create_portal], the [Azure PowerShell][communication_resource_create_power_shell], or the [.NET management client library][communication_resource_create_net].

### Installing

Install the Azure Communication Email client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-email
```

## Examples

`EmailClient` provides the functionality to send email messages.

## Authentication

Email clients can be authenticated using the connection string acquired from an Azure Communication Resource in the [Azure Portal][azure_portal].

```python
from azure.communication.email import EmailClient

connection_string = "endpoint=https://<resource-name>.communication.azure.com/;accessKey=<Base64-Encoded-Key>"
client = EmailClient.from_connection_string(connection_string);
```

Alternatively, you can also use Active Directory authentication using DefaultAzureCredential.

```python
from azure.communication.email import EmailClient
from azure.identity import DefaultAzureCredential

# To use Azure Active Directory Authentication (DefaultAzureCredential) make sure to have AZURE_TENANT_ID, AZURE_CLIENT_ID and AZURE_CLIENT_SECRET as env variables.
endpoint = "https://<resource-name>.communication.azure.com"
client = EmailClient(endpoint, DefaultAzureCredential())
```

Email clients can also be authenticated using an [AzureKeyCredential][azure-key-credential].

```python
from azure.communication.email import EmailClient
from azure.core.credentials import AzureKeyCredential

credential = AzureKeyCredential("<api_key>")
endpoint = "https://<resource-name>.communication.azure.com/"
client = EmailClient(endpoint, credential);
```

### Send an Email Message

To send an email message, call the `begin_send` function from the `EmailClient`. This will return a poller. You can use this poller to check on the status of the operation and retrieve the result once it's finished.

```python
message = {
    "content": {
        "subject": "This is the subject",
        "plainText": "This is the body",
        "html": "html><h1>This is the body</h1></html>"
    },
    "recipients": {
        "to": [
            {
                "address": "customer@domain.com",
                "displayName": "Customer Name"
            }
        ]
    },
    "senderAddress": "sender@contoso.com"
}

poller = client.begin_send(message)
result = poller.result()
```

### Send an Email Message to Multiple Recipients

To send an email message to multiple recipients, add a object for each recipient type and an object for each recipient.

```python
message = {
    "content": {
        "subject": "This is the subject",
        "plainText": "This is the body",
        "html": "html><h1>This is the body</h1></html>"
    },
    "recipients": {
        "to": [
            {"address": "customer@domain.com", "displayName": "Customer Name"},
            {"address": "customer2@domain.com", "displayName": "Customer Name 2"}
        ],
        "cc": [
            {"address": "ccCustomer@domain.com", "displayName": "CC Customer Name"},
            {"address": "ccCustomer2@domain.com", "displayName": "CC Customer Name 2"}
        ],
        "bcc": [
            {"address": "bccCustomer@domain.com", "displayName": "BCC Customer Name"},
            {"address": "bccCustomer2@domain.com", "displayName": "BCC Customer Name 2"}
        ]
    },
    "senderAddress": "sender@contoso.com"
}

poller = client.begin_send(message)
result = poller.result()
```

### Send Email with Attachments

Azure Communication Services support sending email with attachments.

```python
import base64

with open("C://readme.txt", "r") as file:
    file_contents = file.read()

file_bytes_b64 = base64.b64encode(bytes(file_contents, 'utf-8'))

message = {
    "content": {
        "subject": "This is the subject",
        "plainText": "This is the body",
        "html": "html><h1>This is the body</h1></html>"
    },
    "recipients": {
        "to": [
            {
                "address": "customer@domain.com",
                "displayName": "Customer Name"
            }
        ]
    },
    "senderAddress": "sender@contoso.com",
    "attachments": [
        {
            "name": "attachment.txt",
            "contentType": "text/plain",
            "contentInBase64": file_bytes_b64.decode()
        }
    ]
}

poller = client.begin_send(message)
result = poller.result()
```

### Send Email with Inline Attachments

Azure Communication Services support sending inline attachments.
Adding an optional `contentId` parameter to an attachment will make it an inline attachment.

```python
import base64

with open("C://inline_image.jpg", "r") as file:
    file_contents = file.read()

file_bytes_b64 = base64.b64encode(bytes(file_contents, 'utf-8'))

message = {
    "content": {
        "subject": "This is the subject",
        "plainText": "This is the body",
        "html": "<html>This is the body<br /><img src=\"cid:my-inline-image\" /></html>"
    },
    "recipients": {
        "to": [
            {
                "address": "customer@domain.com",
                "displayName": "Customer Name"
            }
        ]
    },
    "senderAddress": "sender@contoso.com",
    "attachments": [
        {
            "name": "inline_image.jpg",
            "contentType": "image/jpeg",
            "contentInBase64": file_bytes_b64.decode(),
            "contentId": "my-inline-image"
        }
    ]
}

poller = client.begin_send(message)
result = poller.result()
```

## Troubleshooting

Email operations will throw an exception if the request to the server fails. The Email client will raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

```python
from azure.core.exceptions import HttpResponseError

try:
    response = email_client.send(message)
except HttpResponseError as ex:
    print('Exception:')
    print(ex)
```

## Next steps

- [Read more about Email in Azure Communication Services][nextsteps]

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

This project has adopted the [Microsoft Open Source Code of Conduct][coc]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_sub]: https://azure.microsoft.com/free/dotnet/
[azure_portal]: https://portal.azure.com
[azure-key-credential]: https://aka.ms/azsdk-python-core-azurekeycredential
[cla]: https://cla.microsoft.com
[coc]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[communication_resource_docs]: https://learn.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp
[email_resource_docs]: https://aka.ms/acsemail/createemailresource
[communication_resource_create_portal]: https://learn.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp
[communication_resource_create_power_shell]: https://learn.microsoft.com/powershell/module/az.communication/new-azcommunicationservice
[communication_resource_create_net]: https://learn.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-net
[package]: https://www.nuget.org/packages/Azure.Communication.Common/
[product_docs]: https://aka.ms/acsemail/overview
[nextsteps]: https://aka.ms/acsemail/overview
[nuget]: https://www.nuget.org/
[source]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication
[domain_overview]: https://aka.ms/acsemail/domainsoverview
