# Azure Purview Sharing client library for Python

Microsoft Purview Share is a fully managed cloud service.

**Please rely heavily on the [service's documentation][sharing_product_documentation] and our [protocol client docs][protocol_client_quickstart] to use this library**

[Source code][source_code] | [Package (PyPI)][client_pypi_package] | [Product documentation][sharing_product_documentation]

## Getting started

### Install the package

Install the Azure Purview Sharing client library for Python with [pip][pip]:

```bash
pip install azure-purview-sharing
```

### Prerequisites

- You must have an [Azure subscription][azure_subscription] and a [Purview resource][purview_resource] to use this package.
- Python 3.6 or later is required to use this package.

### Authenticate the client

#### Using Azure Active Directory

This document demonstrates using [DefaultAzureCredential][default_cred_ref] to authenticate via Azure Active Directory. However, any of the credentials offered by the [azure_identity][azure_identity] will be accepted.  See the [azure_identity][azure_identity] documentation for more information about other credentials.

Once you have chosen and configured your credential, you can create instances of the `PurviewSharingClient`.

```python
from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = PurviewSharingClient(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
```

## Key concepts

## Examples

The following section shows you how to initialize and authenticate your client and share data.

### Create sent share

```python Snippet:create_a_sent_share
import os, uuid, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

sent_share_id = uuid.uuid4()

artifact = {
    "properties": {
        "paths": [
            {
                "containerName": "container-name",
                "receiverPath": "shared-file-name.txt",
                "senderPath": "original/file-name.txt"
            }
        ]
    },
    "storeKind": "AdlsGen2Account",
    "storeReference": {
        "referenceName": "/subscriptions/{subscription-id}/resourceGroups/provider-storage-rg/providers/Microsoft.Storage/storageAccounts/providerstorage",
        "type": "ArmResourceReference"
    }
}

sent_share = {
    "properties": {
        "artifact": artifact,
        "displayName": "sample=share",
        "description": "A sample share"
    },
    "shareKind": "InPlace"
}

request = client.sent_shares.begin_create_or_replace(
    str(sent_share_id),
    content_type="application/json",
    content=json.dumps(sent_share))

response = request.result()
print(response)
```

### Get sent share

```python Snippet:get_a_sent_share
import os, uuid

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()
sent_share_id = uuid.uuid4()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

retrieved_sent_share = client.sent_shares.get(sent_share_id=str(sent_share_id))
print(retrieved_sent_share)
```

### List sent shares

```python Snippet:get_all_sent_shares
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

provider_storage_account_resource_id = "/subscriptions/{subscription-id}/resourceGroups/provider-storage-rg/providers/Microsoft.Storage/storageAccounts/providerstorage"

list_request = client.sent_shares.list(
    reference_name=provider_storage_account_resource_id,
    orderby="properties/createdAt desc")

list_response = list_request.result()
print(list_response)
```

### Create sent share invitation

```python Snippet:send_a_user_invitation
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential
from datetime import date

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

sent_share_id = uuid.uuid4()
sent_share_invitation_id = uuid.uuid4()

consumerEmail = "consumer@contoso.com"
today = date.today()
invitation = {
    "invitationKind": "User",
    "properties": {
        "targetEmail": consumerEmail,
        "notify": "true",
        "expirationDate": date(today.year+1,today.month,today.day).strftime("%Y-%m-%d") + " 00:00:00"
    }
}

invitation_request = client.sent_shares.create_invitation(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id),
    sent_share_invitation=json.dumps(invitation))

invitation_response = invitation_request.result()
created_invitation = json.loads(invitation_response)
print(created_invitation)
```

### List sent share invitations

```python Snippet:view_sent_invitations
import os, uuid, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

sent_share_id = uuid.uuid4()

list_request = client.sent_shares.list_invitations(sent_share_id=str(sent_share_id))
list_response = list_request.result()
result_list = json.loads(list_response)
print(result_list)
```

### List detached received shares

```python Snippet:get_all_detached_received_shares
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

list_detached_response = client.received_shares.list_detached(orderby="properties/createdAt desc")
print(list_detached_response)
```

### Create a received share

```python Snippet:attach_a_received_share
import os, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

consumer_storage_account_resource_id = "/subscriptions/{subscription-id}/resourceGroups/consumer-storage-rg/providers/Microsoft.Storage/storageAccounts/consumerstorage"

list_detached_response = client.received_shares.list_detached(orderby="properties/createdAt desc")
list_detached = json.loads(list_detached_response)
received_share = list_detached[0]

store_reference = {
    "referenceName": consumer_storage_account_resource_id,
    "type": "ArmResourceReference"
}

sink = {
    "properties": {
        "containerName": "container-test",
        "folder": "folder-test",
        "mountPath": "mountPath-test",
    },
    "storeKind": "AdlsGen2Account",
    "storeReference": store_reference
}

received_share['properties']['sink'] = sink

update_request = client.received_shares.begin_create_or_replace(
    received_share['id'],
    content_type="application/json",
    content=json.dumps(received_share))

update_response = update_request.result()
print(update_response)
```

### Get received share

```python Snippet:get_a_received_share
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

list_detached_response = client.received_shares.list_detached(orderby="properties/createdAt desc")
list_detached = json.loads(list_detached_response)
received_share = list_detached[0]

get_share_response = client.received_shares.get(received_share_id=received_share['id'])
retrieved_share = json.loads(get_share_response)
print(retrieved_share)
```

### List attached received shares

```python Snippet:list_attached_received_shares
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

consumer_storage_account_resource_id = "/subscriptions/{subscription-id}/resourceGroups/consumer-storage-rg/providers/Microsoft.Storage/storageAccounts/consumerstorage"

list_attached_response = client.received_shares.list_attached(
    reference_name=consumer_storage_account_resource_id,
    orderby="properties/createdAt desc")
print(list_attached_response)
```

### Delete received share

```python Snippet:delete_a_received_share
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

delete_received_share_request = client.received_shares.begin_delete(received_share_id=received_share['id'])
delete_received_share_response = delete_received_share_request.result()
print(delete_received_share_response)
```

### Delete sent share

```python Snippet:delete_a_sent_share
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

sent_share_id="885E60CB-2001-4192-B95D-B98CE316C783"

delete_request = client.sent_shares.begin_delete(sent_share_id=str(sent_share_id))
delete_response = delete_request.result()
print(delete_response)
```

## Troubleshooting

### General

The Purview Catalog client will raise exceptions defined in [Azure Core][azure_core] if you call `.raise_for_status()` on your responses.

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:

```python
import sys
import logging
from azure.identity import DefaultAzureCredential
from azure.purview.sharing import PurviewSharingClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-account-name>.share.purview.azure.com"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = PurviewSharingClient(endpoint=endpoint, credential=credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single `send_request` call,
even when it isn't enabled for the client:

```python
result = client.types.get_all_type_definitions(logging_enable=True)
```

## Next steps

For more generic samples, see our [samples][samples].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/purview/azure-purview-sharing/azure/purview/sharing
[client_pypi_package]: https://aka.ms/azsdk/python/purviewsharing/pypi
[sharing_ref_docs]: https://aka.ms/azsdk/python/purviewcatalog/ref-docs
[sharing_product_documentation]: https://azure.microsoft.com/services/purview/
[azure_subscription]: https://azure.microsoft.com/free/
[purview_resource]: https://docs.microsoft.com/azure/purview
[pip]: https://pypi.org/project/pip/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[request_builders_and_client]: https://aka.ms/azsdk/python/protocol/quickstart
[enable_aad]: https://docs.microsoft.com/azure/purview/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[python_logging]: https://docs.python.org/3.5/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[samples]: https://github.com/yamanwahsheh/azure-sdk-for-python/tree/yaman/share-v2-python-tests-and-samples/sdk/purview/azure-purview-sharing/samples