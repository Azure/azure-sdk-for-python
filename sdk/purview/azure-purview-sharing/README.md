# Azure Purview Sharing client library for Python

Microsoft Purview Share is a fully managed cloud service.

**Please rely heavily on the [service's documentation][sharing_product_documentation] and our [protocol client docs][request_builders_and_client] to use this library**

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

This document demonstrates using [DefaultAzureCredential][default_azure_credential] to authenticate via Azure Active Directory. However, any of the credentials offered by the [azure-identity package][azure_identity_pip] will be accepted.  See the [azure-identity][azure_identity_credentials] documentation for more information about other credentials.

Once you have chosen and configured your credential, you can create instances of the `PurviewSharingClient`.

```python
from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = PurviewSharingClient(endpoint="https://<my-account-name>.purview.azure.com", credential=credential)
```

## Key concepts

**Data Provider:** A data provider is the individual who creates a share by selecting a data source, choosing which files and folders to share, and who to share them with. Microsoft Purview then sends an invitation to each data consumer.

**Data Consumer:** A data consumer is the individual who accepts the invitation by specifying a target storage account in their own Azure subscription that they'll use to access the shared data.

## Examples

Table of Contents: 
- [Data Provider](#data-provider-examples)
- [Data Consumer](#data-consumer-examples)
- [Share Resource](#share-resource-examples)

## Data Provider Examples

The following code examples demonstrate how data providers can use the Microsoft Azure Python SDK for Purview Sharing to manage their sharing activity.

### Create a Sent Share Client

```python Snippet:create_a_sent_share_client
import os, uuid, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)
```

### Create Share

To begin sharing data, the data provider must first create a sent share that identifies the data they would like to share.

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
        "displayName": "sampleShare",
        "description": "A sample share"
    },
    "shareKind": "InPlace"
}

request = client.sent_shares.begin_create_or_replace(
    str(sent_share_id),
    sent_share=sent_share)

response = request.result()
print(response)
```

### Send Share Invitation to a User

After creating a sent share, the data provider can extend invitations to consumers who may then view the shared data. In this example, an invitation is extended to an individual by specifying their email address.

```python Snippet:send_a_user_invitation
import os, uuid

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
    sent_share_invitation=invitation)

invitation_response = invitation_request.result()
created_invitation = json.loads(invitation_response)
print(created_invitation)
```
### Send Share Invitation to a Service

Data providers can also extend invitations to services or applications by specifying the tenant id and object id of the service. _The object id used for sending an invitation to a service must be the object id associated with the Enterprise Application (not the application registration)._

```python Snippet:send_a_service_invitation
import os, uuid

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

targetActiveDirectoryId = uuid.uuid4()
targetObjectId = uuid.uuid4()

sent_share_invitation = {
    "invitationKind": "Service",
    "properties": {
        "targetActiveDirectoryId": str(targetActiveDirectoryId),
        "targetObjectId": str(targetObjectId)
    }
}

invitation_response = client.sent_shares.create_invitation(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id),
    sent_share_invitation=sent_share_invitation)

print(invitation_response)
```

### Get Sent Share

After creating a sent share, data providers can retrieve it.

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

### List Sent Shares

Data providers can also retrieve a list of the sent shares they have created.

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
    order_by="properties/createdAt desc")

for list_response in list_request:
    print(list_response)
```

### Delete Sent Share

A sent share can be deleted by the data provider to stop sharing their data with all data consumers.

```python Snippet:delete_a_sent_share
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

sent_share_id = uuid.uuid4()

delete_request = client.sent_shares.begin_delete(sent_share_id=str(sent_share_id))
delete_response = delete_request.result()
print(delete_response)
```

### Get Sent Share Invitation

After creating a sent share invitation, data providers can retrieve it.

```python Snippet:get_a_sent_share_invitation
import os, uuid, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

sent_share_id = uuid.uuid4()
sent_share_invitation_id = uuid.uuid4()

get_invitation_response = client.sent_shares.get_invitation(
    sent_share_id=str(sent_share_id), 
    sent_share_invitation_id=str(sent_share_invitation_id))

retrieved_share_invitation = json.loads(get_invitation_response)
print(retrieved_share_invitation)
```

### List Sent Share Invitations

Data providers can also retrieve a list of the sent share invitations they have created.

```python Snippet:view_sent_invitations
import os, uuid, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint, credential=credential)

sent_share_id = uuid.uuid4()

list_request = client.sent_shares.list_invitations(sent_share_id=str(sent_share_id))

for list_response in list_request:
    print(list_response)
```

### Delete Sent Share Invitation

An individual sent share invitation can be deleted by the data provider to stop sharing their data with the specific data consumer to whom the invitation was addressed.

```python Snippet:delete_a_sent_share_invitation
import os, uuid, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

sent_share_id = uuid.uuid4()
sent_share_invitation_id = uuid.uuid4()

delete_invitation_request = client.sent_shares.begin_delete_invitation(
    sent_share_id=str(sent_share_id),
    sent_share_invitation_id=str(sent_share_invitation_id))
delete_invitation_response = delete_invitation_request.result()
print(delete_invitation_response)
```

## Data Consumer Examples

The following code examples demonstrate how data consumers can use the Microsoft Azure Python SDK for Purview Sharing to manage their sharing activity.

### Create a Received Share Client

```python Snippet:create_received_share_client
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)
```

### List Detached Received Shares

To begin viewing data shared with them, a data consumer must first retrieve a list of detached received shares. Within this list, they can identify a detached received share to attach. A "detached" received share refers to a received share that has never been attached or has been detached.

```python Snippet:get_all_detached_received_shares
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

list_detached_response = client.received_shares.list_detached(order_by="properties/createdAt desc")
print(list_detached_response)
```

### Attach a Received Share

Once the data consumer has identified a received share, they can attach the received share to a location where they can access the shared data. If the received share is already attached, the shared data will be made accessible at the new location specified.

```python Snippet:attach_a_received_share
import os, json

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

consumer_storage_account_resource_id = "/subscriptions/{subscription-id}/resourceGroups/consumer-storage-rg/providers/Microsoft.Storage/storageAccounts/consumerstorage"

list_detached_response = client.received_shares.list_detached(order_by="properties/createdAt desc")
received_share = next(x for x in list_detached_response)

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

### Get Received Share

A data consumer can retrieve an individual received share.

```python Snippet:get_a_received_share
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

list_detached_response = client.received_shares.list_detached(order_by="properties/createdAt desc")
list_detached = json.loads(list_detached_response)
received_share = list_detached[0]

get_share_response = client.received_shares.get(received_share_id=received_share['id'])
retrieved_share = json.loads(get_share_response)
print(retrieved_share)
```

### List Attached Received Shares

Data consumers can also retrieve a list of their attached received shares.

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
    order_by="properties/createdAt desc")
print(list_attached_response)
```

### Delete Received Share

A received share can be deleted by the data consumer to terminate their access to shared data.

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

## Share Resource Examples

The following code examples demonstrate how to use the Microsoft Azure Python SDK for Purview Sharing to view share resources. A share resource is the underlying resource from which a provider shares data or the destination where a consumer attaches data shared with them.

### List Share Resources

A list of share resources can be retrieved to view all resources within an account where sharing activities have taken place.

```python Snippet:list_share_resources
import os

from azure.purview.sharing import PurviewSharingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["ENDPOINT"]
credential = DefaultAzureCredential()

client = PurviewSharingClient(endpoint=endpoint,credential=credential)

list_request = client.share_resources.list(
    filter="properties/storeKind eq 'AdlsGen2Account'",
    order_by="properties/createdAt desc")

for list_response in list_request:
    print(list_response)
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
[client_pypi_package]: https://pypi.org/project/azure-purview-sharing/
[sharing_ref_docs]: https://aka.ms/azsdk/python/purviewcatalog/ref-docs
[sharing_product_documentation]: https://azure.microsoft.com/services/purview/
[azure_subscription]: https://azure.microsoft.com/free/
[purview_resource]: https://learn.microsoft.com/purview/
[pip]: https://pypi.org/project/pip/
[authenticate_with_token]: https://learn.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/latest/azure.identity.html#azure.identity.DefaultAzureCredential
[request_builders_and_client]: https://aka.ms/azsdk/python/protocol/quickstart
[enable_aad]: https://learn.microsoft.com/purview/
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[python_logging]: https://docs.python.org/3.5/library/logging.html
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/purview/azure-purview-sharing/samples
