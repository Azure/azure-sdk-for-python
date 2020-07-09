# Release History

## 0.4.0 (2020-05-29)

**Features**

  - Model ServiceSpecification has a new parameter log_specifications
  - Model SignalRResource has a new parameter network_ac_ls
  - Model SignalRResource has a new parameter upstream
  - Model SignalRResource has a new parameter private_endpoint_connections
  - Model SignalRResource has a new parameter kind
  - Model Operation has a new parameter is_data_action
  - Model SignalRCreateOrUpdateProperties has a new parameter upstream
  - Model SignalRCreateOrUpdateProperties has a new parameter network_ac_ls
  - Added operation group SignalRPrivateEndpointConnectionsOperations
  - Added operation group SignalRPrivateLinkResourcesOperations

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - SignalRClient cannot be imported from
    `azure.mgmt.signalr.signalr_client` anymore (import from
    `azure.mgmt.signalr` works like before)
  - SignalRClientConfiguration import has been moved from
    `azure.mgmt.signalr.signalr_client` 
    to `azure.mgmt.signalr`  
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.signalr.models.my_class` (import from
    `azure.mgmt.signalr.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.signalr.operations.my_class_operations` (import from
    `azure.mgmt.signalr.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.0 (2019-08-06)

**Features**

  - Model SignalRResource has a new parameter cors
  - Model SignalRResource has a new parameter features
  - Model SignalRCreateOrUpdateProperties has a new parameter cors
  - Model SignalRCreateOrUpdateProperties has a new parameter feature

## 0.2.0 (2019-05-21)

  - Add restart operation

## 0.1.1 (2018-09-04)

**Features**

  - Model SignalRKeys has a new parameter secondary_connection_string
  - Model SignalRKeys has a new parameter primary_connection_string
  - Model MetricSpecification has a new parameter dimensions
  - Model SignalRResource has a new parameter version
  - Added operation group UsagesOperations

## 0.1.0 (2018-05-07)

  - Initial Release
