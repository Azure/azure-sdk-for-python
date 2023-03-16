# Release History

## 1.1.0 (2023-03-20)

### Features Added

  - Model ContactProfile has a new parameter third_party_configurations
  - Model ContactProfileProperties has a new parameter third_party_configurations
  - Model ContactProfilesProperties has a new parameter third_party_configurations
  - Model OperationResult has a new parameter next_link
  - Model OperationResult has a new parameter value
  - Operation ContactProfilesOperations.begin_create_or_update has a new optional parameter third_party_configurations

### Breaking Changes

  - Model Contact no longer has parameter etag
  - Model ContactProfile no longer has parameter etag
  - Model Spacecraft no longer has parameter etag
  - Parameter contact_profile of model Contact is now required
  - Parameter expiration_date of model AuthorizedGroundstation is now required
  - Parameter ground_station of model AuthorizedGroundstation is now required
  - Parameter ground_station_name of model Contact is now required
  - Parameter id of model AvailableContactsSpacecraft is now required
  - Parameter id of model ContactParametersContactProfile is now required
  - Parameter id of model ContactsPropertiesContactProfile is now required
  - Parameter id of model ResourceReference is now required
  - Parameter links of model ContactProfile is now required
  - Parameter links of model Spacecraft is now required
  - Parameter network_configuration of model ContactProfile is now required
  - Parameter reservation_end_time of model Contact is now required
  - Parameter reservation_start_time of model Contact is now required
  - Parameter title_line of model Spacecraft is now required
  - Parameter tle_line1 of model Spacecraft is now required
  - Parameter tle_line2 of model Spacecraft is now required
  - Removed operation AvailableGroundStationsOperations.get

## 1.1.0b1 (2022-11-30)

### Features Added

  - Added model ContactsStatus

## 1.0.0 (2022-06-16)

**Features**

  - Added operation ContactProfilesOperations.begin_update_tags
  - Added operation SpacecraftsOperations.begin_update_tags
  - Added operation group OperationsResultsOperations
  - Model AvailableGroundStation has a new parameter release_mode
  - Model Contact has a new parameter antenna_configuration
  - Model Contact has a new parameter provisioning_state
  - Model ContactProfile has a new parameter event_hub_uri
  - Model ContactProfile has a new parameter network_configuration
  - Model ContactProfile has a new parameter provisioning_state
  - Model Spacecraft has a new parameter provisioning_state
  - Model SpacecraftLink has a new parameter authorizations

**Breaking changes**

  - Model ContactProfileLink has a new required parameter name
  - Model ContactProfileLinkChannel has a new required parameter name
  - Model Spacecraft no longer has parameter authorization_status
  - Model Spacecraft no longer has parameter authorization_status_extended
  - Model SpacecraftLink has a new required parameter name
  - Operation ContactProfilesOperations.begin_create_or_update has a new parameter event_hub_uri
  - Operation ContactProfilesOperations.begin_create_or_update has a new parameter network_configuration
  - Operation ContactProfilesOperations.begin_create_or_update has a new parameter provisioning_state
  - Operation ContactProfilesOperations.list has a new parameter skiptoken
  - Operation ContactProfilesOperations.list_by_subscription has a new parameter skiptoken
  - Operation ContactsOperations.list has a new parameter skiptoken
  - Operation SpacecraftsOperations.begin_create_or_update has a new parameter provisioning_state
  - Operation SpacecraftsOperations.list has a new parameter skiptoken
  - Operation SpacecraftsOperations.list_by_subscription has a new parameter skiptoken
  - Removed operation ContactProfilesOperations.update_tags
  - Removed operation SpacecraftsOperations.update_tags

## 1.0.0b1 (2021-11-19)

* Initial Release
