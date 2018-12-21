.. :changelog:

Release History
===============

0.2.0 (2018-11-27)
++++++++++++++++++

**Features**

- Model Cluster has a new parameter uri
- Model Cluster has a new parameter state
- Model Cluster has a new parameter data_ingestion_uri
- Model Cluster has a new parameter trusted_external_tenants
- Model DatabaseUpdate has a new parameter etag
- Model DatabaseUpdate has a new parameter statistics
- Model DatabaseUpdate has a new parameter hot_cache_period_in_days
- Model Database has a new parameter statistics
- Model Database has a new parameter hot_cache_period_in_days
- Model ClusterUpdate has a new parameter uri
- Model ClusterUpdate has a new parameter etag
- Model ClusterUpdate has a new parameter state
- Model ClusterUpdate has a new parameter sku
- Model ClusterUpdate has a new parameter tags
- Model ClusterUpdate has a new parameter data_ingestion_uri
- Model ClusterUpdate has a new parameter trusted_external_tenants
- Added operation DatabasesOperations.list_principals
- Added operation DatabasesOperations.check_name_availability
- Added operation DatabasesOperations.add_principals
- Added operation DatabasesOperations.remove_principals
- Added operation ClustersOperations.list_skus
- Added operation ClustersOperations.list_skus_by_resource
- Added operation ClustersOperations.start
- Added operation ClustersOperations.check_name_availability
- Added operation ClustersOperations.stop
- Added operation group EventHubConnectionsOperations

**Breaking changes**

- Operation DatabasesOperations.update has a new signature
- Operation ClustersOperations.update has a new signature
- Operation DatabasesOperations.update has a new signature
- Operation ClustersOperations.create_or_update has a new signature
- Model Cluster has a new required parameter sku

0.1.0 (2018-08-09)
++++++++++++++++++

* Initial Release
