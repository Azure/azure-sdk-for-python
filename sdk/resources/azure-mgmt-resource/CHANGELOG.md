# Release History

## 0.0.0 (2022-06-15)



## 21.1.0 (2022-05-05)

**Features**

  - GA `azure.mgmt.resource.changes`


## 21.1.0b1 (2022-04-19)

**Features**

  - Added operation TemplateSpecVersionsOperations.get_built_in
  - Added operation TemplateSpecVersionsOperations.list_built_ins
  - Added operation TemplateSpecsOperations.get_built_in
  - Added operation TemplateSpecsOperations.list_built_ins
  - Added operation group ChangesOperations
  - Combined operation files into one.

**Fixes**

  - Fixed duplicated query parameters in pageable operation(for more details, see https://github.com/Azure/azure-sdk-for-python/issues/23828)

## 21.0.0 (2022-03-22)

**Features**

  - Added operation PrivateLinkAssociationOperations.list
  - Added operation ResourceManagementPrivateLinkOperations.list_by_resource_group

**Breaking changes**

  - Operation PrivateLinkAssociationOperations.get has a new signature

## 20.1.0 (2022-01-25)

**Features**

  - Added operation SubscriptionsOperations.check_zone_peers
  - Added operation group PrivateLinkAssociationOperations
  - Added operation group ResourceManagementPrivateLinkOperations
  - Model ProviderResourceType has a new parameter zone_mappings

## 20.0.0 (2021-09-03)

**Features**

  - Model PolicyAssignment has a new parameter system_data
  - Model PolicyDefinition has a new parameter system_data
  - Model Location has a new parameter type
  - Model PolicySetDefinition has a new parameter system_data
  - Model LocationMetadata has a new parameter home_location
  - Model TenantIdDescription has a new parameter tenant_branding_logo_url
  - Model TenantIdDescription has a new parameter tenant_type
  - Model TenantIdDescription has a new parameter default_domain
  - Added operation PolicyAssignmentsOperations.update_by_id
  - Added operation PolicyAssignmentsOperations.update

**Breaking changes**

  - Operation ProvidersOperations.list_at_tenant_scope has a new signature
  - Operation ProvidersOperations.list has a new signature
  - Operation SubscriptionsOperations.list_locations has a new signature

## 19.0.0 (2021-07-19)

**Breaking changes**

  - Operation SubscriptionFeatureRegistrationsOperations.create_or_update has a new signature
  - Operation SubscriptionFeatureRegistrationsOperations.delete has a new signature
  - Operation SubscriptionFeatureRegistrationsOperations.get has a new signature
  - Operation SubscriptionFeatureRegistrationsOperations.list_by_subscription has a new signature

## 18.1.0 (2021-07-13)

**Features**

  - Added operation group SubscriptionFeatureRegistrationsOperations

## 18.0.0 (2021-05-19)

**Breaking changes**

  - Operation ResourceGroupsOperations.begin_delete has a new signature

## 17.0.0 (2021-05-13)

**Features**

  - Model Provider has a new parameter provider_authorization_consent_state
  - Model TemplateSpec has a new parameter metadata
  - Model GenericResourceExpanded has a new parameter extended_location
  - Model Resource has a new parameter extended_location
  - Model TemplateSpecVersion has a new parameter ui_form_definition
  - Model TemplateSpecVersion has a new parameter metadata
  - Model TemplateSpecVersion has a new parameter linked_templates
  - Model TemplateSpecVersion has a new parameter main_template
  - Model WhatIfChange has a new parameter unsupported_reason
  - Model GenericResource has a new parameter extended_location
  - Added operation ProvidersOperations.provider_permissions

**Breaking changes**

  - Operation ProvidersOperations.register has a new signature
  - Model TemplateSpecVersion no longer has parameter template
  - Model TemplateSpecVersion no longer has parameter artifacts

## 16.1.0 (2021-04-16)

**Features**

  - Model ManagedServiceIdentity has a new parameter tenant_id

## 16.0.0 (2021-02-26)

**Features**

  - Model ParameterDefinitionsValueMetadata has a new parameter strong_type
  - Model ParameterDefinitionsValueMetadata has a new parameter assign_permissions
  - Model ProviderResourceType has a new parameter location_mappings
  - Model DeploymentProperties has a new parameter expression_evaluation_options
  - Model PolicyAssignment has a new parameter non_compliance_messages
  - Model TemplateLink has a new parameter query_string
  - Model TemplateSpec has a new parameter versions
  - Model DeploymentWhatIfProperties has a new parameter expression_evaluation_options
  - Added operation ApplicationDefinitionsOperations.get_by_id
  - Added operation ApplicationDefinitionsOperations.begin_create_or_update_by_id
  - Added operation ApplicationDefinitionsOperations.begin_delete_by_id
  - Added operation ProvidersOperations.register_at_management_group_scope
  - Added operation PolicySetDefinitionsOperations.list_by_management_group
  - Added operation PolicyDefinitionsOperations.list_by_management_group
  - Added operation group ProviderResourceTypesOperations
  - Added operation group DataPolicyManifestsOperations
  - Added operation group ApplicationClientOperationsMixin
  - Added operation group PolicyExemptionsOperations

**Breaking changes**

  - Operation PolicyAssignmentsOperations.list has a new signature
  - Operation PolicyAssignmentsOperations.list_for_management_group has a new signature
  - Operation PolicyAssignmentsOperations.list_for_resource has a new signature
  - Operation PolicyAssignmentsOperations.list_for_resource_group has a new signature
  - Operation TemplateSpecsOperations.get has a new signature
  - Operation TemplateSpecsOperations.list_by_resource_group has a new signature
  - Operation TemplateSpecsOperations.list_by_subscription has a new signature
  - Model PolicyAssignment no longer has parameter sku
  - Operation PolicySetDefinitionsOperations.list_built_in has a new signature
  - Operation PolicySetDefinitionsOperations.list has a new signature
  - Operation PolicyDefinitionsOperations.list_built_in has a new signature
  - Operation PolicyDefinitionsOperations.list has a new signature

## 15.0.0 (2020-09-17)

**Features**

  - Model ProviderResourceType has a new parameter default_api_version
  - Model ProviderResourceType has a new parameter api_profiles
  - Model AzureResourceBase has a new parameter system_data
  - Model AliasPath has a new parameter metadata
  - Model TemplateLink has a new parameter id
  - Model TemplateLink has a new parameter relative_path
  - Model Alias has a new parameter default_metadata
  - Added operation DeploymentsOperations.begin_what_if_at_management_group_scope
  - Added operation DeploymentsOperations.begin_what_if_at_tenant_scope
  - Added operation group TemplateSpecsOperations
  - Added operation group TemplateSpecVersionsOperations
  - Added operation group SubscriptionClientOperationsMixin

## 15.0.0b1 (2020-06-17)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

# 10.0.0 (2020-06-02)

**Features**

  - Model AzurePowerShellScript has a new parameter storage_account_settings
  - Model DeploymentOperationProperties has a new parameter provisioning_operation
  - Model AzureCliScript has a new parameter storage_account_settings

**Breaking changes**

  - Model AliasPathType no longer has parameter pattern

## 9.0.0 (2020-03-31)

**Features**

  - Model Location has a new parameter metadata
  - Model Location has a new parameter regional_display_name
  - Model Deployment has a new parameter tags
  - Model AliasPathType has a new parameter pattern
  - Model ScopedDeployment has a new parameter tags
  - Model DeploymentPropertiesExtended has a new parameter template_hash
  - Model DeploymentPropertiesExtended has a new parameter validated_resources
  - Model DeploymentPropertiesExtended has a new parameter error
  - Model DeploymentPropertiesExtended has a new parameter output_resources
  - Model DeploymentExtended has a new parameter tags
  - Model Subscription has a new parameter tags
  - Added operation FeaturesOperations.unregister
  - Added operation TagsOperations.get_at_scope
  - Added operation TagsOperations.update_at_scope
  - Added operation TagsOperations.delete_at_scope
  - Added operation TagsOperations.create_or_update_at_scope
  - Added operation group DeploymentScriptsOperations

**Breaking changes**

  - Model Location no longer has parameter latitude
  - Model Location no longer has parameter longitude
  - Model DeploymentPropertiesExtended no longer has parameter template
  - Model TagsResource no longer has parameter tags
  - Model TagsResource no longer has parameter location
  - Operation DeploymentsOperations.validate_at_management_group_scope has a new signature
  - Operation DeploymentsOperations.validate_at_subscription_scope has a new signature
  - Operation DeploymentsOperations.create_or_update_at_subscription_scope has a new signature
  - Operation DeploymentsOperations.create_or_update_at_tenant_scope has a new signature
  - Operation DeploymentsOperations.create_or_update_at_scope has a new signature
  - Operation DeploymentsOperations.validate has a new signature
  - Operation DeploymentsOperations.create_or_update has a new signature
  - Operation DeploymentsOperations.validate_at_scope has a new signature
  - Operation DeploymentsOperations.validate_at_tenant_scope has a new signature
  - Operation DeploymentsOperations.create_or_update_at_management_group_scope has a new signature
  - Model TenantIdDescription has a new signature
  - Removed operation TagsOperations.resource_get
  - Removed operation TagsOperations.resource_delete
  - Removed operation TagsOperations.resource_create
  - Removed operation TagsOperations.resource_update

## 8.0.1 (2020-02-04)

**Bugfixes**

- Added missing API versions

## 8.0.0 (2020-01-24)

**Features**

- Added operation PolicyAssignmentsOperations.list_for_management_group

**Breaking changes**

- Operation DeploymentsOperations.create_or_update_at_tenant_scope has a new signature
- Operation DeploymentsOperations.validate_at_tenant_scope has a new signature
- Operation DeploymentsOperations.validate_at_management_group_scope has a new signature
- Operation DeploymentsOperations.create_or_update_at_management_group_scope has a new signature

## 7.0.0 (2019-12-07)

**Features**

  - Model TenantIdDescription has a new parameter display_name
  - Model TenantIdDescription has a new parameter domains
  - Model Application has a new parameter ui_definition_uri
  - Model ApplicationPatchable has a new parameter ui_definition_uri

**Breaking changes**

  - Operation
    DeploymentsOperations.create_or_update_at_tenant_scope has a
    new signature
  - Operation
    DeploymentsOperations.create_or_update_at_management_group_scope
    has a new signature
  - Operation
    DeploymentsOperations.validate_at_management_group_scope has a
    new signature
  - Operation DeploymentsOperations.validate_at_tenant_scope has a
    new signature
  - Model PolicySetDefinition no longer has parameter
    policy_definition_groups
  - Model Subscription no longer has parameter managed_by_tenants
  - Model DeploymentValidateResult no longer has parameter error
  - Removed operation DeploymentsOperations.what_if
  - Removed operation
    DeploymentsOperations.what_if_at_subscription_scope
  - Model PolicyDefinitionReference has a new signature

## 6.0.0 (2019-11-01)

**Features**

  - Model PolicySetDefinition has a new parameter
    policy_definition_groups

**Breaking changes**

  - Operation DeploymentsOperations.validate_at_tenant_scope has a
    new signature
  - Operation
    DeploymentsOperations.create_or_update_at_management_group_scope
    has a new signature
  - Operation
    DeploymentsOperations.validate_at_management_group_scope has a
    new signature
  - Operation
    DeploymentsOperations.create_or_update_at_tenant_scope has a
    new signature
  - Model PolicyDefinitionReference has a new signature

## 5.1.0 (2019-10-04)

**Features**

  - Added operation DeploymentsOperations.what_if
  - Added operation
    DeploymentsOperations.what_if_at_subscription_scope

## 5.0.0 (2019-09-22)

**Features**

  - Model DeploymentValidateResult has a new parameter error
  - Model Subscription has a new parameter managed_by_tenants

**Breaking changes**

  - Model Application no longer has parameter ui_definition_uri
  - Model ApplicationPatchable no longer has parameter
    ui_definition_uri
  - Model TenantIdDescription no longer has parameter display_name
  - Model TenantIdDescription no longer has parameter domains

## 4.0.0 (2019-09-03)

**Features**

  - Model PolicyAssignment has a new parameter enforcement_mode
  - Added operation DeploymentOperations.get_at_scope
  - Added operation DeploymentOperations.list_at_tenant_scope
  - Added operation DeploymentOperations.get_at_tenant_scope
  - Added operation DeploymentOperations.list_at_scope
  - Added operation
    DeploymentsOperations.create_or_update_at_tenant_scope
  - Added operation DeploymentsOperations.list_at_tenant_scope
  - Added operation DeploymentsOperations.delete_at_scope
  - Added operation DeploymentsOperations.cancel_at_tenant_scope
  - Added operation DeploymentsOperations.list_at_scope
  - Added operation DeploymentsOperations.get_at_scope
  - Added operation
    DeploymentsOperations.export_template_at_tenant_scope
  - Added operation DeploymentsOperations.validate_at_scope
  - Added operation DeploymentsOperations.delete_at_tenant_scope
  - Added operation DeploymentsOperations.export_template_at_scope
  - Added operation DeploymentsOperations.validate_at_tenant_scope
  - Added operation DeploymentsOperations.create_or_update_at_scope
  - Added operation
    DeploymentsOperations.check_existence_at_tenant_scope
  - Added operation DeploymentsOperations.check_existence_at_scope
  - Added operation DeploymentsOperations.cancel_at_scope
  - Added operation DeploymentsOperations.get_at_tenant_scope
  - Added operation DeploymentsOperations.calculate_template_hash
  - Added operation ProvidersOperations.list_at_tenant_scope
  - Added operation ProvidersOperations.get_at_tenant_scope

**Breaking changes**

  - Model DeploymentValidateResult no longer has parameter error
  - Model ErrorResponse has a new signature

## 3.1.0 (2019-07-20)

**Features**

  - Model TenantIdDescription has a new parameter domains
  - Model TenantIdDescription has a new parameter display_name

## 3.0.0 (2019-06-13)

**Features**

  - Model Provider has a new parameter registration_policy
  - Model ProviderResourceType has a new parameter capabilities
  - Model DeploymentOperationProperties has a new parameter duration
  - Model DeploymentPropertiesExtended has a new parameter duration
  - Added operation
    DeploymentOperations.get_at_management_group_scope
  - Added operation
    DeploymentOperations.list_at_management_group_scope
  - Added operation
    DeploymentsOperations.export_template_at_management_group_scope
  - Added operation
    DeploymentsOperations.create_or_update_at_management_group_scope
  - Added operation
    DeploymentsOperations.list_at_management_group_scope
  - Added operation
    DeploymentsOperations.get_at_management_group_scope
  - Added operation
    DeploymentsOperations.check_existence_at_management_group_scope
  - Added operation
    DeploymentsOperations.cancel_at_management_group_scope
  - Added operation
    DeploymentsOperations.delete_at_management_group_scope
  - Added operation
    DeploymentsOperations.validate_at_management_group_scope
  - Policy default API version is now 2018-05-01

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

The following applies for all client and namespaces, we take
ResourceManagementClient and "resources" as example: -
ResourceManagementClient cannot be imported from
`azure.mgmt.resource.resources.v20xx_yy_zz.resource_management_client`
anymore (import from `azure.mgmt.resource.resources.v20xx_yy_zz`
works like before) - ResourceManagementClientConfiguration import has
been moved from
`azure.mgmt.resource.resources.v20xx_yy_zz.resource_management_client`
to `azure.mgmt.resource.resources.v20xx_yy_zz` - A model `MyClass`
from a "models" sub-module cannot be imported anymore using
`azure.mgmt.resource.resources.v20xx_yy_zz.models.my_class` (import
from `azure.mgmt.resource.resources.v20xx_yy_zz.models` works like
before) - An operation class `MyClassOperations` from an
`operations` sub-module cannot be imported anymore using
`azure.mgmt.resource.resources.v20xx_yy_zz.operations.my_class_operations`
(import from `azure.mgmt.resource.resources.v20xx_yy_zz.operations`
works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 2.2.0 (2019-05-23)

**Features on Subscriptions**

  - tenant_id is now returned part of the subscription information

**Features on Locks**

  - Add list_by_scope

## 2.1.0 (2019-02-01)

**Features on Policy**

  - New API version for Policy 2018-05-01
  - Model PolicyAssignment has a new parameter location
  - Model PolicyAssignment has a new parameter identity

## 2.0.0 (2018-07-20)

**Features**

  - Identity class has now a user_assigned_identities attribute
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 2.0.0rc2 (2018-06-13)

**Features on Policy**

  - New API version for Policy 2018-03-01. This a merge of
    2017-06-01-preview and 2016-12-01 and has no external API breaking.

**Features on Resources**

  - Resources new Api Version 2018-05-01
  - Model Deployment has a new parameter location
  - Model DeploymentExtended has a new parameter location
  - Added operation
    DeploymentsOperations.export_template_at_subscription_scope
  - Added operation DeploymentsOperations.get_at_subscription_scope
  - Added operation
    DeploymentsOperations.cancel_at_subscription_scope
  - Added operation
    DeploymentsOperations.delete_at_subscription_scope
  - Added operation
    DeploymentsOperations.create_or_update_at_subscription_scope
  - Added operation
    DeploymentsOperations.validate_at_subscription_scope
  - Added operation
    DeploymentsOperations.check_existence_at_subscription_scope
  - Added operation DeploymentsOperations.list_at_subscription_scope
  - Added operation DeploymentOperations.get_at_subscription_scope
  - Added operation DeploymentOperations.list_at_subscription_scope

**Breaking changes on Resources**

  - Operation DeploymentsOperations.create_or_update lost its ignored
    "location" parameter.
  - Operation DeploymentsOperations.validate lost its ignored "location"
    parameter.

**Common features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 2.0.0rc1 (2018-04-23)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Features**

  - Add new ApiVersion 2018-02-01 (new default):
      - Add on_error_deployment
      - Support MSI in generic ARM resources
  - All clients now support Azure profiles.
  - Add generic resources update (2017-05-10 and 2018-02-01)
  - Add version to Plan

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 1.2.2 (2017-10-17)

**Bug fixes**

  - Unicode strings are valid "subscription_id" in Python 2.7
  - Added some deprecation warnings

## 1.2.1 (2017-10-06)

**Bugfixes**

  - "Get" on unkwon policy resources should raise and not return None

## 1.2.0 (2017-10-05)

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
      - Add policy set definitions to policy_assignments operations
        group
      - Add skus to policy assignment

**Bug fixes**

  - Do not fail on 204 when deleting a policy assignment (2016-12-01)

**Breaking changes to preview clients**

  - Major renaming into ManagedApplication client, and GA ApiVersion
    2017-09-01

**Disclaimer**

  - We removed the "filter" parameter of policy_definitions.list
    method. However, we don't upgrade the major version of the package,
    since this parameter has no meaning for the RestAPI and there is no
    way any Python users would have been able to use it anyway.

## 1.1.0 (2017-05-15)

  - Tag 1.1.0rc2 as stable (same content)

## 1.1.0rc2 (2017-05-12)

  - Add Policy ApiVersion 2015-10-01-preview (AzureStack default)

## 1.1.0rc1 (2017-05-08)

  - New default ApiVersion is now 2017-05-10. Breaking changes described
    in 1.0.0rc3 are now applied by default.

## 1.0.0rc3 (2017-05-04)

**Bug fixes**

  - Subscriptions: Removed deprecated tenant ID
  - Managed Applications: All list methods return an iterator

**New Resources ApiVersion 2017-05-10**

  - Deploy resources to multiple resource groups from one template

  - Some breaking changes are introduced compared to previous versions:

    >   - deployments.list has been renamed
    >     deployments.list_by_resource_group
    >   - resource_groups.list_resources has been moved to
    >     resources.list_by_resource_group
    >   - resource_groups.patch has been renamed to
    >     resource_groups.update and now takes an instance of
    >     ResourceGroupPatchable (and not ResourceGroup).

The default is still 2016-09-01 in this package, waiting for the
ApiVersion to be widely available.

## 1.0.0rc2 (2017-05-02)

  - Add Managed Applications client (preview)

## 1.0.0rc1 (2017-04-11)

**Bug fixes**

  - tag_count is now correctly an int and not a string
  - deployment_properties is now required for all deployments
    operations as expected

**Breaking Changes**

  - Locks moves to a new ApiVersion and brings several consistent naming
    refactoring and new methods

**Features**

To help customers with sovereign clouds (not general Azure), this
version has official multi ApiVersion support for the following resource
type:

  - Locks: 2015-01-01 and 2016-09-01
  - Policy: 2016-04-01 and 2016-12-01
  - Resources: 2016-02-01 and 2016-09-01

The following resource types support one ApiVersion:

  - Features: 2015-12-01
  - Links: 2016-09-01
  - Subscriptions: 2016-06-01

## 0.31.0 (2016-11-10)

**Breaking change**

  - Resource.Links 'create_or_update' method has simpler parameters

## 0.30.2 (2016-10-20)

**Features**

  - Add Resource.Links client

## 0.30.1 (2016-10-17)

**Bugfixes**

  - Location is now correctly declared optional and not required.

## 0.30.0 (2016-10-04)

  - Preview release. Based on API version 2016-09-01.

## 0.20.0 (2015-08-31)

  - Initial preview release. Based on API version 2014-04-01-preview
