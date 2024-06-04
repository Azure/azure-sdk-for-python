# Release History

## 1.0.0 (2024-03-26)

### Features Added

  - Added operation CatalogsOperations.begin_upload_image
  - Model Catalog has a new parameter properties
  - Model Certificate has a new parameter properties
  - Model Deployment has a new parameter properties
  - Model Device has a new parameter properties
  - Model DeviceGroup has a new parameter properties
  - Model DeviceGroupUpdate has a new parameter properties
  - Model DeviceUpdate has a new parameter properties
  - Model Image has a new parameter properties
  - Model Product has a new parameter properties
  - Model ProductUpdate has a new parameter properties

### Breaking Changes

  - Model Catalog no longer has parameter provisioning_state
  - Model Certificate no longer has parameter certificate
  - Model Certificate no longer has parameter expiry_utc
  - Model Certificate no longer has parameter not_before_utc
  - Model Certificate no longer has parameter provisioning_state
  - Model Certificate no longer has parameter status
  - Model Certificate no longer has parameter subject
  - Model Certificate no longer has parameter thumbprint
  - Model Deployment no longer has parameter deployed_images
  - Model Deployment no longer has parameter deployment_date_utc
  - Model Deployment no longer has parameter deployment_id
  - Model Deployment no longer has parameter provisioning_state
  - Model Device no longer has parameter chip_sku
  - Model Device no longer has parameter device_id
  - Model Device no longer has parameter last_available_os_version
  - Model Device no longer has parameter last_installed_os_version
  - Model Device no longer has parameter last_os_update_utc
  - Model Device no longer has parameter last_update_request_utc
  - Model Device no longer has parameter provisioning_state
  - Model DeviceGroup no longer has parameter allow_crash_dumps_collection
  - Model DeviceGroup no longer has parameter description
  - Model DeviceGroup no longer has parameter has_deployment
  - Model DeviceGroup no longer has parameter os_feed_type
  - Model DeviceGroup no longer has parameter provisioning_state
  - Model DeviceGroup no longer has parameter regional_data_boundary
  - Model DeviceGroup no longer has parameter update_policy
  - Model DeviceGroupUpdate no longer has parameter allow_crash_dumps_collection
  - Model DeviceGroupUpdate no longer has parameter description
  - Model DeviceGroupUpdate no longer has parameter os_feed_type
  - Model DeviceGroupUpdate no longer has parameter regional_data_boundary
  - Model DeviceGroupUpdate no longer has parameter update_policy
  - Model DeviceUpdate no longer has parameter device_group_id
  - Model Image no longer has parameter component_id
  - Model Image no longer has parameter description
  - Model Image no longer has parameter image
  - Model Image no longer has parameter image_id
  - Model Image no longer has parameter image_name
  - Model Image no longer has parameter image_type
  - Model Image no longer has parameter provisioning_state
  - Model Image no longer has parameter regional_data_boundary
  - Model Image no longer has parameter uri
  - Model Product no longer has parameter description
  - Model Product no longer has parameter provisioning_state
  - Model ProductUpdate no longer has parameter description

## 1.0.0b1 (2023-07-21)

* Initial Release
