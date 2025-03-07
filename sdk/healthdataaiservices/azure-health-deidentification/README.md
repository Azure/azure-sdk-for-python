

# Azure Health Deidentification client library for Python
Azure.Health.Deidentification is a managed service that enables users to tag, redact, or surrogate health data.

## Getting started

### Install the package

```bash
python -m pip install azure-health-deidentification
```

#### Prequisites

- Python 3.8 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure Health Deidentification instance.
#### Create with an Azure Active Directory Credential
To use an [Azure Active Directory (AAD) token credential][authenticate_with_token],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential] can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client:

```python
>>> from azure.health.deidentification import DeidentificationClient
>>> from azure.identity import DefaultAzureCredential
>>> client = DeidentificationClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
```

## Key concepts

**Operation Modes**
- Tag: Will return a structure of offset and length with the PHI category of the related text spans.
- Redact: Will return output text with placeholder stubbed text. ex. `[name]`
- Surrogate: Will return output text with synthetic replacements.
  - `My name is John Smith`
  - `My name is Tom Jones`

**Job Integration with Azure Storage**
Instead of sending text, you can send an Azure Storage Location to the service. We will asynchronously
process the list of files and output the deidentified files to a location of your choice.

Limitations:
- Maximum file count per job: 1000 documents
- Maximum file size per file: 2 MB

## Examples

```python
>>> from azure.health.deidentification import DeidentificationClient
>>> from azure.identity import DefaultAzureCredential
>>> from azure.core.exceptions import HttpResponseError

>>> client = DeidentificationClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
>>> try:
        <!-- write test code here -->
    except HttpResponseError as e:
        print('service responds error: {}'.format(e.response.json()))

```

## Next steps

- Find a bug, or have feedback? Raise an issue with "Health Deidentification" Label.


## Troubleshooting

- **Unabled to Access Source or Target Storage**
  - Ensure you create your deid service with a system assigned managed identity
  - Ensure your storage account has given permissions to that managed identity

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
[authenticate_with_token]: https://learn.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/

