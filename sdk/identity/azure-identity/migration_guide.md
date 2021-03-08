# Guide for migrating to azure-identity from azure-common

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

[authenticate_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-authenticate?tabs=cmd
[client_from_json]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-json-dict-client-class--config-dict----kwargs-
[client_from_auth_file]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_secret_cred]: https://docs.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python
[json]: https://docs.python.org/3/library/json.html#json.load
