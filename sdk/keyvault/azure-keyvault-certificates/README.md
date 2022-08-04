# Azure Key Vault Certificates client library for Python
Azure Key Vault helps solve the following problems:
- Certificate management (this library) - create, manage, and deploy public and private SSL/TLS certificates
- Cryptographic key management
([azure-keyvault-keys](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys)) - create, store, and control access to the keys used to encrypt your data
- Secrets management
([azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Vault administration ([azure-keyvault-administration](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration)) - role-based access control (RBAC), and vault-level backup and restore options

[Source code][certificates_client_src] | [Package (PyPI)][pypi_package_certificates] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][certificates_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_
_Python 3.7 or later is required to use this package. For more details, please refer to [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)._

## Getting started
### Install the package
Install [azure-keyvault-certificates][pypi_package_certificates] and
[azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-keyvault-certificates azure-identity
```
[azure-identity][azure_identity] is used for Azure Active Directory
authentication as demonstrated below.

### Prerequisites
* An [Azure subscription][azure_sub]
* Python 3.7 or later
* A Key Vault. If you need to create one, you can use the
[Azure Cloud Shell][azure_cloud_shell] to create one with these commands
(replace `"my-resource-group"` and `"my-key-vault"` with your own, unique
names):

  (Optional) if you want a new resource group to hold the Key Vault:
  ```sh
  az group create --name my-resource-group --location westus2
  ```

  Create the Key Vault:
  ```Bash
  az keyvault create --resource-group my-resource-group --name my-key-vault
  ```

  Output:
  ```json
  {
      "id": "...",
      "location": "westus2",
      "name": "my-key-vault",
      "properties": {
          "accessPolicies": [...],
          "createMode": null,
          "enablePurgeProtection": null,
          "enableSoftDelete": null,
          "enabledForDeployment": false,
          "enabledForDiskEncryption": null,
          "enabledForTemplateDeployment": null,
          "networkAcls": null,
          "provisioningState": "Succeeded",
          "sku": { "name": "standard" },
          "tenantId": "...",
          "vaultUri": "https://my-key-vault.vault.azure.net/"
      },
      "resourceGroup": "my-resource-group",
      "type": "Microsoft.KeyVault/vaults"
  }
  ```

  > The `"vaultUri"` property is the `vault_url` used by [CertificateClient][certificate_client_docs]

### Authenticate the client
This document demonstrates using [DefaultAzureCredential][default_cred_ref]
to authenticate as a service principal. However, [CertificateClient][certificate_client_docs]
accepts any [azure-identity][azure_identity] credential. See the
[azure-identity][azure_identity] documentation for more information about other
credentials.

#### Create a service principal (optional)
This [Azure Cloud Shell][azure_cloud_shell] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
a more appropriate name for your service principal.

Create a service principal:
```Bash
az ad sp create-for-rbac --name http://my-application --skip-assignment
```

> Output:
> ```json
> {
>     "appId": "generated app id",
>     "displayName": "my-application",
>     "name": "http://my-application",
>     "password": "random password",
>     "tenant": "tenant id"
> }
> ```

Use the output to set **AZURE_CLIENT_ID** ("appId" above), **AZURE_CLIENT_SECRET**
("password" above) and **AZURE_TENANT_ID** ("tenant" above) environment variables.
The following example shows a way to do this in Bash:
```Bash
export AZURE_CLIENT_ID="generated app id"
export AZURE_CLIENT_SECRET="random password"
export AZURE_TENANT_ID="tenant id"
```

Authorize the service principal to perform certificate operations in your Key Vault:
```Bash
az keyvault set-policy --name my-key-vault --spn $AZURE_CLIENT_ID --certificate-permissions backup create delete get import list purge recover restore update
```
> Possible certificate permissions: backup, create, delete, deleteissuers, get, getissuers, import, list, listissuers, managecontacts, manageissuers, purge, recover, restore, setissuers, update

If you have enabled role-based access control (RBAC) for Key Vault instead, you can find roles like "Key Vault Certificates Officer" in our [RBAC guide][rbac_guide].

#### Create a client
Once the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables are set,
[DefaultAzureCredential][default_cred_ref] will be able to authenticate the
[CertificateClient][certificate_client_docs].

Constructing the client also requires your vault's URL, which you can
get from the Azure CLI or the Azure Portal. In the Azure Portal, this URL is
the vault's "DNS Name".

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
```

## Key concepts
### Certificate Client
With a [CertificateClient][certificate_client_docs] you can get certificates from the vault, create new certificates and
new versions of existing certificates, update certificate metadata, and delete certificates. You
can also manage certificate issuers, contacts, and management policies of certificates. This is
illustrated in the [examples](#examples) below.

## Examples
This section contains code snippets covering common tasks:
* [Create a Certificate](#create-a-certificate "Create a Certificate")
* [Retrieve a Certificate](#retrieve-a-certificate "Retrieve a Certificate")
* [Update Properties of an existing Certificate](#update-properties-of-an-existing-certificate "Update Properties of an existing Certificate")
* [Delete a Certificate](#delete-a-certificate "Delete a Certificate")
* [List Properties of Certificates](#list-properties-of-certificates "List Properties of Certificates")
* [Asynchronously create a Certificate](#asynchronously-create-a-certificate "Asynchronously create a Certificate")
* [Asynchronously list properties of Certificates](#asynchronously-list-properties-of-certificates "Asynchronously list properties of Certificates")

### Create a Certificate
[begin_create_certificate](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.begin_create_certificate)
creates a certificate to be stored in the Azure Key Vault. If a certificate with the same name already exists, a new
version of the certificate is created. Before creating a certificate, a management policy for the certificate can be
created or our default policy will be used. This method returns a long running operation poller.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

create_certificate_poller = certificate_client.begin_create_certificate(
    certificate_name="cert-name", policy=CertificatePolicy.get_default()
)
print(create_certificate_poller.result())
```
If you would like to check the status of your certificate creation, you can call `status()` on the poller or
[get_certificate_operation](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.get_certificate_operation)
with the name of the certificate.

### Retrieve a Certificate
[get_certificate](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.get_certificate)
retrieves the latest version of a certificate previously stored in the Key Vault.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

certificate = certificate_client.get_certificate("cert-name")

print(certificate.name)
print(certificate.properties.version)
print(certificate.policy.issuer_name)
```

[get_certificate_version](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.get_certificate_version)
retrieves a specific version of a certificate.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
certificate = certificate_client.get_certificate_version(certificate_name="cert-name", version="cert-version")

print(certificate.name)
print(certificate.properties.version)
```

### Update properties of an existing Certificate
[update_certificate_properties](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.update_certificate_properties)
updates a certificate previously stored in the Key Vault.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

# we will now disable the certificate for further use
updated_certificate= certificate_client.update_certificate_properties(
    certificate_name="cert-name", enabled=False
)

print(updated_certificate.name)
print(updated_certificate.properties.enabled)
```

### Delete a Certificate
[begin_delete_certificate](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.begin_delete_certificate)
requests Key Vault delete a certificate, returning a poller which allows you to wait for the deletion to finish.
Waiting is helpful when the vault has [soft-delete][soft_delete] enabled, and you want to purge
(permanently delete) the certificate as soon as possible. When [soft-delete][soft_delete] is disabled,
`begin_delete_certificate` itself is permanent.

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

deleted_certificate_poller = certificate_client.begin_delete_certificate("cert-name")

deleted_certificate = deleted_certificate_poller.result()
print(deleted_certificate.name)
print(deleted_certificate.deleted_on)
```
### List properties of Certificates
[list_properties_of_certificates](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient.list_properties_of_certificates)
lists the properties of all certificates in the specified Key Vault.
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

certificates = certificate_client.list_properties_of_certificates()

for certificate in certificates:
    # this list doesn't include versions of the certificates
    print(certificate.name)
```

### Async operations
This library includes a complete set of async APIs. To use them, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport)
for more information.

Async clients and credentials should be closed when they're no longer needed. These
objects are async context managers and define async `close` methods. For
example:

```py
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient

credential = DefaultAzureCredential()

# call close when the client and credential are no longer needed
client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
...
await client.close()
await credential.close()

# alternatively, use them as async context managers (contextlib.AsyncExitStack can help)
client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
async with client:
  async with credential:
    ...
```

### Asynchronously create a Certificate
[create_certificate](https://aka.ms/azsdk/python/keyvault-certificates/aio/docs#azure.keyvault.certificates.aio.CertificateClient.create_certificate)
creates a certificate to be stored in the Azure Key Vault. If a certificate with the same name already exists, a new
version of the certificate is created. Before creating a certificate, a management policy for the certificate can be
created or our default policy will be used. Awaiting `create_certificate` returns your created certificate if creation
is successful, and a
[CertificateOperation](https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateOperation)
if it is not.
```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates import CertificatePolicy

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

create_certificate_result = await certificate_client.create_certificate(
    certificate_name="cert-name", policy=CertificatePolicy.get_default()
)
print(create_certificate_result)
```

### Asynchronously list properties of Certificates
[list_properties_of_certificates](https://aka.ms/azsdk/python/keyvault-certificates/aio/docs#azure.keyvault.certificates.aio.CertificateClient.list_properties_of_certificates)
lists all the properties of the certificates in the client's vault:
```python
from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.certificates.aio import CertificateClient

credential = DefaultAzureCredential()

certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

certificates = certificate_client.list_properties_of_certificates()
async for certificate in certificates:
    print(certificate.name)
```

## Troubleshooting

See the `azure-keyvault-certificates`
[troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/TROUBLESHOOTING.md)
for details on how to diagnose various failure scenarios.

### General
Key Vault clients raise exceptions defined in [azure-core][azure_core_exceptions].
For example, if you try to get a key that doesn't exist in the vault, [CertificateClient][certificate_client_docs]
raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient
from azure.core.exceptions import ResourceNotFoundError

credential = DefaultAzureCredential()
certificate_client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)

try:
    certificate_client.get_certificate("which-does-not-exist")
except ResourceNotFoundError as e:
    print(e.message)
```
### Logging
This library uses the standard
[logging](https://docs.python.org/3.5/library/logging.html) library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument:
```py
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient
import sys
import logging

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = CertificateClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential, logging_enable=True)
```

Network trace logging can also be enabled for any single operation:
 ```python
certificate = certificate_client.get_certificate(certificate_name="cert-name", logging_enable=True)
```

## Next steps
Several samples are available in the Azure SDK for Python GitHub repository. These samples provide example code for additional Key Vault scenarios:
* [hello_world.py][hello_world_sample] and [hello_world_async.py][hello_world_async_sample] - create/get/update/delete certificates
* [backup_restore_operations.py][backup_operations_sample] and [backup_restore_operations_async.py][backup_operations_async_sample] - backup and
recover certificates
* [list_operations.py][list_operations_sample] and [list_operations_async.py][list_operations_async_sample] - list certificates
* [recover_purge_operations.py][recover_purge_operations_sample] and [recover_purge_operations_async.py][recover_purge_operations_async_sample] - recover and purge certificates
* [issuers.py][issuers_sample] and [issuers_async.py][issuers_async_sample] - manage certificate issuers
* [contacts.py][contacts_sample] and [contacts_async.py][contacts_async_sample] - manage certificate contacts

###  Additional Documentation
For more extensive documentation on Azure Key Vault, see the [API reference documentation][reference_docs].

## Contributing
This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact opencode@microsoft.com with any additional questions or comments.

[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_sub]: https://azure.microsoft.com/free/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/backup_restore_operations_async.py
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/hello_world_async.py
[keyvault_docs]: https://docs.microsoft.com/azure/key-vault/
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/list_operations.py
[list_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/list_operations_async.py
[recover_purge_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/recover_purge_operations.py
[recover_purge_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/recover_purge_operations_async.py
[contacts_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/contacts.py
[contacts_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/contacts_async.py
[issuers_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/issuers.py
[issuers_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/azure-keyvault-certificates/samples/issuers_async.py
[pip]: https://pypi.org/project/pip/
[pypi_package_certificates]: https://pypi.org/project/azure-keyvault-certificates/
[certificate_client_docs]: https://aka.ms/azsdk/python/keyvault-certificates/docs#azure.keyvault.certificates.CertificateClient
[rbac_guide]: https://docs.microsoft.com/azure/key-vault/general/rbac-guide
[reference_docs]: https://aka.ms/azsdk/python/keyvault-certificates/docs
[certificates_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/azure/keyvault/certificates
[certificates_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/samples
[soft_delete]: https://docs.microsoft.com/azure/key-vault/general/soft-delete-overview

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-certificates%2FREADME.png)
