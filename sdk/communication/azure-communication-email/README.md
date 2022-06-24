# Azure Communication Email client library for Python

This package contains a Python SDK for Azure Communication Services for Email.

## Key concepts

The Azure Communication Email package is used to do following:
- Send emails to multiple types of recipients
- Query the status of a sent email message

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

`EmailClient` provides the functionality to send email messages .

## Authentication

Email clients can be authenticated using the connection string acquired from an Azure Communication Resource in the [Azure Portal][azure_portal].

```python
from azure.communication.email import EmailClient

connection_string = "endpoint=https://<resource-name>.communication.azure.com/;accessKey=<Base64-Encoded-Key>"
client = EmailClient.from_connection_string(connection_string);
```

### Send an Email Message

To send an email message, call the `send` function from the `EmailClient`.

```python
content = EmailContent(
    subject="This is the subject",
    plain_text="This is the body",
    html= "<html><h1>This is the body</h1></html>",
)

address = EmailAddress(email="customer@domain.com", display_name="Customer Name")

message = EmailMessage(
            sender="sender@contoso.com",
            content=content,
            recipients=EmailRecipients(to=[address])
        )

response = client.send(message)
```

### Send an Email Message to Multiple Recipients

To send an email message to multiple recipients, add a object for each recipient type and an object for each recipient.

```python
content = EmailContent(
    subject="This is the subject",
    plain_text="This is the body",
    html= "<html><h1>This is the body</h1></html>",
)

recipients = EmailRecipients(
        to=[
            EmailAddress(email="customer@domain.com", display_name="Customer Name"),
            EmailAddress(email="customer2@domain.com", display_name="Customer Name 2"),
        ],
        cc=[
            EmailAddress(email="ccCustomer@domain.com", display_name="CC Customer Name"),
            EmailAddress(email="ccCustomer2@domain.com", display_name="CC Customer Name 2"),
        ],
        bcc=[
            EmailAddress(email="bccCustomer@domain.com", display_name="BCC Customer Name"),
            EmailAddress(email="bccCustomer2@domain.com", display_name="BCC Customer Name 2"),
        ]
    )

message = EmailMessage(sender="sender@contoso.com", content=content, recipients=recipients)
response = client.send(message)
```

### Send Email with Attachments

Azure Communication Services support sending email with attachments.

```python
file = open("C://readme.txt", "r")
file_contents = file.read()
file.close()

content = EmailContent(
    subject="This is the subject",
    plain_text="This is the body",
    html= "<html><h1>This is the body</h1></html>",
)

address = EmailAddress(email="customer@domain.com", display_name="Customer Name")

attachment = EmailAttachment(
    name="readme.txt",
    attachment_type="txt",
    content_bytes_base64=base64.b64encode(file_contents)
)

message = EmailMessage(
            sender="sender@contoso.com",
            content=content,
            recipients=EmailRecipients(to=[address]),
            attachments=[attachment]
        )

response = client.send(message)
```

### Get Email Message Status

The result from the `send` call contains a `message_id` which can be used to query the status of the email.

```python
response = client.send(message)
status = client.get_sent_status(message_id)
```

## Troubleshooting

Email operations will throw an exception if the request to the server fails. The Email client will raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md).

```Python
try:
    response = email_client.send(message)
except Exception as ex:
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
[cla]: https://cla.microsoft.com
[coc]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[communication_resource_docs]: https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp
[email_resource_docs]: https://aka.ms/acsemail/createemailresource
[communication_resource_create_portal]: https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-azp
[communication_resource_create_power_shell]: https://docs.microsoft.com/powershell/module/az.communication/new-azcommunicationservice
[communication_resource_create_net]: https://docs.microsoft.com/azure/communication-services/quickstarts/create-communication-resource?tabs=windows&pivots=platform-net
[package]: https://www.nuget.org/packages/Azure.Communication.Common/
[product_docs]: https://aka.ms/acsemail/overview
[nextsteps]: https://aka.ms/acsemail/overview
[nuget]: https://www.nuget.org/
[source]: https://github.com/Azure/azure-sdk-for-net/tree/main/sdk/communication
[domain_overview]: https://aka.ms/acsemail/domainsoverview
