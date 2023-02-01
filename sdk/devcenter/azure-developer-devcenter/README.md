
# Azure DevCenter Service client library for Python
The Azure DevCenter package provides access to manage resources for Microsoft Dev Box and Azure Deployment Environments. This SDK enables managing developer machines and environments in Azure.

Use the package for Azure DevCenter to:
> Create, access, manage, and delete Dev Box resources
> Create, deploy, manage, and delete Environment resources

## Getting started

### Installating the package

```bash
python -m pip install azure-developer-devcenter
```

#### Prequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- You must have [configured](https://learn.microsoft.com/azure/dev-box/quickstart-configure-dev-box-service) a DevCenter, Project, Network Connection, Dev Box Definition, and Pool before you can create Dev Boxes 
- You must have [configured](https://learn.microsoft.com/azure/deployment-environments/) a DevCenter, Project, Catalog, and Environment Type before you can create Environments

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
>>> import os
>>> from azure.developer.devcenter import DevCenterClient
>>> from azure.identity import DefaultAzureCredential
>>> tenant_id = os.environ['AZURE_TENANT_ID']
>>> client = DevCenterClient(tenant_id=tenant_id, dev_center="my_dev_center", credential=DefaultAzureCredential())
```

## Examples

### Dev Box Management
```python
>>> import os
>>> from azure.developer.devcenter import DevCenterClient
>>> from azure.identity import DefaultAzureCredential
>>> from azure.core.exceptions import HttpResponseError
>>> tenant_id = os.environ['AZURE_TENANT_ID']
>>> client = DevCenterClient(tenant_id=tenant_id, dev_center="my_dev_center", credential=DefaultAzureCredential())
>>> try:
        # Fetch control plane resource dependencies
        projects = list(client.dev_center.list_projects(top=1))
        target_project_name = projects[0]['name']

        pools = list(client.dev_boxes.list_pools(target_project_name, top=1))
        target_pool_name = pools[0]['name']

        # Stand up a new dev box
        create_response = client.dev_boxes.begin_create_dev_box(target_project_name, "Test_DevBox", {"poolName": target_pool_name})
        devbox_result = create_response.result()

        LOG.info(f"Provisioned dev box with status {devbox_result['provisioningState']}.")

        # Connect to the provisioned dev box
        remote_connection_response = client.dev_boxes.get_remote_connection(target_project_name, "Test_DevBox")
        LOG.info(f"Connect to the dev box using web URL {remote_connection_response['webUrl']}")

        # Tear down the dev box when finished
        delete_response = client.dev_boxes.begin_delete_dev_box(target_project_name, "Test_DevBox")
        delete_response.wait()
        LOG.info("Deleted dev box successfully.")
    except HttpResponseError as e:
        print('service responds error: {}'.format(e.response.json()))

```

### Environment Management
```python
>>> import os
>>> from azure.developer.devcenter import DevCenterClient
>>> from azure.identity import DefaultAzureCredential
>>> from azure.core.exceptions import HttpResponseError
>>> tenant_id = os.environ['AZURE_TENANT_ID']
>>> client = DevCenterClient(tenant_id=tenant_id, dev_center="my_dev_center", credential=DefaultAzureCredential())
>>> try:
        # Fetch control plane resource dependencies
        target_project_name = list(client.dev_center.list_projects(top=1))[0]['name']
        target_catalog_item_name = list(client.environments.list_catalog_items(target_project_name, top=1))[0]['name']
        target_environment_type_name = list(client.environments.list_environment_types(target_project_name, top=1))[0]['name']

        # Stand up a new environment
        create_response = client.environments.begin_create_environment(target_project_name,
                                                           "Dev_Environment",
                                                           {"catalogItemName": target_catalog_item_name, "environmentType": target_environment_type_name})
        environment_result = create_response.result()

        LOG.info(f"Provisioned environment with status {environment_result['provisioningState']}.")

        # Fetch deployment artifacts
        artifact_response = client.environments.list_artifacts_by_environment(target_project_name, "Dev_Environment")

        for artifact in artifact_response:
            LOG.info(artifact)

        # Tear down the environment when finished
        delete_response = client.environments.begin_delete_environment(target_project_name, "Dev_Environment")
        delete_response.wait()
        LOG.info("Completed deletion for the environment.")
    except HttpResponseError as e:
        print('service responds error: {}'.format(e.response.json()))

```
## Key concepts
Dev Boxes refer to managed developer machines running in Azure. Dev Boxes are provisioned in Pools, which define the network and image used for a Dev Box.

Environments refer to templated developer environments, which combine a template (Catalog Item) and parameters.

## Troubleshooting
Errors can occur during initial requests and long-running operations, and will provide information about how to resolve the error. 
Be sure to confirm that dependent resources, such as pools and catalogs, are set up properly and are in a healthy state. You will not be able to create resources with the package when your dependent resources are in a failed state.

## Next steps
Get started by exploring our samples and starting to use the package!

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
