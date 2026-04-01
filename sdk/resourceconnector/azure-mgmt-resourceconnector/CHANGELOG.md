# Release History

## 2.0.0b1 (2026-01-13)

### Features Added

  - Model `ResourceConnectorMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `ResourceConnectorMgmtClient` added method `send_request`
  - Model `ApplianceOperation` added property `display`
  - Enum `SSHKeyType` added member `USER_MANAGEMENT_KEY`
  - Enum `Status` added member `ARC_GATEWAY_UPDATE_COMPLETE`
  - Enum `Status` added member `ARC_GATEWAY_UPDATE_FAILED`
  - Enum `Status` added member `ARC_GATEWAY_UPDATE_PREPARING`
  - Enum `Status` added member `ARC_GATEWAY_UPDATING`
  - Enum `Status` added member `NETWORK_DNS_UPDATE_COMPLETE`
  - Enum `Status` added member `NETWORK_DNS_UPDATE_FAILED`
  - Enum `Status` added member `NETWORK_DNS_UPDATE_PREPARING`
  - Enum `Status` added member `NETWORK_DNS_UPDATING`
  - Enum `Status` added member `NETWORK_PROXY_UPDATE_COMPLETE`
  - Enum `Status` added member `NETWORK_PROXY_UPDATE_FAILED`
  - Enum `Status` added member `NETWORK_PROXY_UPDATE_PREPARING`
  - Enum `Status` added member `NETWORK_PROXY_UPDATING`
  - Added model `ApplianceOperationValueDisplay`
  - Added model `DnsConfiguration`
  - Added model `Event`
  - Added model `GatewayConfiguration`
  - Added model `NetworkProfile`
  - Added model `ProxyConfiguration`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `ApplianceOperation` moved instance variable `description`, `operation`, `provider` and `resource` under property `display`
  - Method `AppliancesOperations.list_keys` changed its parameter `artifact_type` from `positional_or_keyword` to `keyword_only`
  - Method `AppliancesOperations.update` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ApplianceOperationsList` which actually was not used by SDK users
  - Method `AppliancesOperations.update` inserted a `positional_or_keyword` parameter `parameters` but this change won't break runtime behavior

## 1.0.0 (2023-08-18)

### Features Added

  - Operation AppliancesOperations.list_keys has a new optional parameter artifact_type

## 1.0.0b4 (2023-04-24)

### Breaking Changes

  - Client name is changed from `Appliances` to `ResourceConnectorMgmtClient`

## 1.0.0b3 (2022-12-12)

### Features Added

  - Added operation AppliancesOperations.get_telemetry_config
  - Added operation AppliancesOperations.list_keys
  - Model Resource has a new parameter system_data
  - Model SSHKey has a new parameter certificate
  - Model SSHKey has a new parameter creation_time_stamp
  - Model SSHKey has a new parameter expiration_time_stamp
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Removed operation AppliancesOperations.list_cluster_customer_user_credential

## 1.0.0b2 (2022-07-01)

**Features**

  - Added operation AppliancesOperations.get_upgrade_graph
  - Added operation AppliancesOperations.list_cluster_customer_user_credential

## 1.0.0b1 (2021-11-12)

* Initial Release
