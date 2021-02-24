# Guide for migrating to azure-identity from azure-common

## JSON- and file-based authentication

To encourage best security practices, `azure-identity` does not support JSON- and file-based authentication in the same
way as `azure-common`. `azure-common` provided factory methods like [`get_client_from_json_dict`][client_from_json] and
[`get_client_from_auth_file`][client_from_auth_file] to provide credentials as plaintext JSON. Azure credentials, like
passwords, should not be stored in plaintext whenever possible. Instead, `azure-identity` encourages authenticating with
environment variables (or by other supported means, like [managed identity][managed_identity]).

### Use environment variables

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

### Get credentials from JSON

If it's too difficult to migrate away from JSON- or file-based authentication despite the security risks, you can still
use `azure-identity` credentials. With a JSON file containing the credentials, you can use [`json.load`][json] to
authenticate a service principal with a [`ClientSecretCredential`][client_secret_cred]:
```python
import json
from azure.identity import ClientSecretCredential
from azure.keyvault.certificates import CertificateClient

with open("credentials.json") as json_file:
    json_dict = json.load(json_file)
    
credential = ClientSecretCredential(
    tenant_id=json_dict["tenantId"],
    client_id=json_dict["clientId"],
    client_secret=json_dict["clientSecret"],
    authority=json_dict["activeDirectoryEndpointUrl"]
)
client = CertificateClient("https://{vault-name}.vault.azure.net", credential)
```

Again, if storing credentials in a file, be sure to protect access to this file. Make certain that it's excluded by
version control -- for example, by adding the credential file name to your project's `.gitignore` file.

[client_from_json]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_from_auth_file]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_secret_cred]: https://docs.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python
[json]: https://docs.python.org/3/library/json.html#json.load
[managed_identity]: https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview
