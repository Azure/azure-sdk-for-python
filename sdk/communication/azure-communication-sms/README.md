[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure SMS client library for Python

Azure Communication SMS client package is intended to be used to send SMS using an Azure Resource. 

# Getting started

## Prerequisites

* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/)
* You must have a phone number configured that is associated with an Azure subscription

## Install the package

Install the Azure Communication SMS client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-sms --pre
```

# Key concepts

Azure Communication SMS package is used to do following:
- Send an SMS

# Examples

The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

<!-- - [Client Initialization](#client-initialization)
- [Sending an SMS](#sending-an-sms) -->

## Client Initialization

To initialize the SMS Client, the connection string can be used to instantiate:

```Python
connection_string = "COMMUNICATION_SERVICES_CONNECTION_STRING"
sms_client = SmsClient.from_connection_string(connection_string)
```

## Sending an SMS

Once the client is initialized, the `.send()` method can be invoked:

```Python
smsresponse = sms_client.send(
    from_phone_number=PhoneNumber("<leased-phone-number>"),
    to_phone_numbers=[PhoneNumber("<to-phone-number>")],
    message="Hello World via SMS",
    send_sms_options=SendSmsOptions(enable_delivery_report=True)) # optional property
```

- `leased-phone-number`: an SMS enabled phone number associated with your communication service
- `to-phone-number`: the phone number you wish to send a message to
- `send_sms_options`: an optional parameter that you can use to configure Delivery Reporting. This is useful for scenarios where you want to emit events when SMS messages are delivered.

# Troubleshooting

Running into issues? This section should contain details as to what to do there.

# Next steps

More sample code should go here, along with links out to the appropriate example tests.

# Contributing

If you encounter any bugs or have suggestions, please file an issue in the [Issues](<https://github.com/Azure/azure-sdk-for-python/issues>) section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)