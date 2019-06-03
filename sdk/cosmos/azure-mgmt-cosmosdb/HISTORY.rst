.. :changelog:

Release History
===============

0.6.1 (2019-05-31)
++++++++++++++++++

**Features**

- Add is_zone_redundant attribute

**Bugfix**

- Fix some incorrect type from int to long (Python 2)

0.6.0 (2019-05-03)
++++++++++++++++++

**Features**

- Added operation DatabaseAccountsOperations.list_sql_databases
- Added operation DatabaseAccountsOperations.delete_gremlin_graph
- Added operation DatabaseAccountsOperations.get_sql_database
- Added operation DatabaseAccountsOperations.delete_table
- Added operation DatabaseAccountsOperations.get_cassandra_keyspace
- Added operation DatabaseAccountsOperations.list_sql_containers
- Added operation DatabaseAccountsOperations.create_update_sql_container
- Added operation DatabaseAccountsOperations.get_table
- Added operation DatabaseAccountsOperations.list_cassandra_tables
- Added operation DatabaseAccountsOperations.create_update_table
- Added operation DatabaseAccountsOperations.delete_mongo_db_collection
- Added operation DatabaseAccountsOperations.get_gremlin_graph
- Added operation DatabaseAccountsOperations.get_gremlin_database
- Added operation DatabaseAccountsOperations.list_cassandra_keyspaces
- Added operation DatabaseAccountsOperations.create_update_mongo_db_collection
- Added operation DatabaseAccountsOperations.create_update_cassandra_keyspace
- Added operation DatabaseAccountsOperations.create_update_cassandra_table
- Added operation DatabaseAccountsOperations.get_mongo_db_database
- Added operation DatabaseAccountsOperations.list_gremlin_databases
- Added operation DatabaseAccountsOperations.create_update_sql_database
- Added operation DatabaseAccountsOperations.get_mongo_db_collection
- Added operation DatabaseAccountsOperations.list_mongo_db_collections
- Added operation DatabaseAccountsOperations.get_sql_container
- Added operation DatabaseAccountsOperations.delete_cassandra_keyspace
- Added operation DatabaseAccountsOperations.delete_mongo_db_database
- Added operation DatabaseAccountsOperations.get_cassandra_table
- Added operation DatabaseAccountsOperations.delete_cassandra_table
- Added operation DatabaseAccountsOperations.list_mongo_db_databases
- Added operation DatabaseAccountsOperations.list_gremlin_graphs
- Added operation DatabaseAccountsOperations.create_update_mongo_db_database
- Added operation DatabaseAccountsOperations.delete_sql_container
- Added operation DatabaseAccountsOperations.create_update_gremlin_graph
- Added operation DatabaseAccountsOperations.create_update_gremlin_database
- Added operation DatabaseAccountsOperations.list_tables
- Added operation DatabaseAccountsOperations.delete_gremlin_database
- Added operation DatabaseAccountsOperations.delete_sql_database

0.5.2 (2018-11-05)
++++++++++++++++++

**Features**

- Add ignore_missing_vnet_service_endpoint support

0.5.1 (2018-10-16)
++++++++++++++++++

**Bugfix**

- Fix sdist broken in 0.5.0. No code change.

0.5.0 (2018-10-08)
++++++++++++++++++

**Features**

- Add enable_multiple_write_locations support

**Note**

- `database_accounts.list_read_only_keys` is now doing a POST call, and not GET anymore. This should not impact anything.
  Old behavior be can found with the `database_accounts.get_read_only_keys` **deprecated** method.
- azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

0.4.1 (2018-05-15)
++++++++++++++++++

**Features**

- Add database_accounts.offline_region
- Add database_accounts.online_region
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

0.4.0 (2018-04-17)
++++++++++++++++++

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

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

**Features**

- Add VNet related properties to CosmosDB


0.3.1 (2018-02-01)
++++++++++++++++++

**Bugfixes**

- Fix capabilities model definition

0.3.0 (2018-01-30)
++++++++++++++++++

**Features**

- Add capability
- Add metrics operation groups

0.2.1 (2017-10-18)
++++++++++++++++++

**Bugfixes**

* Fix max_interval_in_seconds interval values from 1/100 to 5/86400
* Tags is now optional

**Features**

* Add operation list

0.2.0 (2017-06-26)
++++++++++++++++++

* Creation on this package based on azure-mgmt-documentdb 0.1.3 content
