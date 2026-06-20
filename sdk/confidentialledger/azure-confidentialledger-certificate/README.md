# Azure Confidential Ledger Certificate client library for Python

The Confidential Ledger Certificate client library is used to retrieve the TLS certificate required for connecting to a Confidential Ledger.

## Getting started

### Install the package

```bash
python -m pip install azure-confidentialledger-certificate
```

#### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Confidential Ledger instance.

## Key concepts

Clients may authenticate with a client certificate in mutual TLS instead of via an Azure Active Directory token. Use the `get_ledger_identity()` method on the `ConfidentialLedgerCertificateClient` to retrieve the certificate.

## Examples

Get a ledger certificate for authentication using the `ConfidentialLedgerCertificateClient` from the `azure-confidentialledger-certificate` package, save the certificate, pass the certificate path to the `ConfidentialLedgerCertificateCredential` from the `azure-confidentialledger` package, and pass the credential to the `ConfidentialLedgerClient` for authentication:

```python
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.confidentialledger import (
    ConfidentialLedgerCertificateCredential,
    ConfidentialLedgerClient,
)

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

## Troubleshooting

Confidential Ledger clients raise exceptions defined in [azure-core][azure_core_exceptions].

## Next steps

Use the certificate retrieved using this library with the `azure-confidentialledger` package. The Azure Confidential Ledger client library has several code samples that show common scenario operations.

### Additional Documentation

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

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#azure-core-library-exceptions
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
[reference_docs]: https://aka.ms/azsdk/python/confidentialledger/ref-docs
[ccf]: https://github.com/Microsoft/CCF
