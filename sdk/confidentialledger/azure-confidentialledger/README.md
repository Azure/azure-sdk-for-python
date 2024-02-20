# Azure Confidential Ledger client library for Python

Azure Confidential Ledger provides a service for logging to an immutable, tamper-proof ledger. As part of the [Azure Confidential Computing][azure_confidential_computing] portfolio, Azure Confidential Ledger runs in secure, hardware-based trusted execution environments, also known as enclaves. It is built on Microsoft Research's [Confidential Consortium Framework][ccf].

[Source code][confidential_ledger_client_src]
| [Package (PyPI)][pypi_package_confidential_ledger]
| [Package (Conda)](https://anaconda.org/microsoft/azure-confidentialledger/)
| [API reference documentation][reference_docs]
| [Product documentation][confidential_ledger_docs]

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

Constructing the client also requires your Confidential Ledger's URL and id, which you can get from the Azure CLI or the Azure Portal. When you have retrieved those values, please replace instances of `"my-ledger-id"` and `"https://my-ledger-id.confidential-ledger.azure.com"` in the examples below. You may also need to replace `"https://identity.confidential-ledger.core.azure.com"` with the hostname from the `identityServiceUri` in the ARM description of your ledger.

Because Confidential Ledgers use self-signed certificates securely generated and stored in an enclave, the signing certificate for each Confidential Ledger must first be retrieved from the Confidential Ledger Identity Service.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)
```

Conveniently, the `ConfidentialLedgerClient` constructor will fetch the ledger TLS certificate (and write it to the specified file) if it is provided with a non-existent file. The user is responsible for removing the created file as needed.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path="ledger_certificate.pem"
)

# The ledger TLS certificate is written to `ledger_certificate.pem`.
```

To make it clear that a file is being used for the ledger TLS certificate, subsequent examples will explicitly write the ledger TLS certificate to a file.

## Key concepts
### Ledger entries and transactions
Every write to Azure Confidential Ledger generates an immutable ledger entry in the service. Writes, also referred to as transactions, are uniquely identified by transaction ids that increment with each write. Once written, ledger entries may be retrieved at any time.

### Collections
While most use cases involve just one collection per Confidential Ledger, we provide the collection id feature in case semantically or logically different groups of data need to be stored in the same Confidential Ledger.

Ledger entries are retrieved by their `collectionId`. The Confidential Ledger will always assume a constant, service-determined `collectionId` for entries written without a `collectionId` specified.

### Users
Users are managed directly with the Confidential Ledger instead of through Azure. Users may be AAD-based, identified by their AAD object id, or certificate-based, identified by their PEM certificate fingerprint.

### Receipts

To enforce transaction integrity guarantees, an Azure Confidential Ledger uses a [Merkle tree][merkle_tree_wiki] data structure to record the hash of all transactions blocks that are appended to the immutable ledger. After a write transaction is committed, Azure Confidential Ledger users can get a cryptographic Merkle proof, or receipt, over the entry produced in a Confidential Ledger to verify that the write operation was correctly saved. A write transaction receipt is proof that the system has committed the corresponding transaction and can be used to verify that the entry has been effectively appended to the ledger.

Please refer to the following [article](https://learn.microsoft.com/azure/confidential-ledger/write-transaction-receipts) for more information about Azure Confidential Ledger write transaction receipts.

### Receipt Verification

After getting a receipt for a write transaction, Azure Confidential Ledger users can verify the contents of the fetched receipt following a verification algorithm. The success of the verification is proof that the write operation associated to the receipt was correctly appended into the immutable ledger.

Please refer to the following [article](https://learn.microsoft.com/azure/confidential-ledger/verify-write-transaction-receipts) for more information about the verification process for Azure Confidential Ledger write transaction receipts.

### Application Claims
Azure Confidential Ledger applications can attach arbitrary data, called application claims, to write transactions. These claims represent the actions executed during a write operation. When attached to a transaction, the SHA-256 digest of the claims object is included in the ledger and committed as part of the write transaction. This guarantees that the digest is signed in place and cannot be tampered with.

Later, application claims can be revealed in their un-digested form in the receipt payload corresponding to the same transaction where they were added. This allows users to leverage the information in the receipt to re-compute the same claims digest that was attached and signed in place by the Azure Confidential Ledger instance during the transaction. The claims digest can be used as part of the write transaction receipt verification process, providing an offline way for users to fully verify the authenticity of the recorded claims.

More details on the application claims format and the digest computation algorithm can be found at the following links:

- [Azure Confidential Ledger application claims](https://learn.microsoft.com/azure/confidential-ledger/write-transaction-receipts#application-claims)
- [Azure Confidential Ledger application claims digest verification](https://learn.microsoft.com/azure/confidential-ledger/verify-write-transaction-receipts#verify-application-claims-digest)

Please refer to the following CCF documentation pages for more information about CCF Application claims:

- [Application Claims](https://microsoft.github.io/CCF/main/use_apps/verify_tx.html#application-claims)
- [User-Defined Claims in Receipts](https://microsoft.github.io/CCF/main/build_apps/example_cpp.html#user-defined-claims-in-receipts)

### Confidential computing
[Azure Confidential Computing][azure_confidential_computing] allows you to isolate and protect your data while it is being processed in the cloud. Azure Confidential Ledger runs on Azure Confidential Computing virtual machines, thus providing stronger data protection with encryption of data in use.

### Confidential Consortium Framework
Azure Confidential Ledger is built on Microsoft Research's open-source [Confidential Consortium Framework (CCF)][ccf]. Under CCF, applications are managed by a consortium of members with the ability to submit proposals to modify and govern application operation. In Azure Confidential Ledger, Microsoft Azure owns an operator member identity that allows it to perform governance and maintenance actions like replacing unhealthy nodes in the Confidential Ledger and upgrading the enclave code.

## Examples
This section contains code snippets covering common tasks, including:
- [Append entry](#append-entry)
- [Retrieving ledger entries](#retrieving-ledger-entries)
- [Making a ranged query](#making-a-ranged-query)
- [Managing users](#managing-users)
- [Using certificate authentication](#using-certificate-authentication)
- [Verify write transaction receipts](#verify-write-transaction-receipts)

### Append entry
Data that needs to be stored immutably in a tamper-proof manner can be saved to Azure Confidential Ledger by appending an entry to the ledger.

Since Confidential Ledger is a distributed system, rare transient failures may cause writes to be lost. For entries that must be preserved, it is advisable to verify that the write became durable. For less important writes where higher client throughput is preferred, the wait step may be skipped.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

post_entry_result = ledger_client.create_ledger_entry(
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
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

post_poller = ledger_client.begin_create_ledger_entry(
    {"contents": "Hello world again!"}
)
new_post_result = post_poller.result()
print(
    'The new ledger entry has been committed successfully at transaction id '
    f'{new_post_result["transactionId"]}'
)
```

### Retrieving ledger entries
Getting ledger entries older than the latest may take some time as the service is loading historical entries, so a poller is provided.

Ledger entries are retrieved by collection. The returned value is the value contained in the specified collection at the point in time identified by the transaction id.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

post_poller = ledger_client.begin_create_ledger_entry(
    {"contents": "Original hello"}
)
post_result = post_poller.result()

post_transaction_id = post_result["transactionId"]

latest_entry = ledger_client.get_current_ledger_entry()
print(
    f'Current entry (transaction id = {latest_entry["transactionId"]}) '
    f'in collection {latest_entry["collectionId"]}: {latest_entry["contents"]}'
)

post_poller = ledger_client.begin_create_ledger_entry(
    {"contents": "Hello!"}
)
post_result = post_poller.result()

get_entry_poller = ledger_client.begin_get_ledger_entry(post_transaction_id)
older_entry = get_entry_poller.result()
print(
    f'Contents of {older_entry["entry"]["collectionId"]} at {post_transaction_id}: {older_entry["entry"]["contents"]}'
)
```

### Making a ranged query
Ledger entries may be retrieved over a range of transaction ids. Entries will only be returned from the default or specified collection.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

post_poller = ledger_client.begin_create_ledger_entry(
    {"contents": "First message"}
)
first_transaction_id = post_poller.result()["transactionId"]

for i in range(10):
    ledger_client.create_ledger_entry(
        {"contents": f"Message {i}"}
    )

post_poller = ledger_client.begin_create_ledger_entry(
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
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
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
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient

identity_client = ConfidentialLedgerCertificateClient()
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
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)
```

### Verify write transaction receipts

Clients can leverage the receipt verification library in the SDK to verify write transaction receipts issued by Azure Confidential Legder instances. The utility can be used to fully verify receipts offline as the verification algorithm does not require to be connected to a Confidential ledger or any other Azure service.

Once a new entry has been appended to the ledger (please refer to [this example](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/confidentialledger/azure-confidentialledger#append-entry)), it is possible to get a receipt for the committed write transaction.

```python
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

# Replace this with the Confidential Ledger ID 
ledger_id = "my-ledger-id"

# Setup authentication
credential = DefaultAzureCredential()

# Create a Ledger Certificate client and use it to
# retrieve the service identity for our ledger
identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id=ledger_id
)

# Save ledger service certificate into a file for later use
ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

# Create Confidential Ledger client
ledger_client = ConfidentialLedgerClient(
    endpoint=f"https://{ledger_id}.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

# The method begin_get_receipt returns a poller that
# we can use to wait for the receipt to be available for retrieval 
get_receipt_poller = ledger_client.begin_get_receipt(transaction_id)
get_receipt_result = get_receipt_poller.result()

print(f"Write receipt for transaction id {transaction_id} was successfully retrieved: {get_receipt_result}")
```

After fetching a receipt for a write transaction, it is possible to call the `verify_receipt` function to verify that the receipt is valid. The function can accept an optional list of application claims to verify against the receipt claims digest.

```python
from azure.confidentialledger.receipt import (
    verify_receipt,
)

# Read contents of service certificate file saved in previous step.
with open(ledger_tls_cert_file_name, "r") as service_cert_file:
    service_cert_content = service_cert_file.read()

# Optionally read application claims, if any
application_claims = get_receipt_result.get("applicationClaims", None) 

try:
    # Verify the contents of the receipt.
    verify_receipt(get_receipt_result["receipt"], service_cert_content, application_claims=application_claims)
    print(f"Receipt for transaction id {transaction_id} successfully verified")
except ValueError:
    print(f"Receipt verification for transaction id {transaction_id} failed")
```

A full sample Python program that shows how to append a new entry to a running Confidential Ledger instance, get a receipt for the committed transaction, and verify the receipt contents can be found under the [samples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples) folder: [get_and_verify_receipt.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/get_and_verify_receipt.py).

### Async API
This library includes a complete async API supported on Python 3.5+. To use it, you must first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp). See the [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#transport) for more information.

An async client is obtained from `azure.confidentialledger.aio`. Methods have the same names and signatures as the synchronous client. Samples may be found [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples).

## Troubleshooting
### General
Confidential Ledger clients raise exceptions defined in [azure-core][azure_core_exceptions]. For example, if you try to get a transaction that doesn't exist, `ConfidentialLedgerClient` raises [ResourceNotFoundError](https://aka.ms/azsdk-python-core-exceptions-resource-not-found-error):

```python
from azure.core.exceptions import ResourceNotFoundError
from azure.confidentialledger import ConfidentialLedgerClient
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=ledger_tls_cert_file_name
)

try:
    ledger_client.begin_get_ledger_entry(
        transaction_id="10000.100000"  # Using a very high id that probably doesn't exist in the ledger if it's relatively new.
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
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.identity import DefaultAzureCredential

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="my-ledger-id"
)

ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level.
ledger_client = ConfidentialLedgerClient(
    endpoint="https://my-ledger-id.confidential-ledger.azure.com",
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
### More sample code
These code samples show common scenario operations with the Azure Confidential Ledger client library.

#### Common scenarios

- Writing to the ledger:
  - [write_to_ledger.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/write_to_ledger.py) 
  - [write_to_ledger_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/write_to_ledger_async.py) (async version)

- Write many ledger entries and retrieve them all afterwards:
  - [list_ledger_entries.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/list_ledger_entries.py)
  - [list_ledger_entries_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/list_ledger_entries_async.py) (async version)

- Manage users using service-implemented role-based access control: 
  - [manage_users.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/manage_users.py)
  - [manage_users_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/manage_users_async.py) (async version)

#### Advanced scenarios

- Using collections: 
  - [use_collections.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/use_collections.py)
  - [use_collections_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/use_collections_async.py) (async version)
  
- Getting receipts for ledger writes: 
  - [get_receipt.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/get_receipt.py)
  - [get_receipt_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/get_receipt_async.py) (async version)
  
- Verifying service details: 
  - [verify_service.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/verify_service.py) 
  - [verify_service_async.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/confidentialledger/azure-confidentialledger/samples/verify_service_async.py) (async version)

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
