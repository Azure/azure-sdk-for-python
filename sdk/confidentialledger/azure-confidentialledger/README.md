# Azure Confidential Ledger client library for Python

Azure Confidential Ledger provides a service for logging to an immutable, tamper-proof ledger. As part of the [Azure Confidential Computing][azure_confidential_computing] portfolio, Azure Confidential Ledger runs in secure, hardware-based trusted execution environments, also known as enclaves. It is built on Microsoft Research's [Confidential Consortium Framework][ccf].

[Source code][confidential_ledger_client_src] | [Package (PyPI)][pypi_package_confidential_ledger] | [API reference documentation][reference_docs] | [Product documentation][confidential_ledger_docs]

# Table of Contents
- [Azure Confidential Ledger client library for Python](#azure-confidential-ledger-client-library-for-python)
- [Table of Contents](#table-of-contents)
  - [Getting started](#getting-started)
    - [Install packages](#install-packages)
    - [Prerequisites](#prerequisites)
    - [Authenticate the client](#authenticate-the-client)
      - [Using Azure Active Directory](#using-azure-active-directory)
      - [Using a client certificate](#using-a-client-certificate)
    - [Create a client](#create-a-client)
  - [Key concepts](#key-concepts)
    - [Ledger entries and transactions](#ledger-entries-and-transactions)
    - [Receipts](#receipts)
    - [Collections](#collections)
    - [Users](#users)
    - [Confidential computing](#confidential-computing)
    - [Confidential Consortium Framework](#confidential-consortium-framework)
  - [Examples](#examples)
    - [Append entry](#append-entry)
    - [Get receipt](#get-receipt)
    - [Using sub-ledgers](#using-sub-ledgers)
    - [Retrieving ledger entries](#retrieving-ledger-entries)
    - [Making a ranged query](#making-a-ranged-query)
    - [Managing users](#managing-users)
    - [Using certificate authentication](#using-certificate-authentication)
    - [Verifying service details](#verifying-service-details)
    - [Async API](#async-api)
      - [Asynchronously get a ledger entry](#asynchronously-get-a-ledger-entry)
      - [Asynchronously get a range of ledger entries](#asynchronously-get-a-range-of-ledger-entries)
  - [Troubleshooting](#troubleshooting)
    - [General](#general)
    - [Logging](#logging)
  - [Next steps](#next-steps)
    - [Additional Documentation](#additional-documentation)
  - [Contributing](#contributing)

## Getting started
### Install packages
Install [azure-confidentialledger][pypi_package_confidential_ledger] and [azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-identity azure-confidentialledger
```
[azure-identity][azure_identity] is used for Azure Active Directory
authentication as demonstrated below.

### Prerequisites
* An [Azure subscription][azure_sub]
* Python 3.6 or later
* A running instance of Azure Confidential Ledger.
* A registered user in the Confidential Ledger, typically assigned during [ARM][azure_resource_manager] resource creation, with `Administrator` privileges.

### Authenticate the client
#### Using Azure Active Directory
This document demonstrates using [DefaultAzureCredential][default_cred_ref] to authenticate to the Confidential Ledger via Azure Active Directory. However, `ConfidentialLedgerClient` accepts any [azure-identity][azure_identity] credential. See the [azure-identity][azure_identity] documentation for more information about other credentials.

#### Using a client certificate
As an alternative to Azure Active Directory, clients may choose to use a client certificate to authenticate via mutual TLS. `azure.confidentialledger.ConfidentialLedgerCertificateCredential` may be used for this purpose.

### Create a client
`DefaultAzureCredential` will automatically handle most Azure SDK client scenarios. To get started, set environment variables for the AAD identity registered with your Confidential Ledger.
```bash
export AZURE_CLIENT_ID="generated app id"
export AZURE_CLIENT_SECRET="random password"
export AZURE_TENANT_ID="tenant id"
```
Then, `DefaultAzureCredential` will be able to authenticate the `ConfidentialLedgerClient`.

Constructing the client also requires your Confidential Ledger's URL and id, which you can get from the Azure CLI or the Azure Portal. When you have retrieved those values, please replace instances of `"my-ledger-id"` and `"https://my-ledger-url.confidential-ledger.azure.com"` in the examples below. You may also need to replace `"https://identity.confidential-ledger.core.azure.com"` with the hostname from the `identityServiceUri` in the ARM description of your ledger.

Because Confidential Ledgers use self-signed certificates securely generated and stored in an enclave, the signing certificate for each Confidential Ledger must first be retrieved from the Confidential Ledger Identity Service.

```python
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient

identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.confidential-ledger.core.azure.com")
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)
```

## Key concepts
### Ledger entries and transactions
Every write to Azure Confidential Ledger generates an immutable ledger entry in the service. Writes, also referred to as transactions, are uniquely identified by transaction ids that increment with each write. Once written, ledger entries may be retrieved at any time.

### Receipts
State changes to the Confidential Ledger are saved in a data structure called a Merkle tree. To cryptographically verify that writes were correctly saved, a Merkle proof, or receipt, can be retrieved for any transaction id.

### Collections
While most use cases involve just one collection per Confidential Ledger, we provide the collection id feature in case semantically or logically different groups of data need to be stored in the same Confidential Ledger.

Ledger entries are retrieved by their `collectionId`. The Confidential Ledger will always assume a constant, service-determined `collectionId` for entries written without a `collectionId` specified.

### Users
Users are managed directly with the Confidential Ledger instead of through Azure. Users may be AAD-based, identified by their AAD object id, or certificate-based, identified by their PEM certificate fingerprint.

### Confidential computing
[Azure Confidential Computing][azure_confidential_computing] allows you to isolate and protect your data while it is being processed in the cloud. Azure Confidential Ledger runs on Azure Confidential Computing virtual machines, thus providing stronger data protection with encryption of data in use.

### Confidential Consortium Framework
Azure Confidential Ledger is built on Microsoft Research's open-source [Confidential Consortium Framework (CCF)][ccf]. Under CCF, applications are managed by a consortium of members with the ability to submit proposals to modify and govern application operation. In Azure Confidential Ledger, Microsoft Azure owns a an operator member identity that allows it to perform governance and maintenance actions like replacing unhealthy nodes in the Confidential Ledger and upgrading the enclave code.

## Examples
This section contains code snippets covering common tasks:

### Append entry
Data that needs to be stored immutably in a tamper-proof manner can be saved to Azure Confidential Ledger by appending an entry to the ledger.

```python
first_append_result = ledger_client.append_to_ledger(entry_contents="Hello world!")
print(first_append_result.transaction_id)
```

Since Confidential Ledger is a distributed system, rare transient failures may cause writes to be lost. For entries that must be preserved, it is advisable to verify that the write became durable. Waits are blocking calls.
```python
from azure.confidentialledger import TransactionState
ledger_client.wait_until_durable(transaction_id=first_append_result.transaction_id)
assert ledger_client.get_transaction_status(
    transaction_id=first_append_result.transaction_id
).state is TransactionState.COMMITTED

# Alternatively, a client may wait when appending.
append_result = ledger_client.append_to_ledger(
    entry_contents="Hello world, again!", wait_for_commit=True
)
assert ledger_client.get_transaction_status(
    transaction_id=append_result.transaction_id
).state is TransactionState.COMMITTED
```

### Get receipt
A receipt can be retrieved for any transaction id to provide cryptographic proof of the contents of the transaction.
```python
receipt = ledger_client.get_transaction_receipt(
    transaction_id=append_result.transaction_id
)
print(receipt.contents)
```

### Using sub-ledgers
Clients can write to different sub-ledgers to separate logically-distinct data.
```python
ledger_client.append_to_ledger(
    entry_contents="Hello from Alice", sub_ledger_id="Alice"
)
ledger_client.append_to_ledger(
    entry_contents="Hello from Bob", sub_ledger_id="Bob"
)
```

When no sub-ledger id is specified on method calls, the Confidential Ledger service will assume a constant, service-determined sub-ledger id.
```python
append_result = ledger_client.append_to_ledger(entry_contents="Hello world?", wait_for_commit=True)

# The append result contains the sub-ledger id assigned.
entry_by_subledger = ledger_client.get_ledger_entry(
    transaction_id=append_result.transaction_id,
    sub_ledger_id=append_result.sub_ledger_id
)
assert entry_by_subledger.contents == "Hello world?"

# When a ledger entry is retrieved without a sub-ledger specified,
# the service default is used.
entry = ledger_client.get_ledger_entry(transaction_id=append_result.transaction_id)
assert entry.contents == entry_by_subledger.contents
assert entry.sub_ledger_id == entry_by_subledger.sub_ledger_id
```

### Retrieving ledger entries
Ledger entries are retrieved from sub-ledgers. When a transaction id is specified, the returned value is the value contained in the specified sub-ledger at the point in time identified by the transaction id. If no transaction id is specified, the latest available value is returned.
```python
append_result = ledger_client.append_to_ledger(entry_contents="Hello world 0")
ledger_client.append_to_ledger(entry_contents="Hello world 1")

subledger_append_result = ledger_client.append_to_ledger(
    entry_contents="Hello world sub-ledger 0",
    sub_ledger_id="sub-ledger"
)
ledger_client.append_to_ledger(
    entry_contents="Hello world sub-ledger 1",
    sub_ledger_id="sub-ledger",
    wait_for_commit=True
)

# The ledger entry written at 'append_result.transaction_id'
# is retrieved from the default sub-ledger.
entry = ledger_client.get_ledger_entry(transaction_id=append_result.transaction_id)
assert entry.contents == "Hello world 0"

# This is the latest entry available in the default sub-ledger.
latest_entry = ledger_client.get_ledger_entry()
assert latest_entry.contents == "Hello world 1"

# The ledger entry written at 'subledger_append_result.transaction_id'
# is retrieved from the sub-ledger 'sub-ledger'.
subledger_entry = ledger_client.get_ledger_entry(
    transaction_id=subledger_append_result.transaction_id,
    sub_ledger_id="sub-ledger"
)
assert subledger_entry.contents == "Hello world sub-ledger 0"

# This is the latest entry available in the sub-ledger 'sub-ledger'.
subledger_latest_entry = ledger_client.get_ledger_entry(
    sub_ledger_id="sub-ledger"
)
assert subledger_latest_entry.contents == "Hello world sub-ledger 1"
```

### Making a ranged query
Ledger entries in a sub-ledger may be retrieved over a range of transaction ids.
```python
ranged_result = ledger_client.get_ledger_entries(
    from_transaction_id=first_append_result.transaction_id
)
for entry in ranged_result:
    print(f"Transaction id {entry.transaction_id} contents: {entry.contents}")
```

### Managing users
Users with `Administrator` privileges can manage users of the Confidential Ledger directly with the Confidential Ledger itself. Available roles are `Reader` (read-only), `Contributor` (read and write), and `Administrator` (read, write, and add or remove users).

```python
from azure.confidentialledger import LedgerUserRole
user_id = "some AAD object id"
user = ledger_client.create_or_update_user(
    user_id, LedgerUserRole.CONTRIBUTOR
)
# A client may now be created and used with AAD credentials for the user identified by `user_id`.

user = ledger_client.get_user(user_id)
assert user.id == user_id
assert user.role == LedgerUserRole.CONTRIBUTOR

ledger_client.delete_user(user_id)

# For a certificate-based user, their user ID is the fingerprint for their PEM certificate.
user_id = "PEM certificate fingerprint"
user = ledger_client.create_or_update_user(
    user_id, LedgerUserRole.READER
)
```

### Using certificate authentication
Clients may authenticate with a client certificate in mutual TLS instead of via an Azure Active Directory token. `ConfidentialLedgerCertificateCredential` is provided for such clients.
```python
from azure.confidentialledger import ConfidentialLedgerClient, ConfidentialLedgerCertificateCredential
from azure.confidentialledger.identity_service import ConfidentialLedgerIdentityServiceClient

identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.confidential-ledger.core.azure.com")
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity.ledger_tls_certificate)

credential = ConfidentialLedgerCertificateCredential("path to user certificate PEM")
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)
```

### Verifying service details
One may want to validate details about the Confidential Ledger for a variety of reasons. For example, you may want to view details about how Microsoft may manage your Confidential Ledger as part of [Confidential Consortium Framework governance](https://microsoft.github.io/CCF/main/governance/index.html), or verify that your Confidential Ledger is indeed running in a secure enclave. A number of client methods are provided for these use cases.
```python
consortium = ledger_client.get_consortium()
# Consortium members can manage and alter the Confidential Ledger,
# such as by replacing unhealthy nodes.
for member in consortium.members:
    print(member.certificate)
    print(member.id)

import hashlib
# The constitution is a collection of JavaScript code that
# defines actions available to members,
# and vets proposals by members to execute those actions.
constitution = ledger_client.get_constitution()
assert constitution.digest.lower() == \
    hashlib.sha256(constitution.contents.encode()).hexdigest().lower()
print(constitution.contents)
print(constitution.digest)

# Enclave quotes contain material that can be used to
# cryptographically verify the validity and contents
# of an enclave.
ledger_enclaves = ledger_client.get_enclave_quotes()
assert ledger_enclaves.source_node in ledger_enclaves.quotes
for node_id, quote in ledger_enclaves.quotes.items():
    assert node_id == quote.node_id
    print(quote.node_id)
    print(quote.mrenclave)
    print(quote.raw_quote)
    print(quote.version)
```

[Microsoft Azure Attestation Service](https://azure.microsoft.com/services/azure-attestation/) is one provider of enclave quotes.

### Async API
This library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp). See the [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

An async client is obtained from `azure.confidentialledger.aio`. Methods have the same names and signatures as the synchronous client.

Async clients should be closed when they're no longer needed. These objects are async context managers and define async `close` methods. For example:

```python
from azure.identity.aio import DefaultAzureCredential
from azure.confidentialledger.aio import ConfidentialLedgerClient
from azure.confidentialledger.identity_service.aio import ConfidentialLedgerIdentityServiceClient

identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.confidential-ledger.core.azure.com")
network_identity = await identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity.ledger_tls_certificate)

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

# Call close when the client and credential are no longer needed.
await client.close()
await credential.close()

# Alternatively, use them as async context managers (contextlib.AsyncExitStack can help).
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)
async with client:
    async with credential:
        pass
```

#### Asynchronously get a ledger entry
Ledger entries may be retrieved with the async client.
```python
entry = await self.client.get_ledger_entry()
print(entry.contents)
print(entry.sub_ledger_id)
```

#### Asynchronously get a range of ledger entries
Ledger entries may be retrieved over a range with the async client.
```python
query_result = client.get_ledger_entries(
    from_transaction_id="12.3"
)
async for entry in query_result:
    print(entry.transaction_id)
    print(entry.contents)
```

## Troubleshooting
### General
Confidential Ledger clients raise exceptions defined in [azure-core][azure_core_exceptions]. For example, if you try to get a transaction that doesn't exist, `ConfidentialLedgerClient` raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.identity_service import ConfidentialLedgerIdentityServiceClient

identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.confidential-ledger.core.azure.com")
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity.ledger_tls_certificate)

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

try:
    ledger_client.get_ledger_entry(transaction_id="10000.100000")
except ResourceNotFoundError as e:
    print(e.message)
```

### Logging
This library uses the standard
[logging](https://docs.python.org/3.5/library/logging.html) library for logging. Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the `logging_enable` argument:
```python
import logging
import sys

from azure.identity import DefaultAzureCredential
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.identity_service import ConfidentialLedgerIdentityServiceClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.confidential-ledger.core.azure.com")
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity.ledger_tls_certificate)

credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name,
    logging_enable=True
)
```

Similarly, `logging_enable` can enable detailed logging for a single operation, even when it isn't enabled for the client:
```python
ledger_client.get_ledger_entry(transaction_id="12.3", logging_enable=True)
```

## Next steps
###  Additional Documentation
For more extensive documentation on Azure Confidential Ledger, see the
[API reference documentation][reference_docs]. You may also read more about Microsoft Research's open-source [Confidential Consortium Framework][ccf].

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
[Code of Conduct FAQ][code_of_conduct_faq] or
contact opencode@microsoft.com with any additional questions or comments.


[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_cloud_shell]: https://shell.azure.com/bash
[azure_confidential_computing]: https://azure.microsoft.com/solutions/confidential-compute
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#azure-core-library-exceptions
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[azure_resource_manager]: https://docs.microsoft.com/azure/azure-resource-manager/management/overview
[azure_sub]: https://azure.microsoft.com/free
[ccf]: https://github.com/Microsoft/CCF
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq
[confidential_ledger_client_src]: https://aka.ms/azsdk/python/confidentialledger/src
[confidential_ledger_docs]: https://aka.ms/confidentialledger-servicedocs
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[pip]: https://pypi.org/project/pip/
[pypi_package_confidential_ledger]: https://aka.ms/azsdk/python/confidentialledger/pypi
[reference_docs]: https://aka.ms/azsdk/python/confidentialledger/ref-docs
