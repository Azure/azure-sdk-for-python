# Release History

## 0.11.0 (2019-12-07)

**Features**

  - Model GremlinDatabaseGetResults has a new parameter resource
  - Model ThroughputSettingsGetResults has a new parameter resource
  - Model SqlStoredProcedureGetResults has a new parameter resource
  - Model MongoDBDatabaseGetResults has a new parameter resource
  - Model SqlUserDefinedFunctionGetResults has a new parameter resource
  - Model TableGetResults has a new parameter resource
  - Model IndexingPolicy has a new parameter composite_indexes
  - Model IndexingPolicy has a new parameter spatial_indexes
  - Model CassandraKeyspaceGetResults has a new parameter resource
  - Model SqlDatabaseGetResults has a new parameter resource

**Breaking changes**

  - Model GremlinDatabaseGetResults no longer has parameter _etag
  - Model GremlinDatabaseGetResults no longer has parameter
    gremlin_database_get_results_id
  - Model GremlinDatabaseGetResults no longer has parameter _ts
  - Model GremlinDatabaseGetResults no longer has parameter _rid
  - Model ThroughputSettingsGetResults no longer has parameter
    minimum_throughput
  - Model ThroughputSettingsGetResults no longer has parameter
    offer_replace_pending
  - Model ThroughputSettingsGetResults no longer has parameter
    throughput
  - Model SqlStoredProcedureGetResults no longer has parameter _etag
  - Model SqlStoredProcedureGetResults no longer has parameter _ts
  - Model SqlStoredProcedureGetResults no longer has parameter _rid
  - Model SqlStoredProcedureGetResults no longer has parameter body
  - Model SqlStoredProcedureGetResults no longer has parameter
    sql_stored_procedure_get_results_id
  - Model MongoDBDatabaseGetResults no longer has parameter _etag
  - Model MongoDBDatabaseGetResults no longer has parameter
    mongo_db_database_get_results_id
  - Model MongoDBDatabaseGetResults no longer has parameter _ts
  - Model MongoDBDatabaseGetResults no longer has parameter _rid
  - Model SqlUserDefinedFunctionGetResults no longer has parameter
    _etag
  - Model SqlUserDefinedFunctionGetResults no longer has parameter
    sql_user_defined_function_get_results_id
  - Model SqlUserDefinedFunctionGetResults no longer has parameter _ts
  - Model SqlUserDefinedFunctionGetResults no longer has parameter _rid
  - Model SqlUserDefinedFunctionGetResults no longer has parameter body
  - Model TableGetResults no longer has parameter _etag
  - Model TableGetResults no longer has parameter
    table_get_results_id
  - Model TableGetResults no longer has parameter _ts
  - Model TableGetResults no longer has parameter _rid
  - Model CassandraKeyspaceGetResults no longer has parameter _etag
  - Model CassandraKeyspaceGetResults no longer has parameter
    cassandra_keyspace_get_results_id
  - Model CassandraKeyspaceGetResults no longer has parameter _ts
  - Model CassandraKeyspaceGetResults no longer has parameter _rid
  - Model SqlDatabaseGetResults no longer has parameter _colls
  - Model SqlDatabaseGetResults no longer has parameter _etag
  - Model SqlDatabaseGetResults no longer has parameter _users
  - Model SqlDatabaseGetResults no longer has parameter
    sql_database_get_results_id
  - Model SqlDatabaseGetResults no longer has parameter _rid
  - Model SqlDatabaseGetResults no longer has parameter _ts
  - Model GremlinGraphGetResults has a new signature
  - Model CassandraTableGetResults has a new signature
  - Model SqlTriggerGetResults has a new signature
  - Model SqlContainerGetResults has a new signature
  - Model MongoDBCollectionGetResults has a new signature

## 0.10.0 (2019-11-13)

**Features**

  - Model DatabaseAccountCreateUpdateParameters has a new parameter
    disable_key_based_metadata_write_access
  - Model ContainerPartitionKey has a new parameter version
  - Added operation DatabaseAccountsOperations.update
  - Added operation group SqlResourcesOperations
  - Added operation group MongoDBResourcesOperations
  - Added operation group TableResourcesOperations
  - Added operation group GremlinResourcesOperations
  - Added operation group CassandraResourcesOperations

**Breaking changes**

  - CosmosDB has been renamed to CosmosDBManagementClient
  - CosmosDBConfiguration was renamed to
    CosmodDBManagementClientConfiguration
  - Model MongoDBCollectionCreateUpdateParameters has a new signature
  - Model GremlinGraphCreateUpdateParameters has a new signature
  - Model CassandraKeyspaceCreateUpdateParameters has a new signature
  - Model GremlinDatabaseCreateUpdateParameters has a new signature
  - Model SqlContainerCreateUpdateParameters has a new signature
  - Model CassandraTableCreateUpdateParameters has a new signature
  - Model TableCreateUpdateParameters has a new signature
  - Model MongoDBDatabaseCreateUpdateParameters has a new signature
  - Model SqlDatabaseCreateUpdateParameters has a new signature
  - Removed operation
    DatabaseAccountsOperations.get_gremlin_graph_throughput
  - Removed operation
    DatabaseAccountsOperations.update_cassandra_keyspace_throughput
  - Removed operation DatabaseAccountsOperations.delete_sql_database
  - Removed operation
    DatabaseAccountsOperations.update_sql_database_throughput
  - Removed operation
    DatabaseAccountsOperations.update_mongo_db_database_throughput
  - Removed operation
    DatabaseAccountsOperations.delete_mongo_db_collection
  - Removed operation
    DatabaseAccountsOperations.list_mongo_db_databases
  - Removed operation
    DatabaseAccountsOperations.create_update_mongo_db_database
  - Removed operation
    DatabaseAccountsOperations.create_update_gremlin_graph
  - Removed operation
    DatabaseAccountsOperations.update_gremlin_database_throughput
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_collection
  - Removed operation
    DatabaseAccountsOperations.delete_gremlin_database
  - Removed operation
    DatabaseAccountsOperations.create_update_cassandra_keyspace
  - Removed operation DatabaseAccountsOperations.get_sql_database
  - Removed operation DatabaseAccountsOperations.get_table
  - Removed operation
    DatabaseAccountsOperations.update_table_throughput
  - Removed operation
    DatabaseAccountsOperations.create_update_mongo_db_collection
  - Removed operation DatabaseAccountsOperations.get_gremlin_database
  - Removed operation
    DatabaseAccountsOperations.create_update_sql_container
  - Removed operation
    DatabaseAccountsOperations.create_update_gremlin_database
  - Removed operation DatabaseAccountsOperations.get_table_throughput
  - Removed operation
    DatabaseAccountsOperations.delete_mongo_db_database
  - Removed operation
    DatabaseAccountsOperations.get_cassandra_table_throughput
  - Removed operation
    DatabaseAccountsOperations.update_sql_container_throughput
  - Removed operation DatabaseAccountsOperations.get_cassandra_table
  - Removed operation
    DatabaseAccountsOperations.list_gremlin_databases
  - Removed operation DatabaseAccountsOperations.list_gremlin_graphs
  - Removed operation
    DatabaseAccountsOperations.list_mongo_db_collections
  - Removed operation
    DatabaseAccountsOperations.create_update_cassandra_table
  - Removed operation
    DatabaseAccountsOperations.delete_cassandra_keyspace
  - Removed operation
    DatabaseAccountsOperations.update_cassandra_table_throughput
  - Removed operation
    DatabaseAccountsOperations.update_gremlin_graph_throughput
  - Removed operation DatabaseAccountsOperations.create_update_table
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_database_throughput
  - Removed operation DatabaseAccountsOperations.get_sql_container
  - Removed operation
    DatabaseAccountsOperations.get_gremlin_database_throughput
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_collection_throughput
  - Removed operation DatabaseAccountsOperations.list_cassandra_tables
  - Removed operation
    DatabaseAccountsOperations.get_sql_database_throughput
  - Removed operation DatabaseAccountsOperations.list_sql_databases
  - Removed operation DatabaseAccountsOperations.list_tables
  - Removed operation
    DatabaseAccountsOperations.get_cassandra_keyspace
  - Removed operation DatabaseAccountsOperations.get_gremlin_graph
  - Removed operation
    DatabaseAccountsOperations.get_mongo_db_database
  - Removed operation DatabaseAccountsOperations.delete_table
  - Removed operation
    DatabaseAccountsOperations.list_cassandra_keyspaces
  - Removed operation DatabaseAccountsOperations.list_sql_containers
  - Removed operation DatabaseAccountsOperations.delete_sql_container
  - Removed operation DatabaseAccountsOperations.delete_gremlin_graph
  - Removed operation
    DatabaseAccountsOperations.get_cassandra_keyspace_throughput
  - Removed operation
    DatabaseAccountsOperations.get_sql_container_throughput
  - Removed operation
    DatabaseAccountsOperations.delete_cassandra_table
  - Removed operation DatabaseAccountsOperations.patch
  - Removed operation
    DatabaseAccountsOperations.create_update_sql_database
  - Removed operation
    DatabaseAccountsOperations.update_mongo_db_collection_throughput

## 0.9.0 (2019-11-09)

**Features**

  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations

## 0.8.0 (2019-08-15)

**Features**

  - Model DatabaseAccount has a new parameter
    enable_cassandra_connector
  - Model DatabaseAccount has a new parameter connector_offer
  - Model DatabaseAccountCreateUpdateParameters has a new parameter
    enable_cassandra_connector
  - Model DatabaseAccountCreateUpdateParameters has a new parameter
    connector_offer

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - CosmosDB cannot be imported from `azure.mgmt.cosmosdb.cosmos_db`
    anymore (import from `azure.mgmt.cosmosdb` works like before)
  - CosmosDBConfiguration import has been moved from
    `azure.mgmt.cosmosdb.cosmos_db` to `azure.mgmt.cosmosdb`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.cosmosdb.models.my_class` (import from
    `azure.mgmt.cosmosdb.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.cosmosdb.operations.my_class_operations` (import
    from `azure.mgmt.cosmosdb.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.7.0 (2019-06-07)

**Features**

  - Added operation
    DatabaseAccountsOperations.get_gremlin_graph_throughput
  - Added operation
    DatabaseAccountsOperations.get_sql_database_throughput
  - Added operation
    DatabaseAccountsOperations.update_gremlin_database_throughput
  - Added operation
    DatabaseAccountsOperations.get_sql_container_throughput
  - Added operation
    DatabaseAccountsOperations.update_sql_container_throughput
  - Added operation
    DatabaseAccountsOperations.get_gremlin_database_throughput
  - Added operation
    DatabaseAccountsOperations.get_cassandra_table_throughput
  - Added operation
    DatabaseAccountsOperations.update_cassandra_keyspace_throughput
  - Added operation
    DatabaseAccountsOperations.update_mongo_db_collection_throughput
  - Added operation
    DatabaseAccountsOperations.update_cassandra_table_throughput
  - Added operation DatabaseAccountsOperations.update_table_throughput
  - Added operation
    DatabaseAccountsOperations.update_mongo_db_database_throughput
  - Added operation
    DatabaseAccountsOperations.get_mongo_db_database_throughput
  - Added operation
    DatabaseAccountsOperations.update_sql_database_throughput
  - Added operation DatabaseAccountsOperations.get_table_throughput
  - Added operation
    DatabaseAccountsOperations.get_mongo_db_collection_throughput
  - Added operation
    DatabaseAccountsOperations.update_gremlin_graph_throughput
  - Added operation
    DatabaseAccountsOperations.get_cassandra_keyspace_throughput

## 0.6.1 (2019-05-31)

**Features**

  - Add is_zone_redundant attribute

**Bugfix**

  - Fix some incorrect type from int to long (Python 2)

## 0.6.0 (2019-05-03)

**Features**

  - Added operation DatabaseAccountsOperations.list_sql_databases
  - Added operation DatabaseAccountsOperations.delete_gremlin_graph
  - Added operation DatabaseAccountsOperations.get_sql_database
  - Added operation DatabaseAccountsOperations.delete_table
  - Added operation DatabaseAccountsOperations.get_cassandra_keyspace
  - Added operation DatabaseAccountsOperations.list_sql_containers
  - Added operation
    DatabaseAccountsOperations.create_update_sql_container
  - Added operation DatabaseAccountsOperations.get_table
  - Added operation DatabaseAccountsOperations.list_cassandra_tables
  - Added operation DatabaseAccountsOperations.create_update_table
  - Added operation
    DatabaseAccountsOperations.delete_mongo_db_collection
  - Added operation DatabaseAccountsOperations.get_gremlin_graph
  - Added operation DatabaseAccountsOperations.get_gremlin_database
  - Added operation
    DatabaseAccountsOperations.list_cassandra_keyspaces
  - Added operation
    DatabaseAccountsOperations.create_update_mongo_db_collection
  - Added operation
    DatabaseAccountsOperations.create_update_cassandra_keyspace
  - Added operation
    DatabaseAccountsOperations.create_update_cassandra_table
  - Added operation DatabaseAccountsOperations.get_mongo_db_database
  - Added operation DatabaseAccountsOperations.list_gremlin_databases
  - Added operation
    DatabaseAccountsOperations.create_update_sql_database
  - Added operation
    DatabaseAccountsOperations.get_mongo_db_collection
  - Added operation
    DatabaseAccountsOperations.list_mongo_db_collections
  - Added operation DatabaseAccountsOperations.get_sql_container
  - Added operation
    DatabaseAccountsOperations.delete_cassandra_keyspace
  - Added operation
    DatabaseAccountsOperations.delete_mongo_db_database
  - Added operation DatabaseAccountsOperations.get_cassandra_table
  - Added operation DatabaseAccountsOperations.delete_cassandra_table
  - Added operation
    DatabaseAccountsOperations.list_mongo_db_databases
  - Added operation DatabaseAccountsOperations.list_gremlin_graphs
  - Added operation
    DatabaseAccountsOperations.create_update_mongo_db_database
  - Added operation DatabaseAccountsOperations.delete_sql_container
  - Added operation
    DatabaseAccountsOperations.create_update_gremlin_graph
  - Added operation
    DatabaseAccountsOperations.create_update_gremlin_database
  - Added operation DatabaseAccountsOperations.list_tables
  - Added operation DatabaseAccountsOperations.delete_gremlin_database
  - Added operation DatabaseAccountsOperations.delete_sql_database

## 0.5.2 (2018-11-05)

**Features**

  - Add ignore_missing_vnet_service_endpoint support

## 0.5.1 (2018-10-16)

**Bugfix**

  - Fix sdist broken in 0.5.0. No code change.

## 0.5.0 (2018-10-08)

**Features**

  - Add enable_multiple_write_locations support

**Note**

  - `database_accounts.list_read_only_keys` is now doing a POST
    call, and not GET anymore. This should not impact anything. Old
    behavior be can found with the
    `database_accounts.get_read_only_keys` **deprecated** method.
  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.4.1 (2018-05-15)

**Features**

  - Add database_accounts.offline_region
  - Add database_accounts.online_region
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 0.4.0 (2018-04-17)

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

  - Compatibility of the sdist with wheel 0.31.0

**Features**

  - Add VNet related properties to CosmosDB

## 0.3.1 (2018-02-01)

**Bugfixes**

  - Fix capabilities model definition

## 0.3.0 (2018-01-30)

**Features**

  - Add capability
  - Add metrics operation groups

## 0.2.1 (2017-10-18)

**Bugfixes**

  - Fix max_interval_in_seconds interval values from 1/100 to 5/86400
  - Tags is now optional

**Features**

  - Add operation list

## 0.2.0 (2017-06-26)

  - Creation on this package based on azure-mgmt-documentdb 0.1.3
    content
