.. :changelog:

Release History
===============

1.2.0 (2019-08-06)
++++++++++++++++++

**Features**

- Model Role has a new parameter autoscale_configuration
- Added operation LocationsOperations.list_billing_specs
- Added operation LocationsOperations.get_capabilities

1.1.0 (2019-06-17)
++++++++++++++++++

**Features**

- Model ApplicationGetHttpsEndpoint has a new parameter disable_gateway_auth
- Model ApplicationGetHttpsEndpoint has a new parameter sub_domain_suffix

1.0.0 (2019-04-08)
++++++++++++++++++

Stable versionning of the 0.3.0 (no changes)

0.3.0 (2019-04-08)
++++++++++++++++++

**Features**

- Added operation ConfigurationsOperations.list
- Added operation ClustersOperations.get_gateway_settings
- Added operation ClustersOperations.update_gateway_settings

0.2.1 (2019-01-28)
++++++++++++++++++

**Features**

- Add MSI support

0.2.0 (2018-12-11)
++++++++++++++++++

**Features**

- Model SecurityProfile has a new parameter msi_resource_id
- Model SecurityProfile has a new parameter aadds_resource_id
- Model ClusterCreateProperties has a new parameter disk_encryption_properties
- Model ClusterGetProperties has a new parameter disk_encryption_properties
- Model Cluster has a new parameter identity
- Model ClusterCreateParametersExtended has a new parameter identity
- Added operation ClustersOperations.rotate_disk_encryption_key
- Added operation ScriptActionsOperations.list_by_cluster
- Added operation ScriptExecutionHistoryOperations.list_by_cluster
- Added operation ConfigurationsOperations.update
- Added operation ApplicationsOperations.list_by_cluster
- Added operation group ExtensionsOperations

**Breaking changes**

- Model ApplicationProperties no longer has parameter additional_properties
- Model ApplicationGetHttpsEndpoint no longer has parameter additional_properties
- Removed operation ScriptActionsOperations.list_persisted_scripts
- Removed operation ScriptExecutionHistoryOperations.list
- Removed operation ConfigurationsOperations.update_http_settings
- Removed operation ApplicationsOperations.list
- Removed operation LocationsOperations.get_capabilities
- Removed operation group ExtensionOperations

0.1.0 (2018-08-08)
++++++++++++++++++

* Initial Release
