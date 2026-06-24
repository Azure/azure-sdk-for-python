# Release History

## 3.0.0 (2026-06-24)

### Features Added

  - Client `QumuloMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `QumuloMgmtClient` added method `send_request`
  - Model `FileSystemResource` added property `properties`
  - Model `FileSystemResourceUpdateProperties` added property `performance_tier`
  - Added model `FileSystemResourceProperties`

### Breaking Changes

  - Model `FileSystemResource` deleted or renamed its instance variable `marketplace_details`
  - Model `FileSystemResource` deleted or renamed its instance variable `provisioning_state`
  - Model `FileSystemResource` deleted or renamed its instance variable `storage_sku`
  - Model `FileSystemResource` deleted or renamed its instance variable `user_details`
  - Model `FileSystemResource` deleted or renamed its instance variable `delegated_subnet_id`
  - Model `FileSystemResource` deleted or renamed its instance variable `cluster_login_url`
  - Model `FileSystemResource` deleted or renamed its instance variable `private_ips`
  - Model `FileSystemResource` deleted or renamed its instance variable `admin_password`
  - Model `FileSystemResource` deleted or renamed its instance variable `availability_zone`
  - Deleted or renamed model `FileSystemResourceListResult`
  - Deleted or renamed model `OperationListResult`

## 2.1.0 (2026-06-23)

### Features Added

  - Client `QumuloMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `QumuloMgmtClient` added method `send_request`
  - Model `FileSystemResourceUpdateProperties` added property `performance_tier`

## 3.0.0 (2026-06-19)

### Breaking Changes

  - Model `FileSystemResource` no longer exposes service-specific fields (`marketplace_details`, `storage_sku`, `admin_password`, `delegated_subnet_id`, `provisioning_state`, `cluster_login_url`, `private_ips`, `availability_zone`, `user_details`) as top-level attributes; they are now accessible via the nested `properties` attribute of type `FileSystemResourceProperties` (e.g. `file_system.properties.storage_sku`)
  - Model `FileSystemResourceListResult` removed from the package namespace
  - Model `OperationListResult` removed from the package namespace

### Features Added

  - Client `QumuloMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `QumuloMgmtClient` added method `send_request`
  - Model `FileSystemResourceUpdateProperties` added property `performance_tier`

## 2.0.0 (2024-09-05)

### Features Added

  - Model MarketplaceDetails has a new parameter term_unit

### Breaking Changes

  - Model FileSystemResource no longer has parameter initial_capacity
  - Rename parameter `private_i_ps` to `private_ips` in Model FileSystemResource
  - Model FileSystemResourceUpdateProperties no longer has parameter cluster_login_url
  - Model FileSystemResourceUpdateProperties no longer has parameter private_i_ps

## 1.0.0 (2023-05-20)

### other change

  - First GA

## 1.0.0b1 (2023-04-14)

* Initial Release
