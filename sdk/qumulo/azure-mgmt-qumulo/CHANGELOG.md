# Release History

## 3.0.0 (2026-06-24)

### Features Added

  - Client `QumuloMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `QumuloMgmtClient` added method `send_request`
  - Model `FileSystemResourceUpdateProperties` added property `performance_tier`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `FileSystemResource` moved instance variable `marketplace_details`, `provisioning_state`, `storage_sku`, `user_details`, `delegated_subnet_id`, `cluster_login_url`, `private_ips`, `admin_password` and `availability_zone` under property `properties` whose type is `FileSystemResourceProperties`

### Other Changes
  
  - Deleted model `FileSystemResourceListResult`/`OperationListResult` which actually were not used by SDK users

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
