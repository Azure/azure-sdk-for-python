# Azure Signing Transparency client library for Python

`azure-codetransparency` is based on a managed service that complies with a [draft SCITT RFC][SCITT_ARCHITECTURE_RFC]. The service stores [COSE signature envelopes][COSE_RFC] in the Merkle tree and issues signed inclusion proofs as [receipts][SCITT_RECEIPT_RFC].

- [OSS server application source code][Service_source_code]

## Getting started

### Install the package

```bash
python -m pip install azure-codetransparency
```

#### Prequisites

- Python 3.9 or later is required to use this package.
- A running, accessible Signing Transparency service
- Ability to create `COSE_Sign1` envelopes (see [example script][CTS_claim_generator_script])
- The registration policy must be configured in the running service to accept your payloads (see [configuration options][CTS_configuration_doc])

## Key concepts

<!-- TODO -->

## Examples

<!-- TODO -->

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
[CTS_claim_generator_script]: https://github.com/microsoft/scitt-ccf-ledger/tree/main/demo/cts_poc
[CTS_configuration_doc]: https://github.com/microsoft/scitt-ccf-ledger/blob/main/docs/configuration.md
[ccf]: https://github.com/Microsoft/CCF
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
