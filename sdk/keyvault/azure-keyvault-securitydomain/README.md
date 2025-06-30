# Azure Key Vault Security Domain client library for Python

Azure Key Vault helps solve the following problems:

- Managed HSM security domain management (this library) - securely download and restore a managed HSM's security domain
- Cryptographic key management ([azure-keyvault-keys](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys))- create, store, and control
access to the keys used to encrypt your data
- Secrets management
([azure-keyvault-secrets](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets)) -
securely store and control access to tokens, passwords, certificates, API keys,
and other secrets
- Certificate management
([azure-keyvault-certificates](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates)) -
create, manage, and deploy public and private SSL/TLS certificates
- Vault administration ([azure-keyvault-administration](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration)) - role-based access control (RBAC), and vault-level backup and restore options

[Source code][library_src]
| [Package (PyPI)][pypi_package]
| [API reference documentation][reference_docs]
| [Key Vault documentation][azure_keyvault]
| [Managed HSM documentation][azure_managedhsm]
| [Samples][samples]

## Getting started

### Install the package

Install [azure-keyvault-securitydomain][pypi_package] and [azure-identity][azure_identity_pypi] with [pip][pip]:

```Bash
python -m pip install azure-keyvault-securitydomain azure-identity
```

[azure-identity][azure_identity] is used for Microsoft Entra ID authentication as demonstrated below.

#### Prequisites

- Python 3.9 or later
- An [Azure subscription][azure_sub]
- An existing [Key Vault Managed HSM][azure_managedhsm]. If you need to create a Managed HSM, you can do so using the Azure CLI by following the steps in [this document][managed_hsm_cli].

### Authenticate the client

In order to interact with the Azure Key Vault service, you will need an instance of a
[SecurityDomainClient][securitydomain_client_docs], as well as a **vault URL** and a credential object. This document
demonstrates using a [DefaultAzureCredential][default_cred_ref], which is appropriate for most scenarios. We recommend
using a [managed identity][managed_identity] for authentication in production environments.

See [azure-identity][azure_identity] documentation for more information about other methods of authentication and their
corresponding credential types.

#### Create a client

After configuring your environment for the [DefaultAzureCredential][default_cred_ref] to use a suitable method of
authentication, you can do the following to create a security domain client (replacing the value of `VAULT_URL` with
your vault's URL):

<!-- SNIPPET:hello_world.create_a_security_domain_client -->

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.securitydomain import SecurityDomainClient

VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
client = SecurityDomainClient(vault_url=VAULT_URL, credential=credential)
```

<!-- END SNIPPET -->

> **NOTE:** For an asynchronous client, import `azure.keyvault.securitydomain.aio`'s `SecurityDomainClient` instead.

## Key concepts

### Security domain

To operate, a managed HSM must have a security domain. The security domain is an encrypted blob file that contains
artifacts like the HSM backup, user credentials, the signing key, and the data encryption key that's unique to the
managed HSM. For more information, please see [service documentation][securitydomain_docs].

### SecurityDomainClient

A `SecurityDomainClient` can download and upload managed HSM security domains and get transfer keys.

### Download operation

A download operation retrieves the security domain of a managed HSM. This can be used to activate a provisioned
managed HSM.

### Upload operation

An upload operation restores a managed HSM using a provided security domain.

### Transfer key

A transfer key, or exchange key, is used to encrypt a security domain before uploading it to a managed HSM. For more
information, please see the [disaster recovery guide][disaster_recovery].

## Examples

This section contains code snippets covering common tasks:

- [Download a security domain](#download-a-security-domain)
- [Get a transfer key](#get-a-transfer-key)
- [Upload a security domain](#upload-a-security-domain)

### Download a security domain

`begin_download` can be used by a `SecurityDomainClient` to fetch a managed HSM's security domain, and this will also
activate a provisioned managed HSM. By default, the poller returned by this operation will poll on the managed HSM's
activation status, finishing when it's activated. To return immediately with the security domain object without waiting
for activation, you can pass the keyword argument `skip_activation_polling=True`.

```python
from azure.keyvault.securitydomain.models import SecurityDomain

security_domain: SecurityDomain = client.begin_download(certificate_info=certs_object).result()
assert security_domain.value
print("The managed HSM is now active.")
```

### Get a transfer key

Using a different managed HSM than the one the security domain was downloaded from, `get_transfer_key` can be used by
a `SecurityDomainClient` to fetch a transfer key (also known as an exchange key).

```python
from azure.keyvault.securitydomain.models import TransferKey

NEW_VAULT_URL = os.environ["NEW_VAULT_URL"]
upload_client = SecurityDomainClient(vault_url=NEW_VAULT_URL, credential=credential)

transfer_key: TransferKey = upload_client.get_transfer_key()
assert transfer_key.transfer_key
```

### Upload a security domain

`begin_upload` can be used by a `SecurityDomainClient` to restore a different managed HSM with a security domain, for
example for disaster recovery. Like the download operation this will activate a provisioned managed HSM, but the poller
will return None if successful (and an error if unsuccessful) instead of the security domain object.

```python
upload_client.begin_upload(security_domain=result).wait()
print("The managed HSM has been successfully restored with the security domain.")
```

## Troubleshooting

See the Azure Key Vault SDK's
[troubleshooting guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/keyvault/TROUBLESHOOTING.md) for
details on how to diagnose various failure scenarios.

## Next steps
Samples are available in the Azure SDK for Python GitHub repository. These samples provide example code for the
following scenarios:

- [Download a security domain][hello_world_sample] ([async version][hello_world_async_sample])

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

<!-- LINKS -->
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_keyvault]: https://learn.microsoft.com/azure/key-vault/
[azure_managedhsm]: https://learn.microsoft.com/azure/key-vault/managed-hsm/
[azure_sub]: https://azure.microsoft.com/free/

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/

[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[disaster_recovery]: https://learn.microsoft.com/azure/key-vault/managed-hsm/disaster-recovery-guide

[hello_world_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/samples/hello_world.py
[hello_world_async_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/samples/hello_world_async.py

[library_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/azure/keyvault/securitydomain

[managed_hsm_cli]: https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli
[managed_identity]: https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview

[pip]: https://pypi.org/project/pip/
[pypi_package]: https://pypi.org/project/azure-keyvault-securitydomain/

[reference_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/azure/keyvault/securitydomain

[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/samples
[securitydomain_client_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/azure/keyvault/securitydomain/_patch.py
[securitydomain_docs]: https://learn.microsoft.com/azure/key-vault/managed-hsm/security-domain
