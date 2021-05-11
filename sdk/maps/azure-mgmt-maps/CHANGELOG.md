# Release History

## 0.2.0 (2021-05-08)

**Features**

  - Model MapsAccount has a new parameter system_data
  - Model MapsAccount has a new parameter kind
  - Model MapsAccount has a new parameter properties
  - Model MapsAccountKeys has a new parameter primary_key_last_updated
  - Model MapsAccountKeys has a new parameter secondary_key_last_updated
  - Added operation group MapsOperationsOperations
  - Added operation group CreatorsOperations

**Breaking changes**

  - Operation AccountsOperations.create_or_update has a new signature
  - Parameter sku of model MapsAccount is now required
  - Parameter location of model MapsAccount is now required
  - Model MapsAccountKeys no longer has parameter id
  - Operation AccountsOperations.update has a new signature
  - Model MapsAccountUpdateParameters has a new signature
  - Removed operation AccountsOperations.list_operations
  - Removed operation AccountsOperations.move

## 0.1.0 (2018-05-07)

  - Initial Release
