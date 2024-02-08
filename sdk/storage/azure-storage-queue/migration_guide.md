# Storage Queue Service SDK Migration Guide from <= 2.x to 12.x

In this section, we list the main changes you need to be aware of when converting your Storage Queue SDK library from version <= 2.X to version 12.X.
In version 12 we also support asynchronous APIs.

## Converting Core Classes
<= 2.X synchronous classes have been replaced. Some functionality has been split into separate clients for more logical organization.

| <= 2.X Classes (Clients)  | V12 Clients | NEW Asynchronous clients |
|---:|---:|---:|
| QueueService (account-level operations) | QueueServiceClient | aio.QueueServiceClient |
| QueueService (queue-level operations) | QueueClient   | aio.QueueClient |

## Version <= 2.X to Version 12 API Mapping

<table border="1" cellspacing="0" cellpadding="0">
    <tbody>
        <tr>
            <td width="353" colspan="2" valign="top">
                <p align="right">
                    Version &lt;= 2.X
                </p>
            </td>
            <td width="270" colspan="2" valign="top">
                <p align="right">
                    Version 12.X
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    API Name
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    Class(es) it belongs to
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    API Name
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    Class(es) it belongs to
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_account_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_account_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.queue directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    generate_queue_shared_access_signature
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    generate_queue_sas
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    It’s not a class method.
                </p>
                <p align="right">
                    Just import from azure.storage.queue directly
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_queue_service_stats
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_service_stats
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_queue_service_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_service_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_queue_service_properties
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_service_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    list_queues
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    list_queues
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    create_queue
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    create_queue
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient or QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    delete_queue
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_queue
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient or QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_queue_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_queue_properties
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueServiceClient or QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_queue_metadata
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_queue_metadata
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    exists
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    N/A
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    N/A
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_queue_acl
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    get_queue_access_policy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    set_queue_acl
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    set_queue_access_policy
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    put_message
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    send_message
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    get_messages
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    receive_messages
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    peek_messages
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    peek_messages
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    delete_message
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    delete_message
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    clear_messages
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    clear_messages
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
        <tr>
            <td width="242" valign="top">
                <p align="right">
                    update_message
                </p>
            </td>
            <td width="111" valign="top">
                <p align="right">
                    QueueService
                </p>
            </td>
            <td width="163" valign="top">
                <p align="right">
                    update_message
                </p>
            </td>
            <td width="107" valign="top">
                <p align="right">
                    QueueClient
                </p>
            </td>
        </tr>
    </tbody>
</table>

## Build Client with Shared Key Credential
Instantiate client in Version 2.X
```python
from azure.storage.queue import QueueService
service = QueueService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
```

Instantiate client in Version 12.
```python
from azure.storage.queue import QueueServiceClient

service = QueueServiceClient(account_url="https://<my-storage-account-name>.queue.core.windows.net/", credential={'account_name': "<storage-account-name>", 'account_key': "<account-access-key>"})
```

## Build Client with SAS token

In version 2.X, to generate the SAS token, you needed to instantiate `QueueService`, then use the class method to generate the sas token.
```python
from azure.storage.queue import QueueService
from azure.storage.common import (
    ResourceTypes,
    AccountPermissions,
)
from datetime import datetime, timedelta

service = QueueService("<storage-account-name>", "<account-access-key>", endpoint_suffix="<endpoint_suffix>")
                        
token = service.generate_account_shared_access_signature(
    ResourceTypes.CONTAINER,
    AccountPermissions.READ,
    datetime.utcnow() + timedelta(hours=1),
)

# Create a service and use the SAS
sas_service = QueueService(
    account_name="<storage-account-name>",
    sas_token=token,
)
```

In V12, SAS token generation is a standalone api, it's no longer a class method.
```python
from datetime import datetime, timedelta
from azure.storage.queue import QueueServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions

sas_token = generate_account_sas(
    account_name="<storage-account-name>",
    account_key="<account-access-key>",
    resource_types=ResourceTypes(service=True),
    permission=AccountSasPermissions(read=True),
    expiry=datetime.utcnow() + timedelta(hours=1)
)

queue_service_client = QueueServiceClient(account_url="https://<my_account_name>.queue.core.windows.net", credential=sas_token)
```

## Build Client with OAuth Credentials
V 2.X using oauth credential to instantiate a service client.
```python
from azure.storage.common import (
    TokenCredential,
)
import adal

context = adal.AuthenticationContext(
    str.format("{}/{}", "<active_directory_auth_endpoint>", "<active_directory_tenant_id>"),
    api_version=None, validate_authority=True)

token = context.acquire_token_with_client_credentials(
    "https://storage.azure.com",
    "<active_directory_application_id>",
    "<active_directory_application_secret>")["accessToken"]
token_credential = TokenCredential(token)

service = QueueService("<storage_account_name>", token_credential=token_credential)
```

In V12, you can leverage the azure-identity package.
```python
from azure.identity import DefaultAzureCredential
token_credential = DefaultAzureCredential()

# Instantiate a QueueServiceClient using a token credential
from azure.storage.queue import QueueServiceClient
queue_service_client = QueueServiceClient("https://<my-storage-account-name>.queue.core.windows.net", credential=token_credential)
```
