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

### Authenticate the client

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

To enforce transaction integrity guarantees, an Azure Confidential Ledger uses a [Merkle tree][merkle_tree_wiki] data structure to record the hash of all transactions blocks that are appended to the immutable ledger. After a write transaction is committed, Azure Confidential Ledger users can get a cryptographic Merkle proof, or receipt, over the entry produced in a Confidential Ledger to verify that the write operation was correctly saved. A write transaction receipt is proof that the system has committed the corresponding transaction and can be used to verify that the entry has been effectively appended to the ledger.

Please refer to the following [article](https://learn.microsoft.com/azure/confidential-ledger/write-transaction-receipts) for more information about Azure Confidential Ledger write transaction receipts.

### Receipt Verification

After getting a receipt for a write transaction, Azure Confidential Ledger users can verify the contents of the fetched receipt following a verification algorithm. The success of the verification is proof that the write operation associated to the receipt was correctly appended into the immutable ledger.

Please refer to the following [article](https://learn.microsoft.com/azure/confidential-ledger/verify-write-transaction-receipts) for more information about the verification process for Azure Confidential Ledger write transaction receipts.

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

## Troubleshooting

The Receipt Verification library always returns a general `ReceiptVerificationException` exception to indicate that the receipt verification failed. Such exception may indicate either that the receipt is not valid or that the algorithm failed to verify the content of the given receipt. A valid, well-formatted receipt is supposed to not encounter any exception during the entire verification process. Therefore, clients are recommended to catch exceptions raised when calling the receipt verification algorithm and handle failures accordingly.

In order to understand how and where the verification failed, it is necessary to look at the stack trace for the raised inner exceptions and find the root cause of the problem. There are more specific exceptions and messages that can provide more details about where the algorithm failed (e.g., `RootSignatureVerificationException` indicates that the algorithm failed when trying to verify the signature over the root of the Merkle Tree).

A list of inner exceptions raised by the library, along with their descriptions, can be found at [exceptions.py]<!--(TODO: add link once PR is merged)-->.

## Next steps

### Additional client libraries

Please find below other Confidential Ledger client libraries for Python that are more suitable for general usage and that can be used to administer and perform operations on Azure Confidential Ledgers:

* [Azure Confidential Ledger Management Client Library][confidential_ledger_mgmt_src]: to adminster and manager Azure Confidential Ledger resources
* [Azure Confidential Ledger Client Library][confidential_ledger_client_src]: to perform operations on Azure Confidential Ledger applications

### Additional Documentation

For more extensive documentation on Azure Confidential Ledger, see the
[API reference documentation][reference_docs]. You may also read more about Microsoft Research's open-source [Confidential Consortium Framework][ccf].

## Contributing

If you'd like to contribute to this library, please read the [contributing guide](https://github.com/Azure/azure-sdk/blob/main/CONTRIBUTING.md) to learn more about how to build and test the code.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct].
For more information, see the
[Code of Conduct FAQ][code_of_conduct_faq] or
contact opencode@microsoft.com with any additional questions or comments.

[azure_confidential_computing]: https://azure.microsoft.com/solutions/confidential-compute
[ccf]: https://github.com/Microsoft/CCF
[ccf_docs]: https://microsoft.github.io/CCF/main/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq
[confidential_ledger_client_src]: https://aka.ms/azsdk/python/confidentialledger/src
[confidential_ledger_docs]: https://aka.ms/confidentialledger-servicedocs
[confidential_ledger_mgmt_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/confidentialledger/azure-mgmt-confidentialledger
[confidential_ledger_versioned_api_reference]: https://azure.github.io/azure-sdk-for-python/confidentialledger.html
[merkle_tree_wiki]: https://wikipedia.org/wiki/Merkle_tree
[pip]: https://pypi.org/project/pip/
[reference_docs]: https://aka.ms/azsdk/python/confidentialledger/ref-docs
