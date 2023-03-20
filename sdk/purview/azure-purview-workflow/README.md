# Azure Purview Workflow Service client library for Python

Workflows are automated, repeatable business processes that users can create within Microsoft Purview to validate and orchestrate CUD (create, update, delete) operations on their data entities. Enabling these processes allow organizations to track changes, enforce policy compliance, and ensure quality data across their data landscape.

Use the client library for Purview Workflow to:

- Manage workflows
- Submit user requests and monitor workflow runs
- View and respond to workflow tasks

For more details about how to use workflow, please refer to the [service documentation][product_documentation]

## Getting started

### Prequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure [Purview account][purview_resource].
  
### Authentication

To authenticate with AAD, you must first [pip][pip] install [`azure-identity`][azure_identity_pip]

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
For Workflow service, it is recommended that use the [UsernamePasswordCredential][username_password_credential] to authenticate the client:

Set the values of  client ID and tenant ID of the AAD application, set the values username and password of the AAD user as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `USERNAME` and `PASSWORD`

Use the returned token credential to authenticate the client:

```python
from azure.purview.workflow import PurviewWorkflowClient
from azure.identity import UsernamePasswordCredential
from azure.core.exceptions import HttpResponseError

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
client_id = os.getenv("AZURE_CLIENT_ID")
tenant_id = os.getenv("AZURE_TENANT_ID")
credential = UsernamePasswordCredential(client_id=client_id, username=username, password=password, tenant_id=tenant_id)
client = PurviewWorkflowClient(endpoint='<endpoint>', credential=credential)
```

## Examples

The following section shows you how to initialize and authenticate your client, then list all workflows.

- [List All Workflows](#list-all-workflows "List All Workflows")

### List All Workflows

```python
from azure.purview.workflow import PurviewWorkflowClient
from azure.identity import UsernamePasswordCredential
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
client_id = os.getenv("AZURE_CLIENT_ID")
tenant_id = os.getenv("AZURE_TENANT_ID")
credential = UsernamePasswordCredential(client_id=client_id, username=username, password=password, tenant_id=tenant_id)
client = PurviewWorkflowClient(endpoint='<endpoint>', credential=credential)
try:
    response = client.list_workflows()
    for item in response:
        print(item)
except HttpResponseError as e:
    print('service responds error: {}'.format(e.response.json()))
```
## Key concepts

## Troubleshooting

## Contributing

## Next steps

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
[product_documentation]: https://learn.microsoft.com/azure/purview/concept-workflow
[purview_resource]: https://docs.microsoft.com/azure/purview/create-catalog-portal
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[username_password_credential]: https://learn.microsoft.com/python/api/azure-identity/azure.identity.usernamepasswordcredential?view=azure-python
[azure_sub]: https://azure.microsoft.com/free/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[pip]: https://pypi.org/project/pip/