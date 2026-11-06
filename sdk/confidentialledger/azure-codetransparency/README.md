# Azure Signing Transparency client library for Python

[comment]: # ( cspell:ignore cose merkle scitt )

`azure-codetransparency` is based on a managed service that complies with a [draft SCITT RFC][SCITT_ARCHITECTURE_RFC]. The service stores [COSE signature envelopes][COSE_RFC] in the Merkle tree and issues signed inclusion proofs as [receipts][SCITT_RECEIPT_RFC].

- [OSS server application source code][Service_source_code]

## Getting started

### Install the package

```bash
python -m pip install --pre azure-codetransparency
```

Optional (if service is configured with AAD):

```bash
python -m pip install azure-identity
```

#### Prequisites

- Python 3.9 or later is required to use this package.
- A running, accessible Signing Transparency service
- Ability to create `COSE_Sign1` envelopes (see [example script][CTS_claim_generator_script])
- The registration policy must be configured in the running service to accept your payloads (see [configuration options][CTS_configuration_doc])

## Key concepts

### SCITT architecture
The Signing Transparency service follows the [SCITT architecture][SCITT_ARCHITECTURE_RFC]. Submitters create and submit COSE signature envelopes, the service applies registration policies before storage, while verifiers check the authenticity of the envelopes and their inclusion in the transparency service.

The architecture also mandates the use of CBOR in the API responses.

### Entries and transactions
Every write generates an immutable entry in the service. Writes, also referred to as transactions, are uniquely identified by transaction ids that increment with each write. Once written, entries and their corresponding receipts may be retrieved at any time.

### Transparent statements and receipts
When a COSE signature envelope is accepted, the service can issue a transparent statement that includes a cryptographic receipt. The receipt is a Merkle proof that demonstrates the inclusion of the signature envelope in the service's Merkle tree. The receipt is signed by the service to ensure its authenticity. The combination of the signature envelope and its corresponding receipt is referred to as a transparent statement (receipt is added to the unprotected headers).

### Transparent statement verification
Verifiers can validate transparent statements by checking the authenticity of the receipt. This involves verifying the receipt signature which implicitly depends on the main signing envelope, checking the inclusion proof, and ensuring that the receipt was issued by a trusted service instance. Verification ensures that the signature envelope was accepted and stored by the service after applying the registration policy.

### COSE signature envelopes
The service accepts [COSE_Sign1][COSE_RFC] signature envelopes as the main payload type. These envelopes contain the signed content along with the signer's public key and other metadata. The service validate the signature before accepting the envelope and applies the configured registration policy to determine whether to store it.

### Registration policies
The service uses registration policies to decide whether to accept or reject submitted COSE signature envelopes. The policy inspects the claims within the envelopes (e.g. signer identity, timestamp, etc.) and applies rules to determine acceptance. Policies can be customized to meet specific transparency requirements.

### Relationship to Confidential Ledger
The Signing Transparency service is running on top of the Confidential Ledger infrastructure, within the same regions, on the same subdomain and has its TLS certificates managed by the Confidential Ledger Identity service. However, it is a separate service with its own API and different features. Both services are built on top of the Confidential Consortium Framework ([CCF][ccf]).

## Examples

There are few main use cases: submitting a COSE signature envelope and verifying the cryptographic submission receipt, which proves that the signature file was accepted.

Before submitting the COSE file, ensure the service is configured with the appropriate policy to be able to accept it.

### Create the client

```python
from azure.confidentialledger.certificate import ConfidentialLedgerCertificateClient
from azure.codetransparency.aio import CodeTransparencyClient
from azure.codetransparency.cbor import CBORDecoder

# Obtain the ledger TLS certificate
identity_client = ConfidentialLedgerCertificateClient()
network_identity = identity_client.get_ledger_identity(
    ledger_id="service-id"
)
ledger_tls_cert_file_name = "ledger_certificate.pem"
with open(ledger_tls_cert_file_name, "w") as cert_file:
    cert_file.write(network_identity["ledgerTlsCertificate"])

# Create the client
credential = None  # the service is designed to be publicly accessible; use Azure Identity credentials if AAD is configured
client = CodeTransparencyClient(
    endpoint="https://service-id.confidential-ledger.azure.com",
    credential=credential,
    ledger_certificate_path=cert_file,
)
```

### Submit a COSE signature envelope

Use the following code to submit the signature:

```python
# Submit the COSE signature envelope and parse the response
entry_body = b"<COSE_Sign1 envelope bytes>"
poller = await client.begin_create_entry(entry_body)
result = await poller.result()
if poller.status() == "finished":
    operation = CBORDecoder(result).decode()
    entry_id = operation.get("EntryId")
    print(f'Entry at transaction id {entry_id} has been committed successfully')
```

### Download the transparent statement

```python
transparent_statement = await client.get_entry_statement(entry_id)
```

### Verify the transparent statement

After obtaining the transparent statement, you can distribute it so others can verify its inclusion in the service. The verifier checks that the receipt was issued for the given signature and that its signature was endorsed by the service. By design transparent statement could contain more than one receipt.

```python
from azure.codetransparency.receipt import (
    verify_transparent_statement,
    VerificationOptions,
    AuthorizedReceiptBehavior,
    UnauthorizedReceiptBehavior,
    OfflineKeysBehavior,
)

verification_options = VerificationOptions(
    authorized_domains=["my-trusted-service-issuer.confidential-ledger.azure.com"],
    authorized_receipt_behavior=AuthorizedReceiptBehavior.VERIFY_ALL_MATCHING,
    unauthorized_receipt_behavior=UnauthorizedReceiptBehavior.FAIL_IF_PRESENT,
    offline_keys=None,  # No offline keys - force network fallback
    offline_keys_behavior=OfflineKeysBehavior.FALLBACK_TO_NETWORK,
)

transparent_statement_bytes = b"".join([chunk async for chunk in transparent_statement])

try:
    verify_transparent_statement(
        transparent_statement_bytes,
        verification_options,
    )
except Exception as e:
    print(f'Verification failed: {e}')
```

If verification completes without errors, you can trust the signature and the receipt if you trust the issuing transparency service and its registration policy. You can then safely inspect the files, especially the payload embedded in the COSE signature envelope.

### Extract the payload from the COSE signature envelope

```python
decoded_struct = CBORDecoder(transparent_statement_bytes).decode_cose_sign1()
payload_bytes=decoded_struct.get("payload", b"")
```

## Troubleshooting

Response values returned from client methods are `Response` objects, which contain information about the HTTP response such as the HTTP `Status` property and a `Headers` collection with more details.

## Next steps

For more extensive documentation, see the API [reference documentation](https://azure.github.io/azure-sdk-for-python/). You can also read more about Microsoft Research's open-source [Confidential Consortium Framework][ccf].

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
[COSE_RFC]: https://www.rfc-editor.org/rfc/rfc8152.txt
[SCITT_ARCHITECTURE_RFC]: https://www.ietf.org/archive/id/draft-ietf-scitt-architecture-11.txt
[SCITT_RECEIPT_RFC]: https://www.ietf.org/archive/id/draft-ietf-cose-merkle-tree-proofs-08.txt
[Service_source_code]: https://github.com/microsoft/scitt-ccf-ledger
[CTS_claim_generator_script]: https://github.com/microsoft/scitt-ccf-ledger/tree/main/demo/transparency-service-poc
[CTS_configuration_doc]: https://github.com/microsoft/scitt-ccf-ledger/blob/main/docs/configuration.md
[ccf]: https://github.com/Microsoft/CCF
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
