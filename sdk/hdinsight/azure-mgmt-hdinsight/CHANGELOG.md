# Release History

## 7.0.0 (2020-12-18)

**Features**

  - Model HostInfo has a new parameter effective_disk_encryption_key_url
  - Model HostInfo has a new parameter fqdn
  - Model ClusterGetProperties has a new parameter compute_isolation_properties
  - Model ClusterCreateProperties has a new parameter compute_isolation_properties

**Breaking changes**

  - Operation ExtensionsOperations.begin_create has a new signature
  - Operation ClustersOperations.begin_update_auto_scale_configuration has a new signature
  - Operation ClustersOperations.begin_resize has a new signature
  - Operation ClustersOperations.update has a new signature
  - Operation ExtensionsOperations.begin_create has a new signature
  - Operation ExtensionsOperations.begin_enable_monitoring has a new signature
  - Operation ClustersOperations.begin_execute_script_actions has a new signature

## 7.0.0b1 (2020-10-31)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 2.0.0(https://pypi.org/project/azure-mgmt-hdinsight/2.0.0/)

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 2.0.0 (2020-10-20)

**Features**

  - Model ClusterGetProperties has a new parameter network_properties
  - Model ClusterGetProperties has a new parameter cluster_id
  - Model ClusterCreateProperties has a new parameter network_properties

**Breaking changes**

  - Model ClusterGetProperties no longer has parameter network_settings
  - Model ClusterCreateProperties no longer has parameter network_settings
  
## 1.7.0 (2020-08-13)

**Features**

  - Model DiskEncryptionProperties has a new parameter encryption_at_host

## 1.6.0 (2020-07-17)

**Features**

  - Added operation group VirtualMachinesOperations

## 1.5.1 (2020-06-11)

**Bugfixes**

  - Fix the List Response

## 1.5.0 (2020-05-29)

**Features**

  - Added operation group VirtualMachinesOperations

## 1.4.0 (2020-01-16)

**Features**

  - Model ClusterCreateProperties has a new parameter
    min_supported_tls_version
  - Model ClusterGetProperties has a new parameter
    min_supported_tls_version

## 1.3.0 (2019-12-07)

**Features**

  - Model ClusterGetProperties has a new parameter
    kafka_rest_properties
  - Model ClusterCreateProperties has a new parameter
    kafka_rest_properties

## 1.2.0 (2019-08-06)

**Features**

  - Model Role has a new parameter autoscale_configuration
  - Added operation LocationsOperations.list_billing_specs
  - Added operation LocationsOperations.get_capabilities

## 1.1.0 (2019-06-17)

**Features**

  - Model ApplicationGetHttpsEndpoint has a new parameter
    disable_gateway_auth
  - Model ApplicationGetHttpsEndpoint has a new parameter
    sub_domain_suffix

## 1.0.0 (2019-04-08)

Stable versionning of the 0.3.0 (no changes)

## 0.3.0 (2019-04-08)

**Features**

  - Added operation ConfigurationsOperations.list
  - Added operation ClustersOperations.get_gateway_settings
  - Added operation ClustersOperations.update_gateway_settings

## 0.2.1 (2019-01-28)

**Features**

  - Add MSI support

## 0.2.0 (2018-12-11)

**Features**

  - Model SecurityProfile has a new parameter msi_resource_id
  - Model SecurityProfile has a new parameter aadds_resource_id
  - Model ClusterCreateProperties has a new parameter
    disk_encryption_properties
  - Model ClusterGetProperties has a new parameter
    disk_encryption_properties
  - Model Cluster has a new parameter identity
  - Model ClusterCreateParametersExtended has a new parameter identity
  - Added operation ClustersOperations.rotate_disk_encryption_key
  - Added operation ScriptActionsOperations.list_by_cluster
  - Added operation ScriptExecutionHistoryOperations.list_by_cluster
  - Added operation ConfigurationsOperations.update
  - Added operation ApplicationsOperations.list_by_cluster
  - Added operation group ExtensionsOperations

**Breaking changes**

  - Model ApplicationProperties no longer has parameter
    additional_properties
  - Model ApplicationGetHttpsEndpoint no longer has parameter
    additional_properties
  - Removed operation ScriptActionsOperations.list_persisted_scripts
  - Removed operation ScriptExecutionHistoryOperations.list
  - Removed operation ConfigurationsOperations.update_http_settings
  - Removed operation ApplicationsOperations.list
  - Removed operation LocationsOperations.get_capabilities
  - Removed operation group ExtensionOperations

## 0.1.0 (2018-08-08)

  - Initial Release
