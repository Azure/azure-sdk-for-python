# Release History

## 1.1.0b1 (2022-11-07)

### Features Added

  - Model AccountUpdateParameters has a new parameter identity
  - Model Identity has a new parameter user_assigned_identities

## 1.0.0 (2021-08-13)

**Features**

  - Model Account has a new parameter managed_resource_group_name
  - Model Account has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model PrivateLinkResource has a new parameter properties
  - Added operation AccountsOperations.add_root_collection_admin
  - Added operation PrivateEndpointConnectionsOperations.begin_create_or_update

**Breaking changes**

  - Model PrivateLinkResource no longer has parameter required_zone_names
  - Model PrivateLinkResource no longer has parameter group_id
  - Model PrivateLinkResource no longer has parameter required_members
  - Model AccountUpdateParameters has a new signature
  - Removed operation PrivateEndpointConnectionsOperations.create_or_update

## 1.0.0b1 (2021-02-01)

* Initial Release
