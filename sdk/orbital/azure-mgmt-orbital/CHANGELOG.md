# Release History

## 1.0.0 (2022-06-01)

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
