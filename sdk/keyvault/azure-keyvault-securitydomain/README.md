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

[azure-identity][azure_identity] is used for Azure Active Directory authentication as demonstrated below.

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

[library_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/azure/keyvault/securitydomain

[managed_hsm_cli]: https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli
[managed_identity]: https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview

[pip]: https://pypi.org/project/pip/
[pypi_package]: https://pypi.org/project/azure-keyvault-securitydomain/

[reference_docs]: https://aka.ms/azsdk/python/keyvault-securitydomain/docs

[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-securitydomain/samples
[securitydomain_client_docs]: https://aka.ms/azsdk/python/keyvault-securitydomain/docs#azure.keyvault.securitydomain.SecurityDomainClient
