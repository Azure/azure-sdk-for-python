# Release History

## 0.3.0 (2021-01-28)

**Features**

  - Model AttestationProvider has a new parameter private_endpoint_connections
  - Added operation group PrivateEndpointConnectionsOperations

## 0.2.0 (2020-11-17)

**Features**

  - Model AttestationProvider has a new parameter trust_model
  - Model AttestationProvider has a new parameter tags
  - Model AttestationProvider has a new parameter system_data
  - Model AttestationProviderListResult has a new parameter system_data
  - Model OperationList has a new parameter system_data
  - Added operation AttestationProvidersOperations.get_default_by_location
  - Added operation AttestationProvidersOperations.list_default
  - Added operation AttestationProvidersOperations.update

**Breaking changes**

  - Model AttestationProvider has a new required parameter location
  - Operation AttestationProvidersOperations.create has a new signature
  - Model AttestationServiceCreationParams has a new signature

## 0.1.0 (2019-11-28)

**Features**

  - Model AttestationServiceCreationParams has a new parameter
    policy_signing_certificates

**Breaking changes**

  - Operation AttestationProvidersOperations.create has a new signature

## 0.1.0rc1 (2019-09-03)

  - Initial Release
