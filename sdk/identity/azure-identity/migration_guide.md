# Guide for migrating to azure-identity from azure-common

## JSON- and file-based authentication

To encourage best security practices, `azure-identity` does not support JSON- and file-based authentication in the same
way as `azure-common`. `azure-common` provided factory methods like [`get_client_from_json_dict`][client_from_json] and
[`get_client_from_auth_file`][client_from_auth_file] to provide credentials as plaintext JSON. Azure credentials, like
passwords, should not be stored in plaintext whenever possible. You can find information about Azure Active Directory
(Azure AD) and best practices for authentication in [Azure AD's documentation][azure_ad].

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

[azure_ad]: https://docs.microsoft.com/azure/active-directory/
[client_from_json]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_from_auth_file]: https://docs.microsoft.com/python/api/azure-common/azure.common.client_factory?view=azure-python#get-client-from-auth-file-client-class--auth-path-none----kwargs-
[client_secret_cred]: https://docs.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python
[json]: https://docs.python.org/3/library/json.html#json.load
