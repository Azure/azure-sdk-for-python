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
    - [Using collections](#using-collections)
    - [Retrieving earlier ledger entries](#retrieving-earlier-ledger-entries)
    - [Making a ranged query](#making-a-ranged-query)
    - [Managing users](#managing-users)
    - [Using certificate authentication](#using-certificate-authentication)
    - [Verifying service details](#verifying-service-details)
    - [Async API](#async-api)
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
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

Since Confidential Ledger is a distributed system, rare transient failures may cause writes to be lost. For entries that must be preserved, it is advisable to verify that the write became durable. For less important writes where higher client throughput is preferred, the wait step may be skipped.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

post_entry_result = ledger_client.post_ledger_entry(
        {"contents": "Hello world!"}
    )
transaction_id = post_entry_result["transactionId"]

wait_poller = ledger_client.begin_wait_for_commit(transaction_id)
wait_poller.wait()
print(f'Ledger entry at transaction id {transaction_id} has been committed successfully')
```

Alternatively, the client may wait for commit when writing a ledger entry.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

post_poller = ledger_client.begin_post_ledger_entry(
    {"contents": "Hello world again!"}
)
new_post_result = post_poller.result()
print(
    'The new ledger entry has been committed successfully at transaction id '
    f'{new_post_result["transactionId"]}'
)
```

### Get receipt
A receipt can be retrieved for any transaction id to provide cryptographic proof of the contents of the transaction.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

get_receipt_poller = client.begin_get_receipt(transaction_id)
get_receipt_result = get_receipt_poller.result()
print(
    f'Receipt for transaction id {get_entry_result["transactionId"]}: '
    f'{get_receipt_result["receipt"]}'
)
```

### Using collections
Clients can write to different collections to group data.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

client.post_ledger_entry(
    {"contents": "Hello from Alice"},
    collection_id="Messages_Alice",
)
client.post_ledger_entry(
    {"contents": "Hello from Bob"},
    collection_id="Messages_Bob",
)
```

When no collection id is specified on method calls, the Confidential Ledger service will assume a constant, service-determined collection id.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

post_poller = ledger_client.begin_post_ledger_entry(
    {"contents": "Hello world?"}
)
post_result = post_poller.result()

# The append result contains the collection id assigned.
latest_entry = ledger_client.get_current_ledger_entry()
assert latest_entry["collectionId"] == post_result["collectionId"]
assert latest_entry["contents"] == "Hello world?"
```

### Retrieving earlier ledger entries
Getting ledger entries older than the latest may take some time as the service is loading historical entries, so a poller is provided.

Ledger entries are retrieved by collection. The returned value is the value contained in the specified collection at the point in time identified by the transaction id.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

post_poller = ledger_client.begin_post_ledger_entry(
    {"contents": "Original hello"}
)
post_result = post_poller.result()

latest_entry = ledger_client.get_current_ledger_entry()
print(
    f'Current entry (transaction id = {latest_entry["transactionId"]}) "
    f"in collection {latest_entry["collectionId"]}: {latest_entry["contents"]}'
)

prior_transaction_id = latest_entry["transactionId"]

post_poller = ledger_client.begin_post_ledger_entry(
    {"contents": "Hello!"}
)
post_result = post_poller.result()

get_entry_poller = ledger_client.begin_get_ledger_entry(prior_transaction_id)
older_entry = get_entry_poller.result()
print(
    f'Contents of {older_entry["collectionId"]} at {prior_transaction_id}: {older_entry["contents"]}'
)
```

### Making a ranged query
Ledger entries may be retrieved over a range of transaction ids. Entries will only be returned from the default or specified collection.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

post_poller = ledger_client.begin_post_ledger_entry(
    {"contents": "First message"}
)
first_transaction_id = post_poller.result()["transactionId"]

for i in range(10):
    ledger_client.post_ledger_entry(
        {"contents": f"Message {i}"}
    )

post_poller = ledger_client.begin_post_ledger_entry(
    {"contents": "Last message"}
)
last_transaction_id = post_poller.result()["transactionId"]

ranged_result = ledger_client.list_ledger_entries(
    from_transaction_id=first_transaction_id,
    to_transaction_id=last_transaction_id,
)
for entry in ranged_result:
    print(f'Contents at {entry["transactionId"]}: {entry["contents"]}')
```

### Managing users
Users with `Administrator` privileges can manage users of the Confidential Ledger directly with the Confidential Ledger itself. Available roles are `Reader` (read-only), `Contributor` (read and write), and `Administrator` (read, write, and add or remove users).

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

user_id = "some AAD object id"
user = ledger_client.create_or_update_user(
    user_id, {"assignedRole": "Contributor"}
)
# A client may now be created and used with AAD credentials (i.e. AAD-issued JWT tokens) for the user identified by `user_id`.

user = ledger_client.get_user(user_id)
assert user["userId"] == user_id
assert user["assignedRole"] == "Contributor"

ledger_client.delete_user(user_id)

# For a certificate-based user, their user ID is the fingerprint for their PEM certificate.
user_id = "PEM certificate fingerprint"
user = ledger_client.create_or_update_user(
    user_id, {"assignedRole": "Reader"}
)

user = ledger_client.get_user(user_id)
assert user["userId"] == user_id
assert user["assignedRole"] == "Reader"

ledger_client.delete_user(user_id)
```

### Using certificate authentication
Clients may authenticate with a client certificate in mutual TLS instead of via an Azure Active Directory token. `ConfidentialLedgerCertificateCredential` is provided for such clients.

```python
from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClient,
)
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient

identity_client = ConfidentialLedgerIdentityServiceClient("https://identity.confidential-ledger.core.azure.com")
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = ConfidentialLedgerCertificateCredential(
    certificate_path="Path to user certificate PEM file"
)
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)
```

### Verifying service details
A user may want to validate details about the Confidential Ledger. For example, you may want to view details about how Microsoft may manage your Confidential Ledger as part of [Confidential Consortium Framework governance](https://microsoft.github.io/CCF/main/governance/index.html), or verify that your Confidential Ledger is indeed running in a secure enclave. A number of client methods are provided for these use cases.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

# Consortium members can manage and alter the Confidential Ledger. Microsoft participates in the consortium to maintain the Confidential Ledger instance.
consortium = ledger_client.get_consortium_members()
for member in consortium.members:
    print(f'Member {member["id"]} has certificate {member["certificate"]}')

import hashlib
# The constitution is a collection of JavaScript code that defines actions available to members, and vets proposals by members to execute those actions.
constitution = ledger_client.get_constitution()
assert (
    constitution["digest"].lower() ==
    hashlib.sha256(constitution["script"].encode()).hexdigest().lower()
)
print(constitution["script"])

# Enclave quotes contain material that can be used to
# cryptographically verify the validity and contents
# of an enclave.
ledger_enclaves = ledger_client.get_enclave_quotes()
assert ledger_enclaves["currentNodeId"] in ledger_enclaves["enclaveQuotes"]
for node_id, quote in ledger_enclaves["enclaveQuotes"].items():
    print(f"Quote for node {node_id}: {quote}")
```

[Microsoft Azure Attestation Service](https://azure.microsoft.com/services/azure-attestation/) is one provider of enclave quotes.

### Async API
This library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp). See the [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

An async client is obtained from `azure.confidentialledger.aio`. Methods have the same names and signatures as the synchronous client. Samples may be found [here](https://aka.ms/python/confidentialledger/samples).

## Troubleshooting
### General
Confidential Ledger clients raise exceptions defined in [azure-core][azure_core_exceptions]. For example, if you try to get a transaction that doesn't exist, `ConfidentialLedgerClient` raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.core.exceptions import ResourceNotFoundError
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger_identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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

try:
    ledger_client.begin_get_ledger_entry(
        transaction_id="10000.100000"
    )
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

from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.identity_service import ConfidentialLedgerIdentityServiceClient
from azure.identity import DefaultAzureCredential

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
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level.
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-url.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name,
    logging_enable=True,
)
```

Similarly, `logging_enable` can enable detailed logging for a single operation, even when it isn't enabled for the client:
```python
ledger_client.get_current_ledger_entry(logging_enable=True)
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
