# Release History

## 10.2.0b7 (2023-04-18)

### Features Added

  - Added operation group BackupAndExportOperations

### Breaking Changes

  - Renamed `SYSTEM_ASSIGNED` to `SYSTEM_MANAGED` in enum `ArmServerKeyType`
  - Removed `SECONDARY`, `WAL_REPLICA`, `SYNC_REPLICA`, `GEO_SYNC_REPLICA` from enum `ReplicationRole`

## 10.2.0b6 (2023-01-04)

### Features Added

  - Model AuthConfig has a new parameter active_directory_auth
  - Model AuthConfig has a new parameter password_auth

### Breaking Changes

  - Model AuthConfig no longer has parameter active_directory_auth_enabled
  - Model AuthConfig no longer has parameter password_auth_enabled

## 10.2.0b5 (2022-11-14)

### Features Added

  - Model ServerForUpdate has a new parameter replication_role

## 10.2.0b4 (2022-11-02)

### Features Added

  - Added operation group AdministratorsOperations
  - Added operation group CheckNameAvailabilityWithLocationOperations
  - Model CapabilityProperties has a new parameter fast_provisioning_supported
  - Model CapabilityProperties has a new parameter supported_fast_provisioning_editions
  - Model ErrorResponse has a new parameter error
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model Server has a new parameter auth_config
  - Model Server has a new parameter data_encryption
  - Model Server has a new parameter identity
  - Model Server has a new parameter replica_capacity
  - Model Server has a new parameter replication_role
  - Model ServerForUpdate has a new parameter auth_config
  - Model ServerForUpdate has a new parameter data_encryption
  - Model ServerForUpdate has a new parameter identity
  - Model ServerForUpdate has a new parameter version
  - Model ServerVersionCapability has a new parameter supported_versions_to_upgrade
  - Model StorageMBCapability has a new parameter supported_upgradable_tier_list
  - Model TrackedResource has a new parameter system_data
  - Model UserAssignedIdentity has a new parameter user_assigned_identities

### Breaking Changes

  - Model DataEncryption no longer has parameter geo_backup_key_uri
  - Model DataEncryption no longer has parameter geo_backup_user_assigned_identity_id
  - Model ErrorResponse no longer has parameter additional_info
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter message
  - Model ErrorResponse no longer has parameter target
  - Model ServerForUpdate no longer has parameter location
  - Model UserAssignedIdentity has a new required parameter type
  - Model UserAssignedIdentity no longer has parameter client_id
  - Model UserAssignedIdentity no longer has parameter principal_id

## 10.2.0b3 (2022-08-09)

**Features**

  - Added operation group AzureADAdministratorsOperations
  - Added operation group CheckNameAvailabilityWithoutLocationOperations

## 10.2.0b2 (2022-08-01)

**Features**

  - Model CapabilityProperties has a new parameter supported_ha_mode
  - Model Configuration has a new parameter documentation_link
  - Model Configuration has a new parameter is_config_pending_restart
  - Model Configuration has a new parameter is_dynamic_config
  - Model Configuration has a new parameter is_read_only
  - Model Configuration has a new parameter unit
  - Model NameAvailability has a new parameter reason
  - Model VirtualNetworkSubnetUsageResult has a new parameter location
  - Model VirtualNetworkSubnetUsageResult has a new parameter subscription_id

**Breaking changes**

  - Model Server no longer has parameter tags_properties_tags
  - Removed operation BackupsOperations.put

## 10.2.0b1 (2022-07-13)

**Features**

  - Added operation BackupsOperations.put
  - Model ConfigurationListForBatchUpdate has a new parameter reset_all_to_default

## 10.1.0 (2022-03-07)

**Features**

  - Added model DataEncryption
  - Added model DataEncryptionType
  - Added model Identity
  - Added model UserAssignedIdentity

## 10.0.0 (2021-10-08)

**Breaking changes**

  - Model Server no longer has parameter identity

## 9.1.0 (2021-09-02)

**Features**

  - Upgrade api-version to `2021-05-01`

## 9.1.0b1 (2021-07-19)

**Features**

  - Added operation group BackupsOperations

## 9.0.0 (2021-07-01)

**Features**

  - Model ServerVersionCapability has a new parameter status
  - Model Server has a new parameter network
  - Model Server has a new parameter backup
  - Model Server has a new parameter storage
  - Model Server has a new parameter system_data
  - Model Server has a new parameter high_availability
  - Model Server has a new parameter minor_version
  - Model Server has a new parameter source_server_resource_id
  - Model Database has a new parameter system_data
  - Model StorageProfile has a new parameter storage_autogrow
  - Model StorageProfile has a new parameter geo_redundant_backup
  - Model VcoreCapability has a new parameter status
  - Model Configuration has a new parameter system_data
  - Model StorageEditionCapability has a new parameter status
  - Model FirewallRule has a new parameter system_data
  - Model ServerForUpdate has a new parameter create_mode
  - Model ServerForUpdate has a new parameter backup
  - Model ServerForUpdate has a new parameter high_availability
  - Model ServerForUpdate has a new parameter storage
  - Model StorageMBCapability has a new parameter status
  - Added operation GetPrivateDnsZoneSuffixOperations.execute
  - Added operation ConfigurationsOperations.begin_put

**Breaking changes**

  - Operation ServersOperations.begin_restart has a new signature
  - Model Server no longer has parameter byok_enforcement
  - Model Server no longer has parameter public_network_access
  - Model Server no longer has parameter display_name
  - Model Server no longer has parameter ha_state
  - Model Server no longer has parameter private_dns_zone_arguments
  - Model Server no longer has parameter source_server_name
  - Model Server no longer has parameter storage_profile
  - Model Server no longer has parameter source_resource_group_name
  - Model Server no longer has parameter delegated_subnet_arguments
  - Model Server no longer has parameter source_subscription_id
  - Model Server no longer has parameter ha_enabled
  - Model Server no longer has parameter standby_availability_zone
  - Model ServerForUpdate no longer has parameter storage_profile
  - Model ServerForUpdate no longer has parameter ha_enabled
  - Model CapabilityProperties has a new signature

## 8.1.0 (2021-06-08)

 - New models and operations for mariadb

## 8.1.0b4 (2021-04-29)

**Features**

  - Added operation ServerSecurityAlertPoliciesOperations.list_by_server
  - Added operation ServerKeysOperations.list

**Breaking changes**

  - Removed operation ServerKeysOperations.list_by_server

## 8.1.0b3 (2021-04-27)

**Features**

  - Model Server has a new parameter private_dns_zone_arguments
  - Added operation ServerKeysOperations.list_by_server
  - Added operation group GetPrivateDnsZoneSuffixOperations

**Breaking changes**

  - Removed operation ServerSecurityAlertPoliciesOperations.list_by_server
  - Removed operation ServerKeysOperations.list

## 8.1.0b2 (2021-03-19)

**Features**

  - Model Server has a new parameter source_subscription_id
  - Model Server has a new parameter source_resource_group_name

## 8.1.0b1 (2021-03-17)

**Features**

  - Added operation ServerSecurityAlertPoliciesOperations.list_by_server

## 8.0.0 (2020-12-28)

- GA release

## 8.0.0b1 (2020-11-05)

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

## 3.1.0rc1 (2020-09-25)

**Features**

  - Model Operation has a new parameter is_data_action
  - Model OperationListResult has a new parameter next_link

## 3.0.0rc1 (2020-09-15)

**Features**

  - Model NameAvailability has a new parameter name
  - Model NameAvailability has a new parameter type
  - Added operation ServersOperations.start
  - Added operation ServersOperations.stop
  - Added operation ConfigurationsOperations.update
  - Added operation group VirtualNetworkSubnetUsageOperations
  - Added operation group LocationBasedCapabilitiesOperations
  - Added operation group CheckVirtualNetworkSubnetUsageOperations

**Breaking changes**

  - Model NameAvailability no longer has parameter reason
  - Model StorageProfile no longer has parameter geo_redundant_backup
  - Model StorageProfile no longer has parameter storage_autogrow
  - Model Server has a new signature
  - Model Sku has a new signature
  - Removed operation ConfigurationsOperations.create_or_update

## 2.2.0 (2020-03-25)

**Features**

  - Model ServerUpdateParameters has a new parameter public_network_access
  - Model ServerPropertiesForCreate has a new parameter public_network_access
  - Model Server has a new parameter public_network_access
  - Model Server has a new parameter private_endpoint_connections
  - Model ServerPropertiesForRestore has a new parameter public_network_access
  - Model ServerPropertiesForReplica has a new parameter public_network_access
  - Model ServerPropertiesForDefaultCreate has a new parameter public_network_access
  - Model ServerPropertiesForGeoRestore has a new parameter public_network_access

## 2.1.0 (2020-03-23)

**Features**

  - Model ServerPropertiesForReplica has a new parameter infrastructure_encryption
  - Model ServerPropertiesForReplica has a new parameter minimal_tls_version
  - Model ServerPropertiesForReplica has a new parameter public_network_access
  - Model ServerForCreate has a new parameter identity
  - Model ServerUpdateParameters has a new parameter minimal_tls_version
  - Model ServerUpdateParameters has a new parameter identity
  - Model ServerUpdateParameters has a new parameter public_network_access
  - Model Server has a new parameter byok_enforcement
  - Model Server has a new parameter minimal_tls_version
  - Model Server has a new parameter public_network_access
  - Model Server has a new parameter infrastructure_encryption
  - Model Server has a new parameter identity
  - Model Server has a new parameter private_endpoint_connections
  - Model ServerPropertiesForDefaultCreate has a new parameter infrastructure_encryption
  - Model ServerPropertiesForDefaultCreate has a new parameter minimal_tls_version
  - Model ServerPropertiesForDefaultCreate has a new parameter public_network_access
  - Model ServerPropertiesForGeoRestore has a new parameter infrastructure_encryption
  - Model ServerPropertiesForGeoRestore has a new parameter minimal_tls_version
  - Model ServerPropertiesForGeoRestore has a new parameter public_network_access
  - Model ServerPropertiesForCreate has a new parameter infrastructure_encryption
  - Model ServerPropertiesForCreate has a new parameter minimal_tls_version
  - Model ServerPropertiesForCreate has a new parameter public_network_access
  - Model ServerPropertiesForRestore has a new parameter infrastructure_encryption
  - Model ServerPropertiesForRestore has a new parameter minimal_tls_version
  - Model ServerPropertiesForRestore has a new parameter public_network_access
  - Added operation group ServerKeysOperations
  - Added operation group ServerAdministratorsOperations

## 2.0.0 (2020-02-21)

**Features**

  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group AdvisorsOperations
  - Added operation group MySQLManagementClientOperationsMixin
  - Added operation group QueryTextsOperations
  - Added operation group RecommendedActionsOperations
  - Added operation group MariaDBManagementClientOperationsMixin
  - Added operation group LocationBasedRecommendedActionSessionsOperationStatusOperations
  - Added operation group LocationBasedRecommendedActionSessionsResultOperations
  - Added operation group WaitStatisticsOperations
  - Added operation group TopQueryStatisticsOperations

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - MariaDBManagementClient cannot be imported from
    `azure.mgmt.rdbms.mariadb.maria_db_management_client` anymore (import from
    `azure.mgmt.rdbms.mariadb` works like before)
  - KustoManagementClientConfiguration import has been moved from
    `azure.mgmt.rdbms.mariadb.maria_db_management_client` to
    `azure.mgmt.rdbms.mariadb`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.rdbms.mariadb.models.my_class` (import from
    `azure.mgmt.rdbms.mariadb.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.rdbms.mariadb.operations.my_class_operations` (import from
    `azure.mgmt.rdbms.mariadb.operations` works like before)
  - MySQLManagementClient cannot be imported from
    `azure.mgmt.rdbms.mysql.my_sql_management_client` anymore (import from
    `azure.mgmt.rdbms.mysql` works like before)
  - MySQLManagementClientConfiguration import has been moved from
    `azure.mgmt.rdbms.mysql.my_sql_management_client` to
    `azure.mgmt.rdbms.mysql`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.rdbms.mysql.models.my_class` (import from
    `azure.mgmt.rdbms.mysql.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.rdbms.mysql.operations.my_class_operations` (import from
    `azure.mgmt.rdbms.mysql.operations` works like before)
  - PostgreSQLManagementClient cannot be imported from
    `azure.mgmt.rdbms.postgresql.postgre_sql_management_client` anymore (import from
    `azure.mgmt.rdbms.postgresql` works like before)
  - PostgreSQLManagementClientConfiguration import has been moved from
    `azure.mgmt.rdbms.postgresql.my_sql_management_client` to
    `azure.mgmt.rdbms.postgresql`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.rdbms.postgresql.models.my_class` (import from
    `azure.mgmt.rdbms.postgresql.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.rdbms.postgresql.operations.my_class_operations` (import from
    `azure.mgmt.rdbms.postgresql.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 1.9.0 (2019-06-04)

**Features**

  - Add storage_autogrow in all DB
  - Support for PG11

## 1.8.0 (2019-04-08)

**Features**

  - Model ServerUpdateParameters has a new parameter replication_role

## 1.7.1 (2019-03-18)

**Features (PostgreSQL only)**

  - Model Server has a new parameter replica_capacity
  - Model Server has a new parameter replication_role
  - Model Server has a new parameter master_server_id
  - Added operation group ReplicasOperations

## 1.7.0 (2019-03-01)

**Features (MariaDB only)**

  - Model ServerUpdateParameters has a new parameter replication_role
  - Model Server has a new parameter master_server_id
  - Model Server has a new parameter replica_capacity
  - Model Server has a new parameter replication_role
  - Added operation ServersOperations.restart
  - Added operation group ReplicasOperations

## 1.6.0 (2019-02-26)

**Features**

  - Added operation ServersOperations.restart

## 1.5.0 (2018-10-30)

**Features**

  - Added operation group VirtualNetworkRulesOperations for MariaDB

## 1.4.1 (2018-10-16)

**Bugfix**

  - Fix sdist broken in 1.4.0. No code change.

## 1.4.0 (2018-10-11)

**Features**

  - Model Server has a new parameter replication_role
  - Model Server has a new parameter master_server_id
  - Model Server has a new parameter replica_capacity
  - Model ServerUpdateParameters has a new parameter replication_role
  - Added operation group ReplicasOperations

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 1.3.0 (2018-09-13)

**Features**

  - Added operation group ServerSecurityAlertPoliciesOperations (MySQL
    only)
  - Added support for PostregreSQL 10.x
  - Added support for MariaDB (public preview)

## 1.2.0 (2018-05-30)

**Features**

  - Added operation group VirtualNetworkRulesOperations
  - Added operation group ServerSecurityAlertPoliciesOperations
    (PostgreSQL only)
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 1.1.1 (2018-04-17)

**Bugfixes**

  - Fix some invalid models in Python 3
  - Compatibility of the sdist with wheel 0.31.0

## 1.1.0 (2018-03-29)

**Features**

  - Add Geo-Restore ability for MySQL and PostgreSQL

## 1.0.0 (2018-03-19)

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

**RDBMS breaking changes**

  - Some properties moved from object "PerformanceTierProperties" to
    "PerformanceTierServiceLevelObjectives "(One level down).

Api Version is now 2017-12-01

## 0.3.1 (2018-02-28)

  - Remove GeoRestore option that is not available yet.

## 0.3.0 (2018-02-26)

  - New pricing model release

## 0.2.0rc1 (2017-10-16)

  - VNET Rules API spec for Postgres and MySQL

## 0.1.0 (2017-05-08)

  - Initial Release
