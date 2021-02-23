# Guide for migrating to azure-identity from azure-common

## JSON- and file-based authentication

To encourage best security practices, `azure-identity` does not support JSON- and file-based authentication in the same
way as `azure-common`. `azure-common` provided factory methods like [`get_client_from_json_dict`][client_from_json] and
[`get_client_from_auth_file`][client_from_auth_file] to provide credentials as plaintext JSON. Azure credentials, like
passwords, should not be stored in plaintext whenever possible. Instead, `azure-identity` encourages using environment
variables.

In `azure-common` you could provide credentials in a JSON dictionary, or from a JSON file:
```python
from azure.common.client_factory import get_client_from_json_dict, get_client_from_auth_file
from azure.keyvault import KeyVaultClient

# Provide credentials in JSON:
json_dict = {
    "clientId": "...",
    "clientSecret": "...",
    "tenantId": "...",
    "activeDirectoryEndpointUrl": "https://login.microsoftonline.com"
}
client = get_client_from_json_dict(KeyVaultClient, json_dict)

# Or, provide credentials from a JSON file:
client = get_client_from_auth_file(KeyVaultClient, "auth_file.json")
```

In `azure-identity`, you can provide credentials through environment variables. After setting `AZURE_CLIENT_ID`,
`AZURE_CLIENT_SECRET`, and `AZURE_TENANT_ID` variables with the values used for `clientId`, `clientSecret`, and
`tenantId`, you can do the following:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()
client = CertificateClient("https://{vault-name}.vault.azure.net", credential)
```

The latter approach greatly reduces the chances of accidentally exporting secrets (imagine committing a file with
plaintext credentials to GitHub). It also prevents anyone who can read your files from reading your credentials
directly.

[client_from_json]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_from_auth_file]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
