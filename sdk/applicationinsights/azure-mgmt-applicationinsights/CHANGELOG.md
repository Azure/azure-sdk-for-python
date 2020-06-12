# Release History

## 0.3.1 (2020-04-20)

** Fixes **

  - Removed an unreferenced client definition.

## 0.3.0 (2020-04-08)

**Features**

  - Model ApplicationInsightsComponentProactiveDetectionConfiguration has a new parameter type
  - Model ApplicationInsightsComponentProactiveDetectionConfiguration has a new parameter location
  - Model ApplicationInsightsComponentProactiveDetectionConfiguration has a new parameter id
  - Model ApplicationInsightsComponentProactiveDetectionConfiguration has a new parameter name1
  - Model ApplicationInsightsComponent has a new parameter connection_string
  - Model ApplicationInsightsComponent has a new parameter immediate_purge_data_on30_days
  - Model ApplicationInsightsComponent has a new parameter retention_in_days
  - Model ApplicationInsightsComponent has a new parameter disable_ip_masking
  - Model ApplicationInsightsComponent has a new parameter public_network_access_for_query
  - Model ApplicationInsightsComponent has a new parameter private_link_scoped_resources
  - Model ApplicationInsightsComponent has a new parameter public_network_access_for_ingestion
  - Added operation group ComponentCurrentPricingPlanOperations
  - Added operation group ComponentLinkedStorageAccountsOperations
  - Added operation group EASubscriptionListMigrationDateOperations
  - Added operation group EASubscriptionMigrateToNewPricingModelOperations
  - Added operation group EASubscriptionRollbackToLegacyPricingModelOperations
  - Added operation group QueryPacksOperations
  - Added operation group WorkbookTemplatesOperations
  - Added operation group QueriesOperations

**Breaking changes**

  - Parameter location of model Workbook is now required
  - Operation WorkbooksOperations.create_or_update has a new signature
  - Operation WorkbooksOperations.list_by_resource_group has a new signature
  - Operation WorkbooksOperations.update has a new signature
  - Model Workbook no longer has parameter workbook_name
  - Model Workbook no longer has parameter source_resource_id
  - Model Workbook no longer has parameter shared_type_kind
  - Model Workbook no longer has parameter workbook_id
  - Model Workbook has a new required parameter display_name
  - Model ApplicationInsightsComponent has a new required parameter workspace_resource_id

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - ApplicationInsightsManagementClient cannot be imported from
    `azure.mgmt.applicationinsights.application_insights_management_client` anymore (import from
    `azure.mgmt.applicationinsights` works like before)
  - ApplicationInsightsManagementClientConfiguration import has been moved from
    `azure.mgmt.applicationinsights.application_insights_management_client` 
    to `azure.mgmt.applicationinsights`  
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.applicationinsights.models.my_class` (import from
    `azure.mgmt.applicationinsights.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.applicationinsights.operations.my_class_operations` (import from
    `azure.mgmt.applicationinsights.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.2.0 (2019-04-10)

**Features**

  - Added operation WebTestsOperations.list_by_component
  - Added operation ComponentsOperations.get_purge_status
  - Added operation ComponentsOperations.purge
  - Added operation group FavoritesOperations
  - Added operation group ComponentFeatureCapabilitiesOperations
  - Added operation group WebTestLocationsOperations
  - Added operation group ComponentAvailableFeaturesOperations
  - Added operation group ProactiveDetectionConfigurationsOperations
  - Added operation group AnnotationsOperations
  - Added operation group WorkItemConfigurationsOperations
  - Added operation group WorkbooksOperations
  - Added operation group AnalyticsItemsOperations

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

## 0.1.1 (2018-02-12)

  - Add proactive_detection_configurations

## 0.1.0 (2018-01-17)

  - Initial Release
