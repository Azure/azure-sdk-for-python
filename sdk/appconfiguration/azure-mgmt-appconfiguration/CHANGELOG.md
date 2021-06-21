# Release History

## 0.7.0 (2021-06-21)

**Features**

  - Model OperationDefinition has a new parameter is_data_action
  - Model OperationDefinition has a new parameter properties
  - Model OperationDefinition has a new parameter origin
  - Model ConfigurationStore has a new parameter disable_local_auth
  - Model ConfigurationStore has a new parameter system_data
  - Model KeyValue has a new parameter id
  - Model KeyValue has a new parameter type
  - Model KeyValue has a new parameter name
  - Model ConfigurationStoreUpdateParameters has a new parameter disable_local_auth
  - Added operation group KeyValuesOperations

**Breaking changes**

  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter tags
  - Removed operation ConfigurationStoresOperations.list_key_value

## 0.6.0 (2020-08-19)

**Features**

  - Model ConfigurationStoreUpdateParameters has a new parameter public_network_access

## 0.5.0 (2020-07-01)

**Features**

  - Model ConfigurationStore has a new parameter private_endpoint_connections
  - Model ConfigurationStore has a new parameter public_network_access
  - Model PrivateLinkResource has a new parameter required_zone_names

## 0.4.0 (2020-02-07)

**Features**

- Model ConfigurationStoreUpdateParameters has a new parameter encryption
- Model ConfigurationStore has a new parameter encryption
- Added operation group PrivateEndpointConnectionsOperations
- Added operation group PrivateLinkResourcesOperations

**Breaking changes**

- Model ConfigurationStoreUpdateParameters no longer has parameter properties

## 0.3.0 (2019-11-08)

**Features**

  - Model ConfigurationStore has a new parameter identity
  - Model ConfigurationStoreUpdateParameters has a new parameter
    identity
  - Model ConfigurationStoreUpdateParameters has a new parameter sku

**Breaking changes**

  - Operation ConfigurationStoresOperations.create has a new signature
  - Operation ConfigurationStoresOperations.update has a new signature
  - Model ConfigurationStore has a new required parameter sku

## 0.2.0 (2019-11-04)

**Features**

  - Added operation ConfigurationStoresOperations.list_key_value

## 0.1.0 (2019-06-17)

  - Initial Release
