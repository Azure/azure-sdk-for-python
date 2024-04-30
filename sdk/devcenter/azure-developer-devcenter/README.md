
# Azure DevCenter Service client library for Python
The Azure DevCenter package provides access to manage resources for Microsoft Dev Box and Azure Deployment Environments. This SDK enables managing developer machines and environments in Azure.

Use the package for Azure DevCenter to:
> Create, access, manage, and delete Dev Box resources
> Create, deploy, manage, and delete Environment resources

## Getting started

### Installing the package

```bash
python -m pip install azure-developer-devcenter
```

### Prerequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- For Dev Box operations you must have [configured](https://learn.microsoft.com/azure/dev-box/quickstart-configure-dev-box-service) a DevCenter, Project, Network Connection, Dev Box Definition, and Pool.
- For Deployment Environments operations you must have [configured](https://learn.microsoft.com/azure/deployment-environments/) a DevCenter, Project, Catalog, Environment Definition and Environment Type.

### Create Client with an Azure Active Directory Credential

In order to interact with the Dev Center service, you will need to create an instance of a client. An **endpoint** and **credential** are necessary to instantiate the client object.

For the endpoint use the Dev Center URI. It should have the format `https://{tenantId}-{devCenterName}.{devCenterRegion}.devcenter.azure.com`.

For the credential use an [Azure Active Directory (AAD) token credential][authenticate_with_token], providing an instance of the desired credential type obtained from the [azure-identity][azure_identity_credentials] library.

To authenticate with AAD, you must first install [azure-identity][azure_identity_pip] using [pip][pip]

```bash
pip install azure-identity
```

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.

As an example, [DefaultAzureCredential][default_azure_credential] can be used to authenticate the client:
Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client.

<!-- SNIPPET:create_client_sample.create_dev_center_client -->

```python
import os

from azure.developer.devcenter import DevCenterClient
from azure.identity import DefaultAzureCredential

# Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
# DEVCENTER_ENDPOINT, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
try:
    endpoint = os.environ["DEVCENTER_ENDPOINT"]
except KeyError:
    raise ValueError("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")

# Build a client through AAD
client = DevCenterClient(endpoint, credential=DefaultAzureCredential())
```

<!-- END SNIPPET -->

With `DevCenterClient` you can execute operations in [Dev Center, Dev Box and Environments REST operations group](https://learn.microsoft.com/rest/api/devcenter/developer/operation-groups).

## Examples
* [Create, Connect and Delete a Dev Box](#create-connect-and-delete-a-dev-box)
* [Deploy and Delete an Environment](#deploy-and-delete-an-environment)

### Create, Connect and Delete a Dev Box

<!-- SNIPPET:dev_box_create_sample.dev_box_create_connect_delete -->

```python
import os

from azure.developer.devcenter import DevCenterClient
from azure.identity import DefaultAzureCredential

# Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
# DEVCENTER_ENDPOINT, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
try:
    endpoint = os.environ["DEVCENTER_ENDPOINT"]
except KeyError:
    raise ValueError("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")

# Build a client through AAD
client = DevCenterClient(endpoint, credential=DefaultAzureCredential())

# List available Projects
projects = client.list_projects()
if projects:
    print("\nList of projects: ")
    for project in projects:
        print(f"{project.name}")

    # Select first project in the list
    target_project_name = list(projects)[0].name
else:
    raise ValueError("Missing Project - please create one before running the example")

# List available Pools
pools = client.list_pools(target_pool_name)
if pools:
    print("\nList of pools: ")
    for pool in pools:
        print(f"{pool.name}")

    # Select first pool in the list
    target_pool_name = list(pools)[0].name
else:
    raise ValueError("Missing Pool - please create one before running the example")

# Stand up a new Dev Box
print(f"\nStarting to create dev box in project {target_project_name} and pool {target_pool_name}")

dev_box_poller = client.begin_create_dev_box(
    target_project_name, "me", "Test_DevBox", {"poolName": target_pool_name}
)
dev_box = dev_box_poller.result()
print(f"Provisioned dev box with status {dev_box.provisioning_state}.")

# Connect to the provisioned Dev Box
remote_connection = client.get_remote_connection(target_project_name, "me", dev_box.name)
print(f"Connect to the dev box using web URL {remote_connection.web_url}")

# Tear down the Dev Box when finished
print(f"Starting to delete dev box.")

delete_poller = client.begin_delete_dev_box(target_project_name, "me", "Test_DevBox")
delete_result = delete_poller.result()
print(f"Completed deletion for the dev box with status {delete_result.status}")
```

<!-- END SNIPPET -->

### Deploy and Delete an Environment

<!-- SNIPPET:deployment_environments_sample.environment_create_and_delete -->

```python
import os

from azure.developer.devcenter import DevCenterClient
from azure.identity import DefaultAzureCredential

# Set the values of the dev center endpoint, client ID, and client secret of the AAD application as environment variables:
# DEVCENTER_ENDPOINT, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
try:
    endpoint = os.environ["DEVCENTER_ENDPOINT"]
except KeyError:
    raise ValueError("Missing environment variable 'DEVCENTER_ENDPOINT' - please set it before running the example")

# Build a client through AAD
client = DevCenterClient(endpoint, credential=DefaultAzureCredential())

# List available Projects
projects = client.list_projects()
if projects:
    print("\nList of projects: ")
    for project in projects:
        print(f"{project.name}")

    # Select first project in the list
    target_project_name = list(projects)[0].name
else:
    raise ValueError("Missing Project - please create one before running the example")

# List available Catalogs
catalogs = client.list_catalogs(target_project_name)
if catalogs:
    print("\nList of catalogs: ")
    for catalog in catalogs:
        print(f"{catalog.name}")

    # Select first catalog in the list
    target_catalog_name = list(catalogs)[0].name
else:
    raise ValueError("Missing Catalog - please create one before running the example")

# List available Environment Definitions
environment_definitions = client.list_environment_definitions_by_catalog(target_project_name, target_catalog_name)
if environment_definitions:
    print("\nList of environment definitions: ")
    for environment_definition in environment_definitions:
        print(f"{environment_definition.name}")

    # Select first environment definition in the list
    target_environment_definition_name = list(environment_definitions)[0].name
else:
    raise ValueError("Missing Environment Definition - please create one before running the example")

# List available Environment Types
environment_types = client.list_environment_types(target_project_name)
if environment_types:
    print("\nList of environment types: ")
    for environment_type in environment_types:
        print(f"{environment_type.name}")

    # Select first environment type in the list
    target_environment_type_name = list(environment_types)[0].name
else:
    raise ValueError("Missing Environment Type - please create one before running the example")

print(
    f"\nStarting to create environment in project {target_project_name} with catalog {target_catalog_name}, environment definition {target_environment_definition_name}, and environment type {target_environment_type_name}."
)

# Stand up a new environment
environment_name = "MyDevEnv"
environment = {
    "environmentType": target_environment_type_name,
    "catalogName": target_catalog_name,
    "environmentDefinitionName": target_environment_definition_name,
}

environment_poller = client.begin_create_or_update_environment(
    target_project_name, "me", environment_name, environment
)
environment_result = environment_poller.result()
print(f"Provisioned environment with status {environment_result.provisioning_state}.")

# Tear down the environment when finished
print(f"Starting to delete environment.")
delete_poller = client.begin_delete_environment(target_project_name, "me", environment_name)
delete_result = delete_poller.result()
print(f"Completed deletion for the environment with status {delete_result.status}")
```

<!-- END SNIPPET -->

## Key concepts
Dev Boxes refer to managed developer machines running in Azure. Dev Boxes are provisioned in Pools, which define the network and image used for a Dev Box.

Environments refer to templated developer environments, which combine a template (Catalog Item) and parameters.

## Troubleshooting
Errors can occur during initial requests and long-running operations, and will provide information about how to resolve the error. 
Be sure to confirm that dependent resources, such as pools and catalogs, are set up properly and are in a healthy state. You will not be able to create resources with the package when your dependent resources are in a failed state.

## Next steps
Get started by exploring our [samples][samples_folder] and starting to use the package!

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
[samples_folder]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/devcenter/azure-developer-devcenter/samples
