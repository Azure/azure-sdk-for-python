# Azure Confidential Ledger Receipt Verification client library for Python

Azure Confidential Ledger provides a service for logging to an immutable, tamper-proof ledger. As part of the [Azure Confidential Computing][azure_confidential_computing] portfolio, Azure Confidential Ledger runs in secure, hardware-based trusted execution environments, also known as enclaves. It is built on Microsoft Research's [Confidential Consortium Framework][ccf].

The Azure Confidential Ledger Receipt Verification client library provides utilities to verify write transaction receipts issued by Azure Confidential Legder instances. The library can be used to fully verify receipts offline as the verification algorithm does not require to be connected to a Confidential ledger or any other Azure service.

[Source code](./) | [API reference documentation][reference_docs] | [Product documentation][confidential_ledger_docs]

## Getting started
### Install packages
Install the `azure-confidentialledgertools-receipt-verification` package with [pip][pip]:

```bash
pip install azure-confidentialledgertools-receipt-verification
```

### Prerequisites
* Python 3.6 or later

## Samples
Please refer to the [Azure Confidential Ledger client library][confidential_ledger_client_src] for more details on how to authenticate and fetch receipts for write transactions. A sample Python program that shows how to get and verify a write transaction receipt from a running Confidential Ledger instance can be found under the [samples](samples/) folder: [get_and_verify_receipt.py](samples/get_and_verify_receipt.py).

## Key concepts

### Ledger entries and transactions
Every write to Azure Confidential Ledger generates an immutable ledger entry in the service. Writes, also referred to as transactions, are uniquely identified by transaction ids that increment with each write. Once written, ledger entries may be retrieved at any time.

### Receipts
State changes to the Confidential Ledger are saved in a data structure called a Merkle tree. To cryptographically verify that writes were correctly saved, a Merkle proof, or receipt, can be retrieved for any transaction id.

### Confidential computing
[Azure Confidential Computing][azure_confidential_computing] allows you to isolate and protect your data while it is being processed in the cloud. Azure Confidential Ledger runs on Azure Confidential Computing virtual machines, thus providing stronger data protection with encryption of data in use.

### Confidential Consortium Framework
Azure Confidential Ledger is built on Microsoft Research's open-source [Confidential Consortium Framework (CCF)][ccf]. Under CCF, applications are managed by a consortium of members with the ability to submit proposals to modify and govern application operation. In Azure Confidential Ledger, Microsoft Azure owns an operator member identity that allows it to perform governance and maintenance actions like replacing unhealthy nodes in the Confidential Ledger and upgrading the enclave code.

###  Additional Documentation
For more extensive documentation on Azure Confidential Ledger, see the
[API reference documentation][reference_docs]. You may also read more about Microsoft Research's open-source [Confidential Consortium Framework][ccf].


## 

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

[ccf]: https://github.com/Microsoft/CCF
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq
[confidential_ledger_client_src]: https://aka.ms/azsdk/python/confidentialledger/src
[confidential_ledger_docs]: https://aka.ms/confidentialledger-servicedocs
[pip]: https://pypi.org/project/pip/
[pypi_package_confidential_ledger]: https://aka.ms/azsdk/python/confidentialledger/pypi
[reference_docs]: https://aka.ms/azsdk/python/confidentialledger/ref-docs
