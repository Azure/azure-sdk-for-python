
# Azure AI Document Intelligence client library for Python
Azure AI Document Intelligence ([previously known as Form Recognizer][service-rename]) is a cloud service that uses machine learning to analyze text and structured data from your documents. It includes the following main features:

- Layout - Extract content and structure (ex. words, selection marks, tables) from documents.
- Document - Analyze key-value pairs in addition to general layout from documents.
- Read - Read page information from documents.
- Prebuilt - Extract common field values from select document types (ex. receipts, invoices, business cards, ID documents, U.S. W-2 tax documents, among others) using prebuilt models.
- Custom - Build custom models from your own data to extract tailored field values in addition to general layout from documents.
- Classifiers - Build custom classification models that combine layout and language features to accurately detect and identify documents you process within your application.
- Add-on capabilities - Extract barcodes/QR codes, formulas, font/style, etc. or enable high resolution mode for large documents with optional parameters.


## Getting started

### Installating the package

```bash
python -m pip install azure-ai-documentintelligence
```

#### Prequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure AI Document Intelligence instance.

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
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
