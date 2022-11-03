# Azure Confidential Ledger Receipt Verification client library for Python

Azure Confidential Ledger provides a service for logging to an immutable, tamper-proof ledger. As part of the [Azure Confidential Computing][azure_confidential_computing] portfolio, Azure Confidential Ledger runs in secure, hardware-based trusted execution environments, also known as enclaves. It is built on Microsoft Research's [Confidential Consortium Framework][ccf].

The Azure Confidential Ledger Receipt Verification client library provides utilities to verify write transaction receipts issued by Azure Confidential Legder instances. The library can be used to fully verify receipts offline as the verification algorithm does not require to be connected to a Confidential ledger or any other Azure service.

[Package (PyPI)]<!--(TODO: add link once PR is merged)--> | [API reference documentation][reference_docs] | [Product documentation][confidential_ledger_docs] | [Source code]<!--(TODO: add link once PR is merged)--> | [ChangeLog]<!--(TODO: add link once PR is merged)--> | [Samples]<!--(TODO: add link once PR is merged)--> | [Versioned API References][confidential_ledger_versioned_api_reference]

## Getting started

### Install the package

Install the `azure-confidentialledgertools-receiptverification` package with [pip][pip]:

```bash
pip install azure-confidentialledgertools-receiptverification
```

You may also want to install the [Azure Confidential Ledger client library][confidential_ledger_client_src] to get write transaction receipts from a running Confidential Ledger instance. Please refer to the [Getting Started section](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/confidentialledger/azure-confidentialledger#getting-started) of the client library for more details on installing the required packages and authenticating the client.

### Prerequisites

* Python 3.6 or later

## Key concepts

### Confidential computing

[Azure Confidential Computing][azure_confidential_computing] allows you to isolate and protect your data while it is being processed in the cloud. Azure Confidential Ledger runs on Azure Confidential Computing virtual machines, thus providing stronger data protection with encryption of data in use.

### Confidential Consortium Framework

Azure Confidential Ledger is built on Microsoft Research's open-source [Confidential Consortium Framework (CCF)][ccf]. Under CCF, applications are managed by a consortium of members with the ability to submit proposals to modify and govern application operation. In Azure Confidential Ledger, Microsoft Azure owns an operator member identity that allows it to perform governance and maintenance actions like replacing unhealthy nodes in the Confidential Ledger and upgrading the enclave code.

### Ledger entries and transactions

Every write to Azure Confidential Ledger generates an immutable ledger entry in the service. Writes, also referred to as transactions, are uniquely identified by transaction ids that increment with each write. Once written, ledger entries may be retrieved at any time.

### Receipts

State changes to the Confidential Ledger are saved in a data structure called a [Merkle tree][merkle_tree_wiki]. To cryptographically verify that writes were correctly saved, a Merkle proof, or receipt, can be retrieved for any transaction id.

A receipt is a cryptographic proof that a transaction has been committed to the ledger: it can be used to verify that the ledger entry associated to a transaction has been appended to the ledger (thus, it can be used to validate properties such as non-repudiation, integrity, and tamper-proofing). A receipt contains all the information needed to verify transaction inclusion and the verification can be done by applying an ad-hoc algorithm.

Please refer to the following CCF documentation links for more information about receipts:

* [Write Receipts](https://microsoft.github.io/CCF/main/use_apps/verify_tx.html#write-receipts)
* [Receipts](https://microsoft.github.io/CCF/main/audit/receipts.html)

### Receipt Verification

Azure Confidential Ledger write transaction receipts can be verfied by following three sequential steps:

1. Compute the SHA-256 hash of the leaf node in the Merkle Tree corresponding to the committed transaction. A leaf node is composed of the ordered concatenation of the following fields that can be found in an Azure Confidential Ledger receipt:
   * `write_set_digest`
   * SHA-256 digest of `commit_evidence`
   * `claims_digest` fields

2. Re-compute the SHA-256 hash of the root of the Merkle Tree at the time the transaction was committed. This can be accomplished by iteratively hashing and concatenating the leaf node hash (computed in the previous step) with the ordered nodes’ hashes provided in the `proof` field of a receipt. The concatenation needs to be done with respect to the relative order indicated in the objects provided in the `proof` field (either `left` or `right`), and the result of the previous iteration shall be used as input for the next one. This process follows the standard steps to compute the root of a [Merkle Tree][merkle_tree_wiki] data structure given the required nodes for the computation.

3. Verify that the cryptograhic signature produced over the root node hash is valid using the signing node certificate in the receipt. The verification process follows the standard steps for digital signature verification for messages signed using the [Elliptic Curve Digital Signature Algorithm (ECDSA)](https://wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm).

In addition to the above, it is also required to verify that the signing node certificate is endorsed by the ledger certificate. As the ledger certificate may have been renewed since the transaction was committed, it is possible that the current service identity is different from the one that endorsed the signing node. If this applies, it is required to build a chain of certificates from the signing node certificate (the `cert` field in the receipt) up to a trusted root Certificate Authority (the current service identity certificate) through other previous service identities (the `service_endorsements` list field in the receipt). Certificate endorsement need to be verified for the entire chain and follows a similar signature verification process outlined in the previous point.

Please refer to the [CCF documentation about receipt verification](https://microsoft.github.io/CCF/main/use_apps/verify_tx.html#receipt-verification) for more details about how the algorithm works. Please also see the docstrings under [models.py]<!--(TODO: add link once PR is merged)--> for detailed description of each field in an Azure Confidential Ledger receipt.

The following CCF documentation links could also be useful to better understand some topics related to receipt verification:

* [CCF Glossary](https://microsoft.github.io/CCF/main/overview/glossary.html)
* [Merkle Tree](https://microsoft.github.io/CCF/main/architecture/merkle_tree.html)
* [Cryptography](https://microsoft.github.io/CCF/main/architecture/cryptography.html)
* [Certificates](https://microsoft.github.io/CCF/main/operations/certificates.html)

### Additional Documentation

For more extensive documentation on Azure Confidential Ledger, see the
[API reference documentation][reference_docs]. You may also read more about Microsoft Research's open-source [Confidential Consortium Framework][ccf].

## Examples

This section contains code snippets covering common tasks, including:

* [Verify write transaction receipts](#verify-write-transaction-receipts)

### Verify write transaction receipts

The Azure Confidential Ledger Receipt Verification can be used to verify write transaction receipts, which can be retrieved from a running Azure Confidential Ledger instance. To get a receipt for a committed write transaction, it is possible to leverage the [Azure Confidential Ledger client library][confidential_ledger_client_src].

Here below is shown a simple example on how to create a new Confidential Ledger client and append a new entry to the ledger. Please refer to the [client library documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/confidentialledger/azure-confidentialledger#append-entry) for more details about appending entries to a ledger.

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

# The method begin_create_ledger_entry returns a poller that
# we can use to wait for the transaction to be committed
post_entry_poller = ledger_client.begin_create_ledger_entry(
    {"contents": "Hello world!"}
)
post_entry_result = post_entry_poller.result()

# Get transaction ID
transaction_id = post_entry_result["transactionId"]

print(f'Ledger entry at transaction id {transaction_id} has been committed successfully')

# The method begin_get_receipt returns a poller that
# we can use to wait for the receipt to be available for retrieval 
get_receipt_poller = ledger_client.begin_get_receipt(transaction_id)
get_receipt_result = get_receipt_poller.result()

print(f"Write receipt for transaction id {transaction_id} was successfully retrieved: {get_receipt_result}")
```

Once a new entry has been appended to the ledger, it is possible to get a receipt for the committed write transaction.

```python
# The method begin_get_receipt returns a poller that
# we can use to wait for the receipt to be available for retrieval 
get_receipt_poller = ledger_client.begin_get_receipt(transaction_id)
get_receipt_result = get_receipt_poller.result()

print(f"Write receipt for transaction id {transaction_id} was successfully retrieved: {get_receipt_result}")
```

After fetching a receipt for a write transaction, it is possible to leverage the Azure Confidential Ledger Receipt Verification client library to verify that the receipt is valid.

```python
from azure.confidentialledgertools.receiptverification import (
    verify_receipt,
    ReceiptVerificationException,
    Receipt,
)

# Convert receipt content to a Receipt model.
receipt_content = Receipt.from_dict(get_receipt_result["receipt"])

# Read contents of service certificate file saved in previous step.
with open(ledger_tls_cert_file_name, "r") as service_cert_file:
    service_cert_content = service_cert_file.read()

try:
    # Verify the contents of the receipt.
    verify_receipt(receipt_content, service_cert_content)
    print(f"Receipt for transaction id {transaction_id} successfully verified")
except ReceiptVerificationException:
    print(f"Receipt verification for transaction id {transaction_id} failed")
```

A full sample Python program that shows how to append a new entry to a running Confidential Ledger instance, get a receipt for the committed transaction, and verify the receipt contents can be found under the [samples]<!--(TODO: add link once PR is merged)--> folder: [get_and_verify_receipt.py]<!--(TODO: add link once PR is merged)-->.

## Contributing

If you'd like to contribute to this library, please read the [contributing guide](https://github.com/Azure/azure-sdk/blob/main/CONTRIBUTING.md) to learn more about how to build and test the code.

[azure_confidential_computing]: https://azure.microsoft.com/solutions/confidential-compute
[ccf]: https://github.com/Microsoft/CCF
[confidential_ledger_client_src]: https://aka.ms/azsdk/python/confidentialledger/src
[confidential_ledger_docs]: https://aka.ms/confidentialledger-servicedocs
[pip]: https://pypi.org/project/pip/
[reference_docs]: https://aka.ms/azsdk/python/confidentialledger/ref-docs
[confidential_ledger_versioned_api_reference]: https://azure.github.io/azure-sdk-for-python/confidentialledger.html
[merkle_tree_wiki]: https://wikipedia.org/wiki/Merkle_tree
