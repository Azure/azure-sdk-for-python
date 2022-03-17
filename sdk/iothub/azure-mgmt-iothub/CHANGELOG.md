# Release History

## 2.2.0 (2022-01-29)

**Features**

  - Model IotHubDescription has a new parameter system_data
  - Model IotHubProperties has a new parameter enable_data_residency

## 2.1.0 (2021-08-25)

**Features**

  - Model IotHubProperties has a new parameter disable_local_auth
  - Model IotHubProperties has a new parameter disable_device_sas
  - Model IotHubProperties has a new parameter restrict_outbound_network_access
  - Model IotHubProperties has a new parameter allowed_fqdn_list
  - Model IotHubProperties has a new parameter disable_module_sas
  - Model CertificateBodyDescription has a new parameter is_verified

## 2.0.0 (2021-05-14)

**Features**

  - Model EndpointHealthData has a new parameter last_send_attempt_time
  - Model EndpointHealthData has a new parameter last_known_error_time
  - Model EndpointHealthData has a new parameter last_known_error
  - Model EndpointHealthData has a new parameter last_successful_send_attempt_time
  - Model ImportDevicesRequest has a new parameter identity
  - Model ImportDevicesRequest has a new parameter configurations_blob_name
  - Model ImportDevicesRequest has a new parameter include_configurations
  - Model RoutingServiceBusTopicEndpointProperties has a new parameter identity
  - Model RoutingStorageContainerProperties has a new parameter identity
  - Model StorageEndpointProperties has a new parameter identity
  - Model IotHubDescription has a new parameter identity
  - Model IotHubProperties has a new parameter network_rule_sets
  - Model ExportDevicesRequest has a new parameter identity
  - Model ExportDevicesRequest has a new parameter configurations_blob_name
  - Model ExportDevicesRequest has a new parameter include_configurations
  - Model RoutingServiceBusQueueEndpointProperties has a new parameter identity
  - Model RoutingEventHubProperties has a new parameter identity

**Breaking changes**

  - Operation IotHubResourceOperations.create_event_hub_consumer_group has a new signature

## 1.0.0 (2020-12-18)

- GA release

## 1.0.0b1 (2020-11-12)

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

## 0.12.0 (2020-05-12)

**Features**

  - Model RoutingEventHubProperties has a new parameter entity_path
  - Model RoutingEventHubProperties has a new parameter authentication_type
  - Model RoutingEventHubProperties has a new parameter endpoint_uri
  - Model RoutingEventHubProperties has a new parameter id
  - Model RoutingServiceBusQueueEndpointProperties has a new parameter entity_path
  - Model RoutingServiceBusQueueEndpointProperties has a new parameter authentication_type
  - Model RoutingServiceBusQueueEndpointProperties has a new parameter endpoint_uri
  - Model RoutingServiceBusQueueEndpointProperties has a new parameter id
  - Model ImportDevicesRequest has a new parameter authentication_type
  - Model ImportDevicesRequest has a new parameter output_blob_name
  - Model ImportDevicesRequest has a new parameter input_blob_name
  - Model ExportDevicesRequest has a new parameter authentication_type
  - Model ExportDevicesRequest has a new parameter export_blob_name
  - Model RoutingServiceBusTopicEndpointProperties has a new parameter entity_path
  - Model RoutingServiceBusTopicEndpointProperties has a new parameter authentication_type
  - Model RoutingServiceBusTopicEndpointProperties has a new parameter endpoint_uri
  - Model RoutingServiceBusTopicEndpointProperties has a new parameter id
  - Model RoutingStorageContainerProperties has a new parameter authentication_type
  - Model RoutingStorageContainerProperties has a new parameter endpoint_uri
  - Model RoutingStorageContainerProperties has a new parameter id
  - Model IotHubProperties has a new parameter public_network_access
  - Model IotHubProperties has a new parameter private_endpoint_connections
  - Model IotHubProperties has a new parameter min_tls_version
  - Model StorageEndpointProperties has a new parameter authentication_type
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

**Breaking changes**

  - Operation IotHubResourceOperations.export_devices has a new signature
  - Operation IotHubResourceOperations.import_devices has a new signature

## 0.11.0 (2020-03-17)

  - Preview API versions 2018-12-01-preview, 2019-03-22-preview, 2019-07-01-preview included

## 0.10.0 (2020-01-09)

**Features**

  - Support for multi-api

**Breaking changes**

  - Model IotHubProperties no longer has parameter device_streams

## 0.9.0 (2019-10-09)

  - Release 0.9.0 as stable.

## 0.9.0rc1 (2019-09-29)

**Features**

  - Model IotHubProperties has a new parameter locations

**General breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if from some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - IotHubClient cannot be imported from
    `azure.mgmt.iothub.iot_hub_client` anymore (import from
    `azure.mgmt.iothub` works like before)
  - IotHubClientConfiguration import has been moved from
    `azure.mgmt.iothub.iot_hub_client` to `azure.mgmt.iothub`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.iothub.models.my_class` (import from
    `azure.mgmt.iothub.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.iothub.operations.my_class_operations` (import from
    `azure.mgmt.iothub.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.8.2 (2019-05-15)

**Bugfixes**

  - Fix manual_failover operation type

## 0.8.1 (2019-05-13)

**Bugfixes**

  - Re-shipping 0.8.0 with wheel 0.33.4
    (<https://github.com/pypa/wheel/issues/294>)

## 0.8.0 (2019-05-10)

**Features**

  - Model RoutingProperties has a new parameter enrichments
  - Added operation group IotHubOperations

**Breaking changes**

  - Model IotHubProperties no longer has parameter
    operations_monitoring_properties

## 0.7.0 (2018-12-14)

**Features**

  - Model OperationDisplay has a new parameter description
  - Model TestRouteInput has a new parameter twin
  - Model IotHubProperties has a new parameter device_streams
  - Model TestAllRoutesInput has a new parameter twin

**Breaking changes**

  - Operation IotHubResourceOperations.test_route has a new signature
  - Operation IotHubResourceOperations.test_all_routes has a new
    signature

## 0.6.0 (2018-08-27)

**Features**

  - Model CertificatePropertiesWithNonce has a new parameter certificate
  - Model CertificateProperties has a new parameter certificate
  - Added operation IotHubResourceOperations.test_all_routes
  - Added operation IotHubResourceOperations.test_route
  - Added operation IotHubResourceOperations.get_endpoint_health
  - Added operation group ResourceProviderCommonOperations
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

## 0.5.0 (2018-04-17)

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

  - Add new ApiVersion 2018-04-01

## 0.4.0 (2017-10-11)

**Features**

  - New API version 2017-07-01. This is a backward compatible.
  - Add "if_match" parameter when applicable
  - Add certificates operation group
  - Add list available operations method
  - Add "storage_containers" attribute to RoutingEndpoints

## 0.3.0 (2017-06-13)

**Features**

  - New API version 2017-01-19. This is a backward compatible.
  - Adding "routing" information

## 0.2.2 (2017-04-20)

**Bugfixes**

  - Fix possible deserialization error, but updating from dict<str,
    enumtype> to dict<str, str> when applicable

**Notes**

  - This wheel package is now built with the azure wheel extension

## 0.2.1 (2016-12-16)

**Bugfixes**

  - Fix #920 - Invalid return type for
    `list_event_hub_consumer_groups`

## 0.2.0 (2016-12-12)

**Bugfixes**

  - Better parameters checking (change exception from CloudError to
    TypeError)
  - Date parsing fix (incorrect None date)
  - CreateOrUpdate random exception fix

## 0.1.0 (2016-08-12)

  - Initial Release
