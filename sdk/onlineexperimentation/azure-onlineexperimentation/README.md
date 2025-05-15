# Azure Online Experimentation client library for Python

This package contains Azure Online Experimentation client library for interacting with `Microsoft.OnlineExperimentation/workspaces` resources.

## Getting started

### Install the package

```bash
python -m pip install azure-onlineexperimentation
```

#### Prequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An [Azure Online Experimentation workspace][az_exp_workspace] resource in the Azure subscription.

### Create and authenticate the client

The Azure Online Experimentation client library initialization requires two parameters:

- The `endpoint` property value from the [`Microsoft.OnlineExperimentation/workspaces`][az_exp_workspace] resource.
- A credential from `azure.identity`, the simplest approach is to use [DefaultAzureCredential][default_azure_credential] and `az login` to authenticate. See [Azure Identity client library for Python][azure_identity_credentials] for more details.

To construct a synchronous client:

<!-- SNIPPET:sample_initialize_client.initialize_client -->
```python
import os
from azure.onlineexperimentation import OnlineExperimentationClient
from azure.identity import DefaultAzureCredential

client = OnlineExperimentationClient(
    endpoint=os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```
<!-- END SNIPPET -->

To construct an asynchronous client, instead import `OnlineExperimentationClient` from `azure.onlineexperimentation.aio` and `DefaultAzureCredential` from `azure.identity.aio` namespaces:

<!-- SNIPPET:initialize_async_client.initialize_async_client -->
```python
import os
from azure.onlineexperimentation.aio import OnlineExperimentationClient
from azure.identity.aio import DefaultAzureCredential

client = OnlineExperimentationClient(
    endpoint=os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"],
    credential=DefaultAzureCredential()
)
```
<!-- END SNIPPET -->

## Key concepts

???

## Troubleshooting

Errors can occur during initial requests and will provide information about how to resolve the error.

## Examples

```python
>>> from azure.onlineexperimentation import OnlineExperimentationClient
>>> from azure.identity import DefaultAzureCredential
>>> from azure.core.exceptions import HttpResponseError

>>> client = OnlineExperimentationClient(endpoint='<endpoint>', credential=DefaultAzureCredential())
>>> try:
        <!-- write test code here -->
    except HttpResponseError as e:
        print('service responds error: {}'.format(e.response.json()))

```

## Next steps

Have a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/onlineexperimentation/azure-onlineexperimentation/samples/) folder, containing fully runnable Python code for synchronous and asynchronous clients.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit <https://cla.microsoft.co>m.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact <opencode@microsoft.com> with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials

[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[azure_sub]: https://azure.microsoft.com/free/
[az_exp_workspace]: https://learn.microsoft.com/azure/templates/microsoft.onlineexperimentation/workspaces
