# Release History

## 2.0.0 (2023-11-20)

### Features Added

  - Added operation NetworkFunctionsOperations.begin_execute_request
  - Added operation group ArtifactManifestsOperations
  - Added operation group ArtifactStoresOperations
  - Added operation group ComponentsOperations
  - Added operation group ConfigurationGroupSchemasOperations
  - Added operation group ConfigurationGroupValuesOperations
  - Added operation group NetworkFunctionDefinitionGroupsOperations
  - Added operation group NetworkFunctionDefinitionVersionsOperations
  - Added operation group NetworkServiceDesignGroupsOperations
  - Added operation group NetworkServiceDesignVersionsOperations
  - Added operation group ProxyArtifactOperations
  - Added operation group PublishersOperations
  - Added operation group SiteNetworkServicesOperations
  - Added operation group SitesOperations
  - Model NetworkFunction has a new parameter identity
  - Model NetworkFunction has a new parameter properties
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model NetworkFunction no longer has parameter device
  - Model NetworkFunction no longer has parameter managed_application
  - Model NetworkFunction no longer has parameter managed_application_parameters
  - Model NetworkFunction no longer has parameter network_function_container_configurations
  - Model NetworkFunction no longer has parameter network_function_user_configurations
  - Model NetworkFunction no longer has parameter provisioning_state
  - Model NetworkFunction no longer has parameter service_key
  - Model NetworkFunction no longer has parameter sku_name
  - Model NetworkFunction no longer has parameter sku_type
  - Model NetworkFunction no longer has parameter vendor_name
  - Model NetworkFunction no longer has parameter vendor_provisioning_state
  - Removed operation group DevicesOperations
  - Removed operation group NetworkFunctionVendorSkusOperations
  - Removed operation group NetworkFunctionVendorsOperations
  - Removed operation group RoleInstancesOperations
  - Removed operation group VendorNetworkFunctionsOperations
  - Removed operation group VendorSkuPreviewOperations
  - Removed operation group VendorSkusOperations
  - Removed operation group VendorsOperations

## 2.0.0b1 (2022-11-18)

### Features Added

  - Added operation NetworkFunctionsOperations.begin_execute_request
  - Added operation VendorSkusOperations.list_credential
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin

### Breaking Changes

  - Model Device no longer has parameter azure_stack_edge
  - Model DevicePropertiesFormat no longer has parameter azure_stack_edge

## 1.0.0 (2021-07-21)

**Features**

  - Model VendorNetworkFunction has a new parameter system_data
  - Model PreviewSubscription has a new parameter provisioning_state
  - Model PreviewSubscription has a new parameter system_data
  - Model Vendor has a new parameter system_data
  - Model Device has a new parameter system_data
  - Model RoleInstance has a new parameter provisioning_state
  - Model RoleInstance has a new parameter system_data
  - Model NetworkFunction has a new parameter network_function_container_configurations
  - Model NetworkFunction has a new parameter system_data
  - Model VendorSku has a new parameter network_function_type
  - Model VendorSku has a new parameter system_data

## 1.0.0b1 (2021-04-20)

* Initial Release
