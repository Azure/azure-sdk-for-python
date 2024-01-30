# Microsoft Azure SDK for Python

This is the Microsoft Azure Attestation Management Client Library.
This package has been tested with Python 3.7+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting Started

### Prerequsites
```shell
pip install azure-identity
pip install azure-mgmt-attestation
```
    
Before running the examples, please set the values of the client ID, tenant ID and client secret
of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal


### Resources
To learn how to use this package, see the [quickstart guide](https://aka.ms/azsdk/python/mgmt)
 
For docs and references, see [Python SDK References](https://docs.microsoft.com/python/api/overview/azure/)
Code samples for this package can be found at [Attestation Management](https://docs.microsoft.com/samples/browse/?languages=python&term=Getting%20started%20-%20Managing&terms=Getting%20started%20-%20Managing) on docs.microsoft.com.
Additional code samples for different Azure services are available at [Samples Repo](https://aka.ms/azsdk/python/mgmt/samples)


## Examples

### List Attestation Providers
```python
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from azure.mgmt.attestation import AttestationManagementClient

client = AttestationManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id="00000000-0000-0000-0000-000000000000",
)

response = client.attestation_providers.list()
print(response)
```

## Troubleshooting

### CredentialUnavailableError
The CredentialUnavailableError is a specific error type derived from ClientAuthenticationError. This error type is used to indicate that the credential can't authenticate in the current environment, due to missing required configuration or setup. This error is also used as an indication for chained credential types, such as DefaultAzureCredential and ChainedTokenCredential, that the chained credential should continue to attempt other credential types later in the chain.

### Permission issues
Service client calls that result in HttpResponseError with a StatusCode of 401 or 403 often indicate the caller doesn't have sufficient permissions for the specified API. Check the [service documentation](https://learn.microsoft.com/azure/attestation/) to determine which RBAC roles are needed for the specific request, and ensure the authenticated user or service principal have been granted the appropriate roles on the resource.

## Next Steps

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fazure-mgmt-attestation%2FREADME.png)


## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any
additional questions or comments.