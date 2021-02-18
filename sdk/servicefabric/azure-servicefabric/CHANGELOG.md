# Release History

## 7.2.0.46 (2020-10-29)

**Features**

  - Added `update_partition_load` method to update the loads of provided partitions.

## 7.1.0.45 (2020-05-14)

**Bugfix**

  - Fix ContainerCodePackageProperties entrypoint to entry_point

## 7.0.0.0 (2019-12-13)

This is re-release of 6.6.0.0 to match the actual API version used
internally

## 6.6.0.0 (2019-12-07)

**Features**

  - Model StartClusterUpgradeDescription has a new parameter
    instance_close_delay_duration_in_seconds
  - Model Setting has a new parameter type
  - Model ApplicationUpgradeDescription has a new parameter
    instance_close_delay_duration_in_seconds
  - Model HealthEvent has a new parameter health_report_id
  - Model HealthInformation has a new parameter health_report_id
  - Model StatelessServiceDescription has a new parameter flags
  - Model StatelessServiceDescription has a new parameter
    min_instance_count
  - Model StatelessServiceDescription has a new parameter
    min_instance_percentage
  - Model StatelessServiceDescription has a new parameter
    instance_close_delay_duration_seconds
  - Model StatefulServiceDescription has a new parameter
    service_placement_time_limit_seconds
  - Model ImageRegistryCredential has a new parameter password_type
  - Model ContainerCodePackageProperties has a new parameter
    liveness_probe
  - Model ContainerCodePackageProperties has a new parameter
    readiness_probe
  - Model ServiceResourceDescription has a new parameter
    execution_policy
  - Model ServiceResourceDescription has a new parameter dns_name
  - Model StatefulServiceUpdateDescription has a new parameter
    service_placement_time_limit_seconds
  - Model EnvironmentVariable has a new parameter type
  - Model StatelessServicePartitionInfo has a new parameter
    min_instance_percentage
  - Model StatelessServicePartitionInfo has a new parameter
    min_instance_count
  - Model RollingUpgradeUpdateDescription has a new parameter
    instance_close_delay_duration_in_seconds
  - Model ServiceProperties has a new parameter execution_policy
  - Model ServiceProperties has a new parameter dns_name
  - Model StatelessServiceUpdateDescription has a new parameter
    min_instance_percentage
  - Model StatelessServiceUpdateDescription has a new parameter
    min_instance_count
  - Model StatelessServiceUpdateDescription has a new parameter
    instance_close_delay_duration_seconds
  - Added operation MeshApplicationOperations.get_upgrade_progress
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.remove_configuration_overrides
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.get_image_store_info
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.get_configuration_overrides
  - Added operation
    ServiceFabricClientAPIsOperationsMixin.add_configuration_parameter_overrides

## 6.5.0.0 (2019-06-17)

**Features**

  - Model ApplicationDescription has a new parameter
    managed_application_identity
  - Model ApplicationUpgradeDescription has a new parameter sort_order
  - Model NodeLoadMetricInformation has a new parameter
    planned_node_load_removal
  - Model NodeLoadMetricInformation has a new parameter
    current_node_load
  - Model NodeLoadMetricInformation has a new parameter
    buffered_node_capacity_remaining
  - Model NodeLoadMetricInformation has a new parameter
    node_capacity_remaining
  - Model StartClusterUpgradeDescription has a new parameter sort_order
  - Model ApplicationResourceDescription has a new parameter identity
  - Model ServiceResourceDescription has a new parameter identity_refs
  - Model ClusterUpgradeDescriptionObject has a new parameter
    sort_order
  - Model ServiceProperties has a new parameter identity_refs

**Breaking changes**

  - Model ChaosStartedEvent no longer has parameter
    wait_time_between_fautls_in_seconds
  - Model ChaosStartedEvent has a new required parameter
    wait_time_between_faults_in_seconds

## 6.4.0.0 (2018-12-07)

**Bugfixes**

  - Numerous improvements to descriptions and help texts

**Features**

  - Add command to get cluster load
  - Add command to get cluster version
  - Add mesh gateway support
  - Add mesh support
  - Add command for rolling back compose deployment upgrades
  - Various new parameters added.

## 6.3.0.0 (2018-07-27)

**Bugfixes**

  - Numerous improvements to descriptions and help texts

**Features**

  - Add application health policies parameter for config upgrade
  - Query to get nodes now supports specification to limit number of
    returned items

## 6.2.0.0 (2018-05-10)

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

**Bugfixes**

  - Numerous fixes to descriptions and help text of entities
  - Compatibility of the sdist with wheel 0.31.0

**Features**

  - Add support for invoking container APIs
  - Add option to fetch container logs from exited containers
  - Query to get chaos events now supports specification to limit number
    of returned items
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 6.1.2.9 (2018-02-05)

**Bugfixes**

  - Numerous fixes to descriptions and help text of entities

**Features**

  - Chaos service now supports a target filter
  - Application types can now be provisioned and created in external
    stores
  - Added Orchestration Service internal support APIs
  - Added container deployment management APIs

## 6.1.1.9 (2018-01-23)

This version was broken and has been removed from PyPI.

## 6.0.2 (2017-10-26)

**Bugfixes**

  - remove application_type_version in
    get_application_type_info_list_by_name
  - fix application_type_definition_kind_filter default value from
    65535 to 0

**Features**

  - add create_name, get_name_exists_info, delete_name,
    get_sub_name_info_list, get_property_info_list,
    put_property, get_property_info, delete_property,
    submit_property_batch

## 6.0.1 (2017-09-28)

**Bug fix**

  - Fix some unexpected exceptions

## 6.0 (2017-09-22)

  - Stable 6.0 api

## 6.0.0rc1 (2017-09-16)

  - Release candidate for Service Fabric 6.0 runtime

## 5.6.130 (2017-05-04)

  - Initial Release
