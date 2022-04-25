How to Find the SDK in CLI 
======

This article aims to provide a guide for customer to find the sdk in Azure CLI.

Find SDK function in cli command is divided into the following steps:
1. Determine the command module
2. Search its definition in `command.py`
3. Find the management client and corresponding SDK
4. Find the function in Python SDK or Doc

## Determine the command module

Before looking for the SDK, please determine the command module you want to find. You can find it through the keyword in the CLI and the corresponding way [here](https://github.com/Azure/azure-cli/tree/dev/src/azure-cli/azure/cli/command_modules).

Such as, if you want to find the module about `az resource group create`, you could find [`resource` folder](https://github.com/Azure/azure-cli/tree/dev/src/azure-cli/azure/cli/command_modules/resource) in above link.

## Search its definition in `command.py`

After entering the link, a command module folder generally contains the following files. You can find the command in `command.py`.
```
└─command module folder
    └─ _help.py    # Store help information
    └─ command.py    # Store command definition
    └─ custom.py    # Store Custom method
    └─ _params.py   # Store parameters information
    └─....
```
Still the above sample `az resource group create`, You can find its definition on line 222 from [here](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/resource/commands.py#L222).

## Find the management client and corresponding SDK
```python
with self.command_group('group', resource_group_sdk, resource_type=ResourceType.MGMT_RESOURCE_RESOURCES) as g:
    g.command('delete', 'begin_delete', supports_no_wait=True, confirmation=True)
    g.show_command('show', 'get')
    g.command('exists', 'check_existence')
    g.custom_command('list', 'list_resource_groups', table_transformer=transform_resource_group_list)
    g.custom_command('create', 'create_resource_group')
    g.custom_command('export', 'export_group_as_template')
    g.generic_update_command('update', custom_func_name='update_resource_group', custom_func_type=resource_custom)
    g.wait_command('wait')
```

Taking the above code as an example, follow the  `resource_type` parameter in `command_group()` function find SDK name and client. like searching for the `MGMT_RESOURCE_RESOURCES` definition.
```python
# src/azure-cli-core/azure/cli/core/profiles/_shared.py
MGMT_RESOURCE_RESOURCES = ('azure.mgmt.resource.resources', 'ResourceManagementClient')
```
You could find that its package name is `azure-mgmt-resource` and its client name is `ResourceManagementClient`.

Then, you could it can be divided into three types in `command_group()` function: command()` function, `show_command()` function and `custom_command()` function.<br/>

For the first two function, the first parameter comes from the CLI command, and the second parameter comes from the function name of the SDK.
If you want to find the SDK function about `az resource group delete`, it is the `begin_delete`.<br/>
![img.png](find_the_sdk.PNG)
If it is a `custom_command()` function, you could find its definition in the `custom.py` In the peer path.
Such as `create_resource_group()`, you could find the definition from [here](https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/resource/custom.py#L1310). (If it is not found, you could search for `create_resource_group` in this file.)
```python
def create_resource_group(cmd, rg_name, location, tags=None, managed_by=None):
    """ Create a new resource group.
    :param str resource_group_name:the desired resource group name
    :param str location:the resource group location
    :param str tags:tags in 'a=b c' format
    """
    rcf = _resource_client_factory(cmd.cli_ctx)

    ResourceGroup = cmd.get_models('ResourceGroup')
    parameters = ResourceGroup(
        location=location,
        tags=tags
    )

    if cmd.supported_api_version(min_api='2016-09-01'):
        parameters.managed_by = managed_by

    return rcf.resource_groups.create_or_update(rg_name, parameters)
```
Then, you could find the `create_or_update()` function in its return, it is the SDK function.

## Find the function in Python SDK or Doc

Similarly, find the `service` folder in the [SDK folder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk) of [SDK repo](https://github.com/Azure/azure-sdk-for-python).
Such as [`resources` folder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/resources).

Then, you could find [here](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/resources/azure-mgmt-resource/azure/mgmt/resource/resources). This step may be a little difficult for beginners. It requires some experience.
Don't be frightened by a lot of folders here. You can choose the latest date to enter, like [this](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/resources/azure-mgmt-resource/azure/mgmt/resource/resources/v2021_04_01).

Enter the [_operation.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/resources/azure-mgmt-resource/azure/mgmt/resource/resources/v2021_04_01/operations/_operations.py) in the [operation folder](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/resources/azure-mgmt-resource/azure/mgmt/resource/resources/v2021_04_01/operations), and you can see the meta code.

In this file, you could search the function name to find the function definition.(Be careful, the function need under the correct class.)
Above the `begin_delete` function, you could find it from [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/resources/azure-mgmt-resource/azure/mgmt/resource/resources/v2021_04_01/operations/_operations.py#L8784).
The same, the `create_or_update` function is [here](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/resources/azure-mgmt-resource/azure/mgmt/resource/resources/v2021_04_01/operations/_operations.py#L9761).

Finally, you also could find the usage of function by [Azure doc](https://docs.microsoft.com/en-us/azure/developer/python/sdk/examples/azure-sdk-example-resource-group#3-write-code-to-provision-a-resource-group) or [Azure samples](https://github.com/Azure-Samples/azure-samples-python-management).

Feel free to contact Azure SDK team at any time through any channels. We are passionate to build the world-class cloud product.
