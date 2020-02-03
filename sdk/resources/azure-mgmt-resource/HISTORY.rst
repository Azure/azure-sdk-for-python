.. :changelog:

Release History
===============

8.0.0 (2020-01-24)
++++++++++++++++++

**Features**

- Added operation PolicyAssignmentsOperations.list_for_management_group

**Breaking changes**

- Operation DeploymentsOperations.create_or_update_at_tenant_scope has a new signature
- Operation DeploymentsOperations.validate_at_tenant_scope has a new signature
- Operation DeploymentsOperations.validate_at_management_group_scope has a new signature
- Operation DeploymentsOperations.create_or_update_at_management_group_scope has a new signature

7.0.0 (2019-12-07)
++++++++++++++++++

**Features**

- Model TenantIdDescription has a new parameter display_name
- Model TenantIdDescription has a new parameter domains
- Model Application has a new parameter ui_definition_uri
- Model ApplicationPatchable has a new parameter ui_definition_uri

**Breaking changes**

- Operation DeploymentsOperations.create_or_update_at_tenant_scope has a new signature
- Operation DeploymentsOperations.create_or_update_at_management_group_scope has a new signature
- Operation DeploymentsOperations.validate_at_management_group_scope has a new signature
- Operation DeploymentsOperations.validate_at_tenant_scope has a new signature
- Model PolicySetDefinition no longer has parameter policy_definition_groups
- Model Subscription no longer has parameter managed_by_tenants
- Model DeploymentValidateResult no longer has parameter error
- Removed operation DeploymentsOperations.what_if
- Removed operation DeploymentsOperations.what_if_at_subscription_scope
- Model PolicyDefinitionReference has a new signature

6.0.0 (2019-11-01)
++++++++++++++++++

**Features**

- Model PolicySetDefinition has a new parameter policy_definition_groups

**Breaking changes**

- Operation DeploymentsOperations.validate_at_tenant_scope has a new signature
- Operation DeploymentsOperations.create_or_update_at_management_group_scope has a new signature
- Operation DeploymentsOperations.validate_at_management_group_scope has a new signature
- Operation DeploymentsOperations.create_or_update_at_tenant_scope has a new signature
- Model PolicyDefinitionReference has a new signature

5.1.0 (2019-10-04)
++++++++++++++++++

**Features**

- Added operation DeploymentsOperations.what_if
- Added operation DeploymentsOperations.what_if_at_subscription_scope

5.0.0 (2019-09-22)
++++++++++++++++++

**Features**

- Model DeploymentValidateResult has a new parameter error
- Model Subscription has a new parameter managed_by_tenants

**Breaking changes**

- Model Application no longer has parameter ui_definition_uri
- Model ApplicationPatchable no longer has parameter ui_definition_uri
- Model TenantIdDescription no longer has parameter display_name
- Model TenantIdDescription no longer has parameter domains

4.0.0 (2019-09-03)
++++++++++++++++++

**Features**

- Model PolicyAssignment has a new parameter enforcement_mode
- Added operation DeploymentOperations.get_at_scope
- Added operation DeploymentOperations.list_at_tenant_scope
- Added operation DeploymentOperations.get_at_tenant_scope
- Added operation DeploymentOperations.list_at_scope
- Added operation DeploymentsOperations.create_or_update_at_tenant_scope
- Added operation DeploymentsOperations.list_at_tenant_scope
- Added operation DeploymentsOperations.delete_at_scope
- Added operation DeploymentsOperations.cancel_at_tenant_scope
- Added operation DeploymentsOperations.list_at_scope
- Added operation DeploymentsOperations.get_at_scope
- Added operation DeploymentsOperations.export_template_at_tenant_scope
- Added operation DeploymentsOperations.validate_at_scope
- Added operation DeploymentsOperations.delete_at_tenant_scope
- Added operation DeploymentsOperations.export_template_at_scope
- Added operation DeploymentsOperations.validate_at_tenant_scope
- Added operation DeploymentsOperations.create_or_update_at_scope
- Added operation DeploymentsOperations.check_existence_at_tenant_scope
- Added operation DeploymentsOperations.check_existence_at_scope
- Added operation DeploymentsOperations.cancel_at_scope
- Added operation DeploymentsOperations.get_at_tenant_scope
- Added operation DeploymentsOperations.calculate_template_hash
- Added operation ProvidersOperations.list_at_tenant_scope
- Added operation ProvidersOperations.get_at_tenant_scope

**Breaking changes**

- Model DeploymentValidateResult no longer has parameter error
- Model ErrorResponse has a new signature

3.1.0 (2019-07-20)
++++++++++++++++++

**Features**

- Model TenantIdDescription has a new parameter domains
- Model TenantIdDescription has a new parameter display_name

3.0.0 (2019-06-13)
++++++++++++++++++

**Features**

- Model Provider has a new parameter registration_policy
- Model ProviderResourceType has a new parameter capabilities
- Model DeploymentOperationProperties has a new parameter duration
- Model DeploymentPropertiesExtended has a new parameter duration
- Added operation DeploymentOperations.get_at_management_group_scope
- Added operation DeploymentOperations.list_at_management_group_scope
- Added operation DeploymentsOperations.export_template_at_management_group_scope
- Added operation DeploymentsOperations.create_or_update_at_management_group_scope
- Added operation DeploymentsOperations.list_at_management_group_scope
- Added operation DeploymentsOperations.get_at_management_group_scope
- Added operation DeploymentsOperations.check_existence_at_management_group_scope
- Added operation DeploymentsOperations.cancel_at_management_group_scope
- Added operation DeploymentsOperations.delete_at_management_group_scope
- Added operation DeploymentsOperations.validate_at_management_group_scope

- Policy default API version is now 2018-05-01

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes if you were importing from the v20xx_yy_zz API folders.
In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

The following applies for all client and namespaces, we take ResourceManagementClient and "resources" as example:
- ResourceManagementClient cannot be imported from `azure.mgmt.resource.resources.v20xx_yy_zz.resource_management_client` anymore (import from `azure.mgmt.resource.resources.v20xx_yy_zz` works like before)
- ResourceManagementClientConfiguration import has been moved from `azure.mgmt.resource.resources.v20xx_yy_zz.resource_management_client` to `azure.mgmt.resource.resources.v20xx_yy_zz`
- A model `MyClass` from a "models" sub-module cannot be imported anymore using `azure.mgmt.resource.resources.v20xx_yy_zz.models.my_class` (import from `azure.mgmt.resource.resources.v20xx_yy_zz.models` works like before)
- An operation class `MyClassOperations` from an `operations` sub-module cannot be imported anymore using `azure.mgmt.resource.resources.v20xx_yy_zz.operations.my_class_operations` (import from `azure.mgmt.resource.resources.v20xx_yy_zz.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.

2.2.0 (2019-05-23)
++++++++++++++++++

**Features on Subscriptions**

- tenant_id is now returned part of the subscription information

**Features on Locks**

- Add list_by_scope

2.1.0 (2019-02-01)
++++++++++++++++++

**Features on Policy**

- New API version for Policy 2018-05-01
- Model PolicyAssignment has a new parameter location
- Model PolicyAssignment has a new parameter identity

2.0.0 (2018-07-20)
++++++++++++++++++

**Features**

- Identity class has now a user_assigned_identities attribute
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

2.0.0rc2 (2018-06-13)
+++++++++++++++++++++

**Features on Policy**

- New API version for Policy 2018-03-01. This a merge of 2017-06-01-preview and 2016-12-01 and has no external API breaking.

**Features on Resources**

- Resources new Api Version 2018-05-01
- Model Deployment has a new parameter location
- Model DeploymentExtended has a new parameter location
- Added operation DeploymentsOperations.export_template_at_subscription_scope
- Added operation DeploymentsOperations.get_at_subscription_scope
- Added operation DeploymentsOperations.cancel_at_subscription_scope
- Added operation DeploymentsOperations.delete_at_subscription_scope
- Added operation DeploymentsOperations.create_or_update_at_subscription_scope
- Added operation DeploymentsOperations.validate_at_subscription_scope
- Added operation DeploymentsOperations.check_existence_at_subscription_scope
- Added operation DeploymentsOperations.list_at_subscription_scope
- Added operation DeploymentOperations.get_at_subscription_scope
- Added operation DeploymentOperations.list_at_subscription_scope

**Breaking changes on Resources**

- Operation DeploymentsOperations.create_or_update lost its ignored "location" parameter.
- Operation DeploymentsOperations.validate lost its ignored "location" parameter.

**Common features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance

2.0.0rc1 (2018-04-23)
+++++++++++++++++++++

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Features**

- Add new ApiVersion 2018-02-01 (new default):

  - Add on_error_deployment
  - Support MSI in generic ARM resources

- All clients now support Azure profiles.
- Add generic resources update (2017-05-10 and 2018-02-01)
- Add version to Plan

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

1.2.2 (2017-10-17)
++++++++++++++++++

**Bug fixes**

- Unicode strings are valid "subscription_id" in Python 2.7
- Added some deprecation warnings

1.2.1 (2017-10-06)
++++++++++++++++++

**Bugfixes**

- "Get" on unkwon policy resources should raise and not return None

1.2.0 (2017-10-05)
++++++++++++++++++

**Features**

- Add validate_move_resources
- Add mode and metadata to PolicyDefinition
- Add policy_definitions.get_built_in
- Add policy_definitions.list_built_in
- Add policy_definitions.create_or_update_at_management_group
- Add policy_definitions.delete_at_management_group
- Add policy_definitions.get_at_management_group
- Add policy_definitions.list_by_management_group

- Add preview version of Policy 2017-06-01-preview:

  - Add policy_set_definitions operations group
  - Add policy set definitions to policy_assignments operations group
  - Add skus to policy assignment

**Bug fixes**

- Do not fail on 204 when deleting a policy assignment (2016-12-01)

**Breaking changes to preview clients**

* Major renaming into ManagedApplication client, and GA ApiVersion 2017-09-01

**Disclaimer**

- We removed the "filter" parameter of policy_definitions.list method.
  However, we don't upgrade the  major version of the package, since this parameter has no meaning
  for the RestAPI and there is no way any Python users would have been able to use it anyway.

1.1.0 (2017-05-15)
++++++++++++++++++

- Tag 1.1.0rc2 as stable (same content)

1.1.0rc2 (2017-05-12)
+++++++++++++++++++++

- Add Policy ApiVersion 2015-10-01-preview (AzureStack default)

1.1.0rc1 (2017-05-08)
+++++++++++++++++++++

- New default ApiVersion is now 2017-05-10. Breaking changes described in 1.0.0rc3 are now applied by default.

1.0.0rc3 (2017-05-04)
+++++++++++++++++++++

**Bug fixes**

- Subscriptions: Removed deprecated tenant ID
- Managed Applications: All list methods return an iterator

**New Resources ApiVersion 2017-05-10**

- Deploy resources to multiple resource groups from one template
- Some breaking changes are introduced compared to previous versions:

   - deployments.list has been renamed deployments.list_by_resource_group
   - resource_groups.list_resources has been moved to resources.list_by_resource_group
   - resource_groups.patch has been renamed to resource_groups.update and now takes an instance of ResourceGroupPatchable (and not ResourceGroup).

The default is still 2016-09-01 in this package, waiting for the ApiVersion to be widely available.

1.0.0rc2 (2017-05-02)
+++++++++++++++++++++

- Add Managed Applications client (preview)

1.0.0rc1 (2017-04-11)
+++++++++++++++++++++

**Bug fixes**

- tag_count is now correctly an int and not a string
- deployment_properties is now required for all deployments operations as expected

**Breaking Changes**

- Locks moves to a new ApiVersion and brings several consistent naming refactoring and new methods

**Features**

To help customers with sovereign clouds (not general Azure),
this version has official multi ApiVersion support for the following resource type:

- Locks: 2015-01-01 and 2016-09-01
- Policy: 2016-04-01 and 2016-12-01
- Resources: 2016-02-01 and 2016-09-01

The following resource types support one ApiVersion:

- Features: 2015-12-01
- Links: 2016-09-01
- Subscriptions: 2016-06-01

0.31.0 (2016-11-10)
+++++++++++++++++++

**Breaking change**

- Resource.Links 'create_or_update' method has simpler parameters

0.30.2 (2016-10-20)
+++++++++++++++++++

**Features**

- Add Resource.Links client


0.30.1 (2016-10-17)
+++++++++++++++++++

**Bugfixes**

- Location is now correctly declared optional and not required.

0.30.0 (2016-10-04)
+++++++++++++++++++

* Preview release. Based on API version 2016-09-01.

0.20.0 (2015-08-31)
+++++++++++++++++++

* Initial preview release. Based on API version 2014-04-01-preview
