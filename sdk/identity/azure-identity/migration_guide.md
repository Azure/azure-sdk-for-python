# Guide for migrating to azure-identity from azure-common

The newest Azure SDK libraries (the "client" and "management" libraries
[listed here](https://azure.github.io/azure-sdk/releases/latest/python.html))
use credentials from `azure-identity` to authenticate requests. Older versions
of these libraries typically used credentials from `azure-common`. Credential
types from these two libraries have different APIs, causing clients to raise
`AttributeError` when given a credential from the wrong library. For example, a
client expecting an `azure-identity` credential will raise an error like
`'ServicePrincipalCredentials' object has no attribute 'get_token'` when given a
credential from `azure-common`. A client expecting an `azure-common` credential
will raise an error like
`'ClientSecretCredential' object has no attribute 'signed_session'` when given
an `azure-identity` credential.

This document shows common authentication code using `azure-common`, and its
equivalent using `azure-identity`.

## Service principal authentication

`azure-common` uses `ServicePrincipalCredentials` to authenticate a service principal:

```python
from azure.common.credentials import ServicePrincipalCredentials

credential = ServicePrincipalCredentials(client_id, client_secret, tenant=tenant_id)
```

`azure-identity` uses [`ClientSecretCredential`][client_secret_cred] :

```python
from azure.identity import ClientSecretCredential

credential = ClientSecretCredential(tenant_id, client_id, client_secret)
```

## Authenticating through the Azure CLI

`azure-common` provides the
[`get_client_from_cli_profile`][get_client_from_cli_profile] function to
integrate with the Azure CLI for authentication. This code works with older
versions of `azure-mgmt-resource` such as 10.0.0:

```python
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.resource import SubscriptionClient

subscription_client = get_client_from_cli_profile(SubscriptionClient)
```

`azure-identity` integrates with the Azure CLI through its
[`AzureCliCredential`][cli_cred]. This code works with newer versions of
`azure-mgmt-resource`, starting with 15.0.0:

```python
from azure.identity import AzureCliCredential
from azure.mgmt.resource import SubscriptionClient

credential = AzureCliCredential()
subscription_client = SubscriptionClient(credential)
```

## JSON- and file-based authentication

To encourage best security practices, `azure-identity` does not support JSON- and file-based authentication in the same
way as `azure-common`. `azure-common` provided factory methods like [`get_client_from_json_dict`][client_from_json] and
[`get_client_from_auth_file`][client_from_auth_file] that are no longer available in `azure-identity`.

In `azure-common` you could provide credentials in a JSON dictionary, or from a JSON file:
```python
from azure.common.client_factory import get_client_from_json_dict, get_client_from_auth_file
from azure.mgmt.keyvault import KeyVaultManagementClient
# Provide credentials in JSON:
json_dict = {
    "clientId": "...",
    "clientSecret": "...",
    "subscriptionId": "...",
    "tenantId": "...",
    "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
    "resourceManagerEndpointUrl": "https://management.azure.com"
}
client = get_client_from_json_dict(KeyVaultManagementClient, json_dict)
# Or, provide credentials from a JSON file:
client = get_client_from_auth_file(KeyVaultManagementClient, "credentials.json")
```

If it's not possible to immediately migrate from file-based authentication, you can still use `azure-identity`. With a
JSON file containing your credentials, you can use [`json.load`][json] to authenticate a service principal with a
[`ClientSecretCredential`][client_secret_cred]:
```python
import json
from azure.identity import ClientSecretCredential
from azure.mgmt.keyvault import KeyVaultManagementClient

with open("credentials.json") as json_file:
    json_dict = json.load(json_file)

credential = ClientSecretCredential(
    tenant_id=json_dict["tenantId"],
    client_id=json_dict["clientId"],
    client_secret=json_dict["clientSecret"],
    authority=json_dict["activeDirectoryEndpointUrl"]
)
client = KeyVaultManagementClient(
    credential,
    json_dict["subscriptionId"],
    base_url=json_dict["resourceManagerEndpointUrl"],
    credential_scopes=["{}/.default".format(json_dict["resourceManagerEndpointUrl"])]
)
```

If storing credentials in a file, be sure to protect access to this file. Make certain that it's excluded by version
control -- for example, by adding the credential file name to your project's `.gitignore` file.

The global documentation for authenticating Python apps on Azure is available [here][authenticate_docs].

[authenticate_docs]: https://docs.microsoft.com/azure/developer/python/sdk/authentication-overview?tabs=cmd
[cli_cred]: https://aka.ms/azsdk/python/identity/docs#azure.identity.AzureCliCredential
[client_from_json]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-json-dict-client-class--config-dict----kwargs-
[client_from_auth_file]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_secret_cred]: https://aka.ms/azsdk/python/identity/docs#azure.identity.ClientSecretCredential
[get_client_from_cli_profile]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-cli-profile-client-class----kwargs-
[json]: https://docs.python.org/3/library/json.html#json.load

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fidentity%2Fazure-identity%2Fmigration_guide.png)
