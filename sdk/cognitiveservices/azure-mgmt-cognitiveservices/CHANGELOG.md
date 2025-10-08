# Release History

## 14.0.0 (2025-09-22)

### Features Added

  - Added model `NetworkInjection`

### Breaking Changes

  - Deleted or renamed model `NetworkInjections`
  - Deleted or renamed operation group `CognitiveServicesManagementClientOperationsMixin`

## 13.7.0 (2025-07-21)

### Features Added

  - Client `CognitiveServicesManagementClient` added operation group `projects`
  - Client `CognitiveServicesManagementClient` added operation group `account_connections`
  - Client `CognitiveServicesManagementClient` added operation group `project_connections`
  - Client `CognitiveServicesManagementClient` added operation group `account_capability_hosts`
  - Client `CognitiveServicesManagementClient` added operation group `project_capability_hosts`
  - Model `AccountProperties` added property `network_injections`
  - Model `AccountProperties` added property `allow_project_management`
  - Model `AccountProperties` added property `default_project`
  - Model `AccountProperties` added property `associated_projects`
  - Model `DeploymentProperties` added property `spillover_deployment_name`
  - Enum `ProvisioningState` added member `CANCELED`
  - Added model `AADAuthTypeConnectionProperties`
  - Added model `AccessKeyAuthTypeConnectionProperties`
  - Added model `AccountKeyAuthTypeConnectionProperties`
  - Added model `ApiKeyAuthConnectionProperties`
  - Added model `CapabilityHost`
  - Added enum `CapabilityHostKind`
  - Added model `CapabilityHostProperties`
  - Added enum `CapabilityHostProvisioningState`
  - Added model `ConnectionAccessKey`
  - Added model `ConnectionAccountKey`
  - Added model `ConnectionApiKey`
  - Added enum `ConnectionAuthType`
  - Added enum `ConnectionCategory`
  - Added enum `ConnectionGroup`
  - Added model `ConnectionManagedIdentity`
  - Added model `ConnectionOAuth2`
  - Added model `ConnectionPersonalAccessToken`
  - Added model `ConnectionPropertiesV2`
  - Added model `ConnectionPropertiesV2BasicResource`
  - Added model `ConnectionPropertiesV2BasicResourceArmPaginatedResult`
  - Added model `ConnectionServicePrincipal`
  - Added model `ConnectionSharedAccessSignature`
  - Added model `ConnectionUpdateContent`
  - Added model `ConnectionUsernamePassword`
  - Added model `CustomKeys`
  - Added model `CustomKeysConnectionProperties`
  - Added model `ManagedIdentityAuthTypeConnectionProperties`
  - Added enum `ManagedPERequirement`
  - Added enum `ManagedPEStatus`
  - Added model `NetworkInjections`
  - Added model `NoneAuthTypeConnectionProperties`
  - Added model `OAuth2AuthTypeConnectionProperties`
  - Added model `PATAuthTypeConnectionProperties`
  - Added model `Project`
  - Added model `ProjectListResult`
  - Added model `ProjectProperties`
  - Added model `ResourceBase`
  - Added model `SASAuthTypeConnectionProperties`
  - Added enum `ScenarioType`
  - Added model `ServicePrincipalAuthTypeConnectionProperties`
  - Added model `UsernamePasswordAuthTypeConnectionProperties`
  - Added operation group `AccountCapabilityHostsOperations`
  - Added operation group `AccountConnectionsOperations`
  - Added operation group `ProjectCapabilityHostsOperations`
  - Added operation group `ProjectConnectionsOperations`
  - Added operation group `ProjectsOperations`

## 13.7.0b1 (2025-05-15)

### Features Added

  - Client `CognitiveServicesManagementClient` added operation group `projects`
  - Client `CognitiveServicesManagementClient` added operation group `account_connection`
  - Client `CognitiveServicesManagementClient` added operation group `project_connection`
  - Client `CognitiveServicesManagementClient` added operation group `account_capability_hosts`
  - Client `CognitiveServicesManagementClient` added operation group `project_capability_hosts`
  - Model `AccountProperties` added property `network_injections`
  - Model `AccountProperties` added property `allow_project_management`
  - Model `AccountProperties` added property `default_project`
  - Model `AccountProperties` added property `associated_projects`
  - Model `DeploymentProperties` added property `spillover_deployment_name`
  - Enum `ProvisioningState` added member `CANCELED`
  - Added model `AADAuthTypeConnectionProperties`
  - Added model `AccessKeyAuthTypeConnectionProperties`
  - Added model `AccountKeyAuthTypeConnectionProperties`
  - Added model `ApiKeyAuthConnectionProperties`
  - Added model `CapabilityHost`
  - Added enum `CapabilityHostKind`
  - Added model `CapabilityHostProperties`
  - Added enum `CapabilityHostProvisioningState`
  - Added model `ConnectionAccessKey`
  - Added model `ConnectionAccountKey`
  - Added model `ConnectionApiKey`
  - Added enum `ConnectionAuthType`
  - Added enum `ConnectionCategory`
  - Added enum `ConnectionGroup`
  - Added model `ConnectionManagedIdentity`
  - Added model `ConnectionOAuth2`
  - Added model `ConnectionPersonalAccessToken`
  - Added model `ConnectionPropertiesV2`
  - Added model `ConnectionPropertiesV2BasicResource`
  - Added model `ConnectionPropertiesV2BasicResourceArmPaginatedResult`
  - Added model `ConnectionServicePrincipal`
  - Added model `ConnectionSharedAccessSignature`
  - Added model `ConnectionUpdateContent`
  - Added model `ConnectionUsernamePassword`
  - Added model `CustomKeys`
  - Added model `CustomKeysConnectionProperties`
  - Added model `ManagedIdentityAuthTypeConnectionProperties`
  - Added enum `ManagedPERequirement`
  - Added enum `ManagedPEStatus`
  - Added model `NetworkInjections`
  - Added model `NoneAuthTypeConnectionProperties`
  - Added model `OAuth2AuthTypeConnectionProperties`
  - Added model `PATAuthTypeConnectionProperties`
  - Added model `Project`
  - Added model `ProjectListResult`
  - Added model `ProjectProperties`
  - Added model `ResourceBase`
  - Added model `SASAuthTypeConnectionProperties`
  - Added enum `ScenarioType`
  - Added model `ServicePrincipalAuthTypeConnectionProperties`
  - Added model `UsernamePasswordAuthTypeConnectionProperties`
  - Added operation group `AccountCapabilityHostsOperations`
  - Added operation group `AccountConnectionOperations`
  - Added operation group `ProjectCapabilityHostsOperations`
  - Added operation group `ProjectConnectionOperations`
  - Added operation group `ProjectsOperations`

## 13.6.0 (2024-12-19)

### Features Added

  - Client `CognitiveServicesManagementClient` added method `calculate_model_capacity`
  - Client `CognitiveServicesManagementClient` added operation group `location_based_model_capacities`
  - Client `CognitiveServicesManagementClient` added operation group `model_capacities`
  - Client `CognitiveServicesManagementClient` added operation group `encryption_scopes`
  - Client `CognitiveServicesManagementClient` added operation group `rai_policies`
  - Client `CognitiveServicesManagementClient` added operation group `rai_blocklists`
  - Client `CognitiveServicesManagementClient` added operation group `rai_blocklist_items`
  - Client `CognitiveServicesManagementClient` added operation group `rai_content_filters`
  - Client `CognitiveServicesManagementClient` added operation group `network_security_perimeter_configurations`
  - Client `CognitiveServicesManagementClient` added operation group `defender_for_ai_settings`
  - Model `AccountModel` added property `publisher`
  - Model `AccountModel` added property `source_account`
  - Model `AccountProperties` added property `aml_workspace`
  - Model `AccountProperties` added property `rai_monitor_config`
  - Model `CapacityConfig` added property `allowed_values`
  - Model `CommitmentPlanAccountAssociation` added property `tags`
  - Model `Deployment` added property `tags`
  - Model `DeploymentModel` added property `publisher`
  - Model `DeploymentModel` added property `source_account`
  - Model `DeploymentProperties` added property `dynamic_throttling_enabled`
  - Model `DeploymentProperties` added property `current_capacity`
  - Model `DeploymentProperties` added property `capacity_settings`
  - Model `DeploymentProperties` added property `parent_deployment_name`
  - Model `Model` added property `description`
  - Enum `ModelLifecycleStatus` added member `DEPRECATED`
  - Enum `ModelLifecycleStatus` added member `DEPRECATING`
  - Enum `ModelLifecycleStatus` added member `STABLE`
  - Model `ModelSku` added property `cost`
  - Model `NetworkRuleSet` added property `bypass`
  - Added model `BillingMeterInfo`
  - Added enum `ByPassSelection`
  - Added model `CalculateModelCapacityParameter`
  - Added model `CalculateModelCapacityResult`
  - Added model `CalculateModelCapacityResultEstimatedCapacity`
  - Added enum `ContentLevel`
  - Added model `CustomBlocklistConfig`
  - Added model `DefenderForAISetting`
  - Added model `DefenderForAISettingResult`
  - Added enum `DefenderForAISettingState`
  - Added model `DeploymentCapacitySettings`
  - Added model `DeploymentSkuListResult`
  - Added model `EncryptionScope`
  - Added model `EncryptionScopeListResult`
  - Added model `EncryptionScopeProperties`
  - Added enum `EncryptionScopeProvisioningState`
  - Added enum `EncryptionScopeState`
  - Added model `ModelCapacityCalculatorWorkload`
  - Added model `ModelCapacityCalculatorWorkloadRequestParam`
  - Added model `ModelCapacityListResult`
  - Added model `ModelCapacityListResultValueItem`
  - Added model `ModelSkuCapacityProperties`
  - Added model `NetworkSecurityPerimeter`
  - Added model `NetworkSecurityPerimeterAccessRule`
  - Added model `NetworkSecurityPerimeterAccessRuleProperties`
  - Added model `NetworkSecurityPerimeterAccessRulePropertiesSubscriptionsItem`
  - Added model `NetworkSecurityPerimeterConfiguration`
  - Added model `NetworkSecurityPerimeterConfigurationAssociationInfo`
  - Added model `NetworkSecurityPerimeterConfigurationList`
  - Added model `NetworkSecurityPerimeterConfigurationProperties`
  - Added model `NetworkSecurityPerimeterProfileInfo`
  - Added enum `NspAccessRuleDirection`
  - Added model `ProvisioningIssue`
  - Added model `ProvisioningIssueProperties`
  - Added model `RaiBlockListItemsResult`
  - Added model `RaiBlockListResult`
  - Added model `RaiBlocklist`
  - Added model `RaiBlocklistConfig`
  - Added model `RaiBlocklistItem`
  - Added model `RaiBlocklistItemBulkRequest`
  - Added model `RaiBlocklistItemProperties`
  - Added model `RaiBlocklistProperties`
  - Added model `RaiContentFilter`
  - Added model `RaiContentFilterListResult`
  - Added model `RaiContentFilterProperties`
  - Added model `RaiMonitorConfig`
  - Added model `RaiPolicy`
  - Added model `RaiPolicyContentFilter`
  - Added enum `RaiPolicyContentSource`
  - Added model `RaiPolicyListResult`
  - Added enum `RaiPolicyMode`
  - Added model `RaiPolicyProperties`
  - Added enum `RaiPolicyType`
  - Added model `SkuResource`
  - Added model `UserOwnedAmlWorkspace`
  - Operation group `CognitiveServicesManagementClientOperationsMixin` added method `calculate_model_capacity`
  - Operation group `DeploymentsOperations` added method `begin_update`
  - Operation group `DeploymentsOperations` added method `list_skus`
  - Added operation group `DefenderForAISettingsOperations`
  - Added operation group `EncryptionScopesOperations`
  - Added operation group `LocationBasedModelCapacitiesOperations`
  - Added operation group `ModelCapacitiesOperations`
  - Added operation group `NetworkSecurityPerimeterConfigurationsOperations`
  - Added operation group `RaiBlocklistItemsOperations`
  - Added operation group `RaiBlocklistsOperations`
  - Added operation group `RaiContentFiltersOperations`
  - Added operation group `RaiPoliciesOperations`

## 13.5.0 (2023-07-21)

### Features Added

  - Added operation group ModelsOperations
  - Added operation group UsagesOperations
  - Model AccountModel has a new parameter is_default_version
  - Model AccountModel has a new parameter skus
  - Model AccountModel has a new parameter source
  - Model AccountProperties has a new parameter abuse_penalty
  - Model CommitmentPlanProperties has a new parameter provisioning_issues
  - Model Deployment has a new parameter sku
  - Model DeploymentModel has a new parameter source
  - Model DeploymentProperties has a new parameter rate_limits
  - Model DeploymentProperties has a new parameter version_upgrade_option
  - Model UsageListResult has a new parameter next_link

## 13.4.0 (2023-02-15)

### Features Added

  - Added operation CommitmentPlansOperations.begin_create_or_update_association
  - Added operation CommitmentPlansOperations.begin_create_or_update_plan
  - Added operation CommitmentPlansOperations.begin_delete_association
  - Added operation CommitmentPlansOperations.begin_delete_plan
  - Added operation CommitmentPlansOperations.begin_update_plan
  - Added operation CommitmentPlansOperations.get_association
  - Added operation CommitmentPlansOperations.get_plan
  - Added operation CommitmentPlansOperations.list_associations
  - Added operation CommitmentPlansOperations.list_plans_by_resource_group
  - Added operation CommitmentPlansOperations.list_plans_by_subscription
  - Model AccountModel has a new parameter finetune_capabilities
  - Model AccountModel has a new parameter lifecycle_status
  - Model AccountProperties has a new parameter commitment_plan_associations
  - Model AccountProperties has a new parameter locations
  - Model CommitmentPlan has a new parameter kind
  - Model CommitmentPlan has a new parameter location
  - Model CommitmentPlan has a new parameter sku
  - Model CommitmentPlan has a new parameter tags
  - Model CommitmentPlanProperties has a new parameter commitment_plan_guid
  - Model CommitmentPlanProperties has a new parameter provisioning_state

## 13.4.0b1 (2022-12-29)

### Features Added

  - Added operation CommitmentPlansOperations.begin_create_or_update_association
  - Added operation CommitmentPlansOperations.begin_create_or_update_plan
  - Added operation CommitmentPlansOperations.begin_delete_association
  - Added operation CommitmentPlansOperations.begin_delete_plan
  - Added operation CommitmentPlansOperations.begin_update_plan
  - Added operation CommitmentPlansOperations.get_association
  - Added operation CommitmentPlansOperations.get_plan
  - Added operation CommitmentPlansOperations.list_associations
  - Added operation CommitmentPlansOperations.list_plans_by_resource_group
  - Added operation CommitmentPlansOperations.list_plans_by_subscription
  - Model AccountModel has a new parameter finetune_capabilities
  - Model AccountModel has a new parameter lifecycle_status
  - Model AccountProperties has a new parameter commitment_plan_associations
  - Model AccountProperties has a new parameter locations
  - Model CommitmentPlan has a new parameter kind
  - Model CommitmentPlan has a new parameter location
  - Model CommitmentPlan has a new parameter sku
  - Model CommitmentPlan has a new parameter tags
  - Model CommitmentPlanProperties has a new parameter commitment_plan_guid
  - Model CommitmentPlanProperties has a new parameter provisioning_state

## 13.3.0 (2022-10-24)

### Features Added

  - Model AccountModel has a new parameter call_rate_limit
  - Model DeploymentModel has a new parameter call_rate_limit
  - Model DeploymentProperties has a new parameter call_rate_limit
  - Model DeploymentProperties has a new parameter capabilities
  - Model DeploymentProperties has a new parameter rai_policy_name

## 13.2.0 (2022-06-08)

**Features**

  - `scale_type` of Model DeploymentScaleType has a new Enum type STANDARD

## 13.1.0 (2022-03-25)

**Features**

  - Added operation AccountsOperations.list_models
  - Model AccountProperties has a new parameter deletion_date
  - Model AccountProperties has a new parameter dynamic_throttling_enabled
  - Model AccountProperties has a new parameter scheduled_purge_date
  - Model DeploymentScaleSettings has a new parameter active_capacity

## 13.0.0 (2021-11-15)

**Features**

  - Model DomainAvailability has a new parameter kind
  - Model CheckDomainAvailabilityParameter has a new parameter kind
  - Added operation group CommitmentPlansOperations
  - Added operation group CommitmentTiersOperations
  - Added operation group DeploymentsOperations

**Breaking changes**

  - Operation CognitiveServicesManagementClientOperationsMixin.check_domain_availability has a new signature

## 12.0.0 (2021-06-03)

**Features**

  - Model UserOwnedStorage has a new parameter identity_client_id
  - Model Sku has a new parameter family
  - Model Sku has a new parameter capacity
  - Model Sku has a new parameter size
  - Model PrivateEndpointConnection has a new parameter location
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model PrivateEndpointConnection has a new parameter etag
  - Model PrivateEndpointConnectionProperties has a new parameter provisioning_state
  - Model KeyVaultProperties has a new parameter identity_client_id
  - Model PrivateLinkServiceConnectionState has a new parameter actions_required
  - Added operation PrivateEndpointConnectionsOperations.begin_create_or_update
  - Added operation PrivateEndpointConnectionsOperations.begin_delete
  - Added operation AccountsOperations.list_usages
  - Added operation AccountsOperations.begin_delete
  - Added operation AccountsOperations.get
  - Added operation AccountsOperations.begin_create
  - Added operation AccountsOperations.begin_update
  - Added operation group DeletedAccountsOperations

**Breaking changes**

  - Model PrivateLinkServiceConnectionState no longer has parameter action_required
  - Removed operation PrivateEndpointConnectionsOperations.create_or_update
  - Removed operation PrivateEndpointConnectionsOperations.delete
  - Removed operation AccountsOperations.delete
  - Removed operation AccountsOperations.create
  - Removed operation AccountsOperations.get_usages
  - Removed operation AccountsOperations.update
  - Removed operation AccountsOperations.get_properties

## 11.0.0 (2020-12-22)

**Features**

  - Model CognitiveServicesAccountProperties has a new parameter date_created

## 11.0.0b1 (2020-11-03)

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

## 6.3.0 (2020-10-09)

**Features**

  - Model CognitiveServicesAccountApiProperties has a new parameter website_name
  - Model CognitiveServicesAccountApiProperties has a new parameter super_user
  - Model CognitiveServicesAccountApiProperties has a new parameter aad_client_id
  - Model CognitiveServicesAccountApiProperties has a new parameter aad_tenant_id
  - Added operation PrivateEndpointConnectionsOperations.list

## 6.2.0 (2020-05-29)

**Features**

  - Model CognitiveServicesAccountProperties has a new parameter public_network_access
  - Model CognitiveServicesAccountProperties has a new parameter private_endpoint_connections
  - Model CognitiveServicesAccountProperties has a new parameter capabilities
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

## 6.1.0 (2020-03-25)

**Features**

  - Model CognitiveServicesAccount has a new parameter identity
  - Model CognitiveServicesAccountProperties has a new parameter user_owned_storage
  - Model CognitiveServicesAccountProperties has a new parameter encryption

## 6.0.0 (2020-02-07)

**Features**

- Model CognitiveServicesAccount has a new parameter properties
- Added operation CognitiveServicesManagementClientOperationsMixin.check_sku_availability

**Breaking changes**

- Operation AccountsOperations.create has a new signature
- Model CognitiveServicesAccount no longer has parameter network_acls
- Model CognitiveServicesAccount no longer has parameter provisioning_state
- Model CognitiveServicesAccount no longer has parameter internal_id
- Model CognitiveServicesAccount no longer has parameter custom_sub_domain_name
- Model CognitiveServicesAccount no longer has parameter endpoint
- Model NetworkRuleSet no longer has parameter bypass
- Operation AccountsOperations.update has a new signature
- Removed operation group CheckSkuAvailabilityOperations

## 5.0.0 (2019-06-21)

**Features**

  - Model CognitiveServicesAccount has a new parameter network_acls
  - Add operation check_domain_availability

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes for some imports. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - CognitiveServicesManagementClient cannot be imported from
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.cognitive_services_management_client`
    anymore (import from `azure.mgmt.cognitiveservices.v20xx_yy_zz`
    works like before)
  - CognitiveServicesManagementClientConfiguration import has been moved
    from
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.cognitive_services_management_client`
    to `azure.mgmt.cognitiveservices.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.cognitiveservices.v20xx_yy_zz.models`
    works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.operations.my_class_operations`
    (import from
    `azure.mgmt.cognitiveservices.v20xx_yy_zz.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 4.0.0 (2019-05-01)

**Features**

  - Model CognitiveServicesAccount has a new parameter
    custom_sub_domain_name
  - Model CognitiveServicesAccountUpdateParameters has a new parameter
    properties
  - Operation AccountsOperations.update now takes optional properties

**Breaking changes**

  - Remove limited enum Kind and SkuName. Replace all usage by a simple
    string (e.g. "Bing.SpellCheck.v7")

## 3.0.0 (2018-05-21)

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

  - Add "resource_skus" operation group
  - Update SKU list
  - Add "accounts.get_usages" operation
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 2.0.0 (2017-10-26)

**Breaking changes**

  - remove "location" as a constructor parameter
  - sku_name in "check_sku_availability" result is now a str (from an
    enum)
  - merge "cognitive_services_accounts" into "accounts" operation
    group
  - "key_name" is now required to regenerate keys
  - "location/skus/kind/type" are now required for "list" available skus

## 1.0.0 (2017-05-01)

  - No changes, this is the 0.30.0 approved as stable.

## 0.30.0 (2017-05-01)

  - Initial Release (ApiVersion 2017-04-18)
  - This wheel package is now built with the azure wheel extension
