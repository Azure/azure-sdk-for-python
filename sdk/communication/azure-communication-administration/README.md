[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=master)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=master)

# Azure Communication Administration Package client library for Python

Azure Communication Administration client package is intended to be used to setup the basics for opening a way to use Azure Communication Service offerings. This package helps to create identities user tokens to be used by other client packages such as chat, calling, sms. 

# Getting started
### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/)

### Install the package
Install the Azure Communication Administration client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-communication-administration
```

# Key concepts
## CommunicationIdentityClient
`CommunicationIdentityClient` provides operations for:

- Create/delete identities to be used in Azure Communication Services. Those identities can be used to make use of Azure Communication offerings and can be scoped to have limited abilities through token scopes.

- Create/revoke scoped user access tokens to access services such as chat, calling, sms. Tokens are issued for a valid Azure Communication identity and can be revoked at any time.

# Examples
The following section provides several code snippets covering some of the most common Azure Communication Services tasks, including:

<!-- [Create/delete Azure Communication Services identities](#identity_samples) -->

<!-- [Create/revoke scoped user access tokens](#identity_samples) -->

# Troubleshooting

# Next steps

# Contributing

<!-- LINKS -->
<!--TODO: add links -->
[identity_samples]: []
