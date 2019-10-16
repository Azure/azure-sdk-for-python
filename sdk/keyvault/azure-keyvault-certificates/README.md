# Azure Key Vault Certificates client library for Python
Azure Key Vault helps solve the following problems:
- Certificate management (this library) - create, manage, and deploy public and private SSL/TLS certificates
- Cryptographic key management
([`azure-keyvault-keys`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys)) - create, store, and control access to the keys used to encrypt your data
- Secrets management
([`azure-keyvault-secrets`](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets

[Source code][certificates_client_src] | [Package (PyPI)][pypi_package_certificates] | [API reference documentation][reference_docs] | [Product documentation][keyvault_docs] | [Samples][certificates_samples]

## Getting started
### Install the package
Install the Azure Key Vault client library for Python with [pip][pip]:

```Bash
pip install azure-keyvault-certificates
```

### Prerequisites
* An [Azure subscription][azure_sub]
* Python 2.7, 3.5.3, or later
* A Key Vault. If you need to create one, you can use the
[Azure Cloud Shell][azure_cloud_shell] to create one with these commands
(replace `"my-resource-group"` and `"my-key-vault"` with your own, unique
names):
  * (Optional) if you want a new resource group to hold the Key Vault:
    ```sh
    az group create --name my-resource-group --location westus2
    ```
  * Create the Key Vault:
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

    > The `"vaultUri"` property is the `vault_endpoint` used by `CertificateClient`

### Authenticate the client
In order to interact with a Key Vault's certificates, you'll need an instance
of the [CertificateClient][certificate_client_docs] class. Creating one
requires a **vault url** and **credential**. This document demonstrates using
`DefaultAzureCredential` as the credential, authenticating with a service
principal's client id, secret, and tenant id. Other authentication methods are
supported. See the [azure-identity][azure_identity] documentation for more
details.

#### Create a service principal
This [Azure Cloud Shell][azure_cloud_shell] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
a more appropriate name for your service principal.

 * Create a service principal:
    ```Bash
    az ad sp create-for-rbac --name http://my-application --skip-assignment
    ```
    Output:
    ```json
    {
        "appId": "generated app id",
        "displayName": "my-application",
        "name": "http://my-application",
        "password": "random password",
        "tenant": "tenant id"
    }
    ```

    * Use the output to set **AZURE_CLIENT_ID** (appId), **AZURE_CLIENT_SECRET**
(password) and **AZURE_TENANT_ID** (tenant) environment variables. The
following example shows a way to do this in Bash:
  ```Bash
   export AZURE_CLIENT_ID="generated app id"
   export AZURE_CLIENT_SECRET="random password"
   export AZURE_TENANT_ID="tenant id"
  ```

* Authorize the service principal to perform certificate operations in your Key Vault:
    ```Bash
    az keyvault set-policy --name my-key-vault --spn $AZURE_CLIENT_ID --certificate-permissions backup create delete get import list purge recover restore update
    ```
    > Possible certificate permissions: backup, create, delete, deleteissuers, get, getissuers, import, list, listissuers, managecontacts, manageissuers, purge, recover, restore, setissuers, update

#### Create a client
After setting the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables, you can create the [CertificateClient][certificate_client_docs]:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient

credential = DefaultAzureCredential()

# Create a new certificate client using the default credential
certificate_client = CertificateClient(vault_endpoint=<your-vault-url>, credential=credential)
```
## Key concepts
With a `CertificateClient` you can get certificates from the vault, create new certificates and
new versions of existing certificates, update certificate metadata, and delete certificates. You
can also manage certificate issuers, contacts, and management policies of certificates. This is
illustrated in the [examples](#examples) below.

### Certificate Client:

## Examples
This section contains code snippets covering common tasks:
* [Create a Certificate](#create-a-certificate)
* [Retrieve a Certificate](#retrieve-a-certificate)
* [Update Properties of an existing Certificate](#update-properties-of-an-existing-certificate)
* [Delete a Certificate](#delete-a-certificate)
* [List Properites of Certificates](#list-properties-of-certificates)
* [Asynchronously create a Certificate](#asynchronously-create-a-certificate)
* [Asynchronously list properties of Certificates](#asynchronously-list-properties-of-certificates)

### Create a Certificate
`begin_create_certificate` creates a certificate to be stored in the Azure Key Vault. If a certificate with
the same name already exists, then a new version of the certificate is created.
Before creating a certificate, a management policy for the certificate can be created or our default
policy will be used. The `begin_create_certificate` operation returns a long running operation poller.
```python
create_certificate_poller = certificate_client.begin_create_certificate(name="cert-name", policy=CertificatePolicy.get_default())

print(create_certificate_poller.result())
```

### Retrieve a Certificate
`get_certificate` retrieves a certificate previously stored in the Key Vault without
having to specify version.
```python
certificate = certificate_client.get_certificate(name="cert-name")

print(certificate.name)
print(certificate.properties.version)
print(certificate.policy.id)
```

`get_certificate_version` retrieves a certificate based on the certificate name and the version of the certificate.
Version is required.
```python
certificate = certificate_client.get_certificate_version(name="cert-name", version="cert-version")

print(certificate.name)
print(certificate.properties.version)
```

### Update properties of an existing Certificate]
`update_certificate_properties` updates a certificate previously stored in the Key Vault.
```python
# You can specify additional application-specific metadata in the form of tags.
tags = {"foo": "updated tag"}

updated_certificate= certificate_client.update_certificate_properties(name="cert-name", tags=tags)

print(updated_certificate.name)
print(updated_certificate.properties.version)
print(updated_certificate.properties.updated_on)
print(updated_certificate.properties.tags)

```

### Delete a Certificate
`delete_certificate` deletes a certificate previously stored in the Key Vault. When [soft-delete][soft_delete]
is not enabled for the Key Vault, this operation permanently deletes the certificate.
```python
deleted_certificate = certificate_client.delete_certificate(name="cert-name")

print(deleted_certificate.name)
print(deleted_certificate.deleted_date)
```
### List properties of Certificates
This example lists the properties of all certificates in the specified Key Vault.
```python
certificates = certificate_client.list_properites_of_certificates()

for certificate in certificates:
    # this list doesn't include versions of the certificates
    print(certificate.name)
```

### Async operations
This library includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [`aiohttp`](https://pypi.org/project/aiohttp/).
See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md#transport)
for more information.

### Asynchronously create a Certificate
`create_certificate` creates a certificate to be stored in the Azure Key Vault. If a certificate with the
same name already exists, then a new version of the certificate is created.
Before creating a certificate, a management policy for the certificate can be created or our default policy
will be used. Awaiting the call to `create_certificate` returns your created certificate if creation is successful,
and a `CertificateOperation` if creation is not.
```python
create_certificate_result = await certificate_client.create_certificate(name="cert-name", policy=CertificatePolicy.get_default())
print(create_certificate_result)
```

### Asynchronously list properties of Certificates
This example lists all the certificates in the client's vault:
```python
certificates = certificate_client.list_certificates()

async for certificate in certificates:
    print(certificate.name)
```

## Troubleshooting
### General
Key Vault clients raise exceptions defined in [`azure-core`][azure_core_exceptions].

For example, if you try to retrieve a certificate after it is deleted a `404` error is returned, indicating
resource not found. In the following snippet, the error is handled gracefully by catching the exception and
displaying additional information about the error.
```python
from azure.core.exceptions import ResourceNotFoundError
try:
    certificate_client.get_certificate(name="deleted_certificate")
except ResourceNotFoundError as e:
    print(e.message)

Output: "certificate not found:deleted_certificate"
```
### Logging
Network trace logging is disabled by default for this library. When enabled,
HTTP requests will be logged at DEBUG level using the `logging` library. You
can configure logging to print debugging information to stdout or write it
to a file:

 ```python
import sys
import logging

 # Create a logger for the 'azure' SDK
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

 # Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

 # Configure a file output
file_handler = logging.FileHandler(filename)
logger.addHandler(file_handler)

# Enable network trace logging. Each HTTP request will be logged at DEBUG level.
client = CertificateClient(vault_endpoint=url, credential=credential, logging_enable=True))
```

Network trace logging can also be enabled for any single operation:
 ```python
certificate = certificate_client.get_certificate(name="cert-name", logging_enable=True)
```

## Next steps
Several samples are available in the Azure SDK for Python GitHub repository. These samples provide example code for additional Key Vault scenarios:
* [test_examples_certificates.py][test_example_certificates] and
[test_examples_certificates_async.py][test_example_certificates_async] - code snippets from
the library's documentation
* [hello_world.py][hello_world_sample] and [hello_world_async.py][hello_world_async_sample] - create/get/update/delete certificates
* [backup_restore_operations.py][backup_operations_sample] and [backup_restore_operations_async.py][backup_operations_async_sample] - backup and
recover certificates

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

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

[asyncio_package]: https://docs.python.org/3/library/asyncio.html
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/docs/exceptions.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_sub]: https://azure.microsoft.com/free/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[backup_operations_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/samples/backup_restore_operations.py
[backup_operations_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/samples/backup_restore_operations_async.py
[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/samples/hello_world_async.py
[certificate_client_docs]: https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.certificates.html#azure.keyvault.certificates.CertificateClient
[keyvault_docs]: https://docs.microsoft.com/en-us/azure/key-vault/
[list_operations_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/samples/list_operations.py
[pip]: https://pypi.org/project/pip/
[pypi_package_certificates]: https://pypi.org/project/azure-keyvault-certificates/
[reference_docs]: https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.certificates.html
[certificates_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/azure/keyvault/certificates
[certificates_samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/samples
[soft_delete]: https://docs.microsoft.com/en-us/azure/key-vault/key-vault-ovw-soft-delete
[test_example_certificates]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/tests/test_examples_certificates.py
[test_example_certificates_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/keyvault/azure-keyvault-certificates/tests/test_examples_certificates_async.py

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Fkeyvault%2Fazure-keyvault-certificates%2FFREADME.png)
