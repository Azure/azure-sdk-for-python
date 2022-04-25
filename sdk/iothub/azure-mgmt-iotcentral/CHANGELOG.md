# Release History

## 10.0.0b1 (2022-04-13)

**Features**

  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinksOperations
  - Model App has a new parameter network_rule_sets
  - Model App has a new parameter private_endpoint_connections
  - Model App has a new parameter provisioning_state
  - Model App has a new parameter public_network_access
  - Model App has a new parameter system_data
  - Model AppPatch has a new parameter network_rule_sets
  - Model AppPatch has a new parameter private_endpoint_connections
  - Model AppPatch has a new parameter provisioning_state
  - Model AppPatch has a new parameter public_network_access
  - Model Resource has a new parameter system_data

**Breaking changes**

  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter tags

## 9.0.0 (2021-11-11)

**Features**

  - Model App has a new parameter state
  - Model App has a new parameter identity
  - Model AppPatch has a new parameter state
  - Model AppPatch has a new parameter identity

## 9.0.0b1 (2021-05-13)

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

## 4.1.0 (2021-02-19)

**Features**

  - Model AppTemplate has a new parameter industry
  - Model AppTemplate has a new parameter locations
  - Model Operation has a new parameter properties
  - Model Operation has a new parameter origin

## 4.0.0 (2021-01-05)

**Features**

  - Model AppTemplate has a new parameter name

**Breaking changes**

  - Model AppTemplate no longer has parameter app_template_name

## 3.1.0 (2020-06-30)

**Features**

  - Model AppPatch has a new parameter sku

## 3.0.0 (2020-03-09)

**Breaking changes**

- Removed operation AppsOperations.list_templates

## 2.0.0 (2019-12-25)

**Features**

  - Added operation AppsOperations.list_templates

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. IoTCentralClient cannot be imported from
azure.mgmt.iotcentreal.iot_central_client anymore (import from
azure.mgmt.iotcentreal works like before) IoTCentralClientConfiguration
import has been moved from azure.mgmt.iotcentreal.iot_central_client
to azure.mgmt.iotcentreal A model MyClass from a "models" sub-module
cannot be imported anymore using azure.mgmt.iotcentreal.models.my_class
(import from azure.mgmt.iotcentreal.models works like before) An
operation class MyClassOperations from an operations sub-module cannot
be imported anymore using
azure.mgmt.iotcentreal.operations.my_class_operations (import from
azure.mgmt.iotcentreal.operations works like before) Last but not least,
HTTP connection pooling is now enabled by default. You should always use
a client as a context manager, or call close(), or use no more than one
client per process.

## 1.0.0 (2018-10-26)

**Features**

  - Model OperationInputs has a new parameter type
  - Model ErrorDetails has a new parameter details
  - Added operation AppsOperations.check_subdomain_availability

**Breaking changes**

  - Operation AppsOperations.check_name_availability has a new
    signature

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 0.2.0 (2018-08-07)

  - Replace API version by 2018-09-01

## 0.1.0 (2018-07-16)

  - Initial Release with support for 2017-07-01-privatepreview
