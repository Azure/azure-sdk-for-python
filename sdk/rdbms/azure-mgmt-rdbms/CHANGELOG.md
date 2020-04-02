# Release History

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
