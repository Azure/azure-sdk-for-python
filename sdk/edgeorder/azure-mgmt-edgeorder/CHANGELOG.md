# Release History

## 3.0.0b1 (2026-07-06)

### Features Added

  - Client `EdgeOrderManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `EdgeOrderManagementClient` added method `send_request`
  - Client `EdgeOrderManagementClient` added operation group `operations`
  - Client `EdgeOrderManagementClient` added operation group `addresses`
  - Client `EdgeOrderManagementClient` added operation group `order_items`
  - Client `EdgeOrderManagementClient` added operation group `orders`
  - Client `EdgeOrderManagementClient` added operation group `products_and_configurations`
  - Model `AddressProperties` added property `address_classification`
  - Model `AddressProperties` added property `provisioning_state`
  - Model `AddressResource` added property `properties`
  - Model `AddressUpdateParameter` added property `properties`
  - Enum `AvailabilityStage` added member `DISCOVERABLE`
  - Model `BasicInformation` added property `fulfilled_by`
  - Model `BillingMeterDetails` added property `term_type_details`
  - Model `CommonProperties` added property `fulfilled_by`
  - Model `ConfigurationProperties` added property `provisioning_support`
  - Model `ConfigurationProperties` added property `child_configuration_types`
  - Model `ConfigurationProperties` added property `grouped_child_configurations`
  - Model `ConfigurationProperties` added property `supported_term_commitment_durations`
  - Model `ConfigurationProperties` added property `fulfilled_by`
  - Model `ConfigurationsRequest` added property `configuration_filter`
  - Model `DeviceDetails` added property `display_serial_number`
  - Model `DeviceDetails` added property `provisioning_support`
  - Model `DeviceDetails` added property `provisioning_details`
  - Model `HierarchyInformation` added property `configuration_id_display_name`
  - Enum `LinkType` added member `DISCOVERABLE`
  - Model `OrderItemDetails` added property `order_item_mode`
  - Model `OrderItemDetails` added property `site_details`
  - Model `OrderItemResource` added property `properties`
  - Model `OrderItemResource` added property `identity`
  - Enum `OrderItemType` added member `EXTERNAL`
  - Model `OrderItemUpdateParameter` added property `properties`
  - Model `OrderItemUpdateParameter` added property `identity`
  - Model `OrderResource` added property `properties`
  - Model `Preferences` added property `term_commitment_preferences`
  - Model `ProductDetails` added property `identification_type`
  - Model `ProductDetails` added property `parent_device_details`
  - Model `ProductDetails` added property `parent_provisioning_details`
  - Model `ProductDetails` added property `opt_in_additional_configurations`
  - Model `ProductDetails` added property `child_configuration_device_details`
  - Model `ProductDetails` added property `term_commitment_information`
  - Model `ProductFamilyProperties` added property `fulfilled_by`
  - Model `ProductLineProperties` added property `fulfilled_by`
  - Model `ProductProperties` added property `fulfilled_by`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `ResourceIdentity` added property `user_assigned_identities`
  - Enum `StageName` added member `READY_TO_SETUP`
  - Model `TrackedResource` added property `system_data`
  - Added model `AdditionalConfiguration`
  - Added enum `AddressClassification`
  - Added model `AddressUpdateProperties`
  - Added enum `AutoProvisioningStatus`
  - Added model `CategoryInformation`
  - Added model `ChildConfiguration`
  - Added model `ChildConfigurationFilter`
  - Added model `ChildConfigurationProperties`
  - Added enum `ChildConfigurationType`
  - Added model `ConfigurationDeviceDetails`
  - Added model `ConfigurationFilter`
  - Added model `DevicePresenceVerificationDetails`
  - Added enum `DevicePresenceVerificationStatus`
  - Added enum `FulfillmentType`
  - Added model `GroupedChildConfigurations`
  - Added enum `IdentificationType`
  - Added model `OrderItemDetailsUpdateParameter`
  - Added model `OrderItemProperties`
  - Added model `OrderItemUpdateProperties`
  - Added enum `OrderMode`
  - Added model `OrderProperties`
  - Added model `ProductDetailsUpdateParameter`
  - Added model `ProvisioningDetails`
  - Added enum `ProvisioningState`
  - Added enum `ProvisioningSupport`
  - Added model `SiteDetails`
  - Added model `TermCommitmentInformation`
  - Added model `TermCommitmentPreferences`
  - Added enum `TermCommitmentType`
  - Added model `TermTypeDetails`
  - Added model `UserAssignedIdentity`

### Breaking Changes

  - Deleted or renamed client method `EdgeOrderManagementClient.begin_create_address`
  - Deleted or renamed client method `EdgeOrderManagementClient.begin_create_order_item`
  - Deleted or renamed client method `EdgeOrderManagementClient.begin_delete_address_by_name`
  - Deleted or renamed client method `EdgeOrderManagementClient.begin_delete_order_item_by_name`
  - Deleted or renamed client method `EdgeOrderManagementClient.begin_return_order_item`
  - Deleted or renamed client method `EdgeOrderManagementClient.begin_update_address`
  - Deleted or renamed client method `EdgeOrderManagementClient.begin_update_order_item`
  - Deleted or renamed client method `EdgeOrderManagementClient.cancel_order_item`
  - Deleted or renamed client method `EdgeOrderManagementClient.get_address_by_name`
  - Deleted or renamed client method `EdgeOrderManagementClient.get_order_by_name`
  - Deleted or renamed client method `EdgeOrderManagementClient.get_order_item_by_name`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_addresses_at_resource_group_level`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_addresses_at_subscription_level`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_configurations`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_operations`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_order_at_resource_group_level`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_order_at_subscription_level`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_order_items_at_resource_group_level`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_order_items_at_subscription_level`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_product_families`
  - Deleted or renamed client method `EdgeOrderManagementClient.list_product_families_metadata`
  - Model `AddressResource` deleted or renamed its instance variable `shipping_address`
  - Model `AddressResource` deleted or renamed its instance variable `contact_details`
  - Model `AddressResource` deleted or renamed its instance variable `address_validation_status`
  - Model `AddressUpdateParameter` deleted or renamed its instance variable `shipping_address`
  - Model `AddressUpdateParameter` deleted or renamed its instance variable `contact_details`
  - Model `Configuration` deleted or renamed its instance variable `display_name`
  - Model `Configuration` deleted or renamed its instance variable `description`
  - Model `Configuration` deleted or renamed its instance variable `image_information`
  - Model `Configuration` deleted or renamed its instance variable `cost_information`
  - Model `Configuration` deleted or renamed its instance variable `availability_information`
  - Model `Configuration` deleted or renamed its instance variable `hierarchy_information`
  - Model `Configuration` deleted or renamed its instance variable `filterable_properties`
  - Model `Configuration` deleted or renamed its instance variable `specifications`
  - Model `Configuration` deleted or renamed its instance variable `dimensions`
  - Model `ConfigurationsRequest` deleted or renamed its instance variable `configuration_filters`
  - Model `OrderItemDetails` deleted or renamed its instance variable `management_rp_details`
  - Model `OrderItemResource` deleted or renamed its instance variable `order_item_details`
  - Model `OrderItemResource` deleted or renamed its instance variable `address_details`
  - Model `OrderItemResource` deleted or renamed its instance variable `start_time`
  - Model `OrderItemResource` deleted or renamed its instance variable `order_id`
  - Model `OrderItemUpdateParameter` deleted or renamed its instance variable `forward_address`
  - Model `OrderItemUpdateParameter` deleted or renamed its instance variable `preferences`
  - Model `OrderItemUpdateParameter` deleted or renamed its instance variable `notification_email_list`
  - Model `OrderResource` deleted or renamed its instance variable `order_item_ids`
  - Model `OrderResource` deleted or renamed its instance variable `current_stage`
  - Model `OrderResource` deleted or renamed its instance variable `order_stage_history`
  - Model `Product` deleted or renamed its instance variable `display_name`
  - Model `Product` deleted or renamed its instance variable `description`
  - Model `Product` deleted or renamed its instance variable `image_information`
  - Model `Product` deleted or renamed its instance variable `cost_information`
  - Model `Product` deleted or renamed its instance variable `availability_information`
  - Model `Product` deleted or renamed its instance variable `hierarchy_information`
  - Model `Product` deleted or renamed its instance variable `filterable_properties`
  - Model `Product` deleted or renamed its instance variable `configurations`
  - Model `ProductDetails` deleted or renamed its instance variable `count`
  - Model `ProductDetails` deleted or renamed its instance variable `device_details`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `display_name`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `description`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `image_information`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `cost_information`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `availability_information`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `hierarchy_information`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `filterable_properties`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `product_lines`
  - Model `ProductFamiliesMetadataDetails` deleted or renamed its instance variable `resource_provider_details`
  - Model `ProductFamily` deleted or renamed its instance variable `display_name`
  - Model `ProductFamily` deleted or renamed its instance variable `description`
  - Model `ProductFamily` deleted or renamed its instance variable `image_information`
  - Model `ProductFamily` deleted or renamed its instance variable `cost_information`
  - Model `ProductFamily` deleted or renamed its instance variable `availability_information`
  - Model `ProductFamily` deleted or renamed its instance variable `hierarchy_information`
  - Model `ProductFamily` deleted or renamed its instance variable `filterable_properties`
  - Model `ProductFamily` deleted or renamed its instance variable `product_lines`
  - Model `ProductFamily` deleted or renamed its instance variable `resource_provider_details`
  - Model `ProductLine` deleted or renamed its instance variable `display_name`
  - Model `ProductLine` deleted or renamed its instance variable `description`
  - Model `ProductLine` deleted or renamed its instance variable `image_information`
  - Model `ProductLine` deleted or renamed its instance variable `cost_information`
  - Model `ProductLine` deleted or renamed its instance variable `availability_information`
  - Model `ProductLine` deleted or renamed its instance variable `hierarchy_information`
  - Model `ProductLine` deleted or renamed its instance variable `filterable_properties`
  - Model `ProductLine` deleted or renamed its instance variable `products`
  - Deleted or renamed model `AddressResourceList`
  - Deleted or renamed model `ConfigurationFilters`
  - Deleted or renamed model `Configurations`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `OrderItemResourceList`
  - Deleted or renamed model `OrderResourceList`
  - Deleted or renamed model `ProductFamilies`
  - Deleted or renamed model `ProductFamiliesMetadata`
  - Deleted or renamed model `ShippingDetails`
  - Deleted or renamed model `EdgeOrderManagementClientOperationsMixin`

## 2.0.0 (2024-10-30)

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 2.0.0b1 (2023-02-13)

### Features Added

  - Added operation group AddressesOperations
  - Added operation group Operations
  - Added operation group OrderItemsOperations
  - Added operation group OrdersOperations
  - Added operation group ProductsAndConfigurationsOperations
  - Model BasicInformation has a new parameter fulfilled_by
  - Model CommonProperties has a new parameter fulfilled_by
  - Model Configuration has a new parameter child_configuration_types
  - Model Configuration has a new parameter fulfilled_by
  - Model Configuration has a new parameter grouped_child_configurations
  - Model ConfigurationProperties has a new parameter child_configuration_types
  - Model ConfigurationProperties has a new parameter fulfilled_by
  - Model ConfigurationProperties has a new parameter grouped_child_configurations
  - Model ConfigurationsRequest has a new parameter configuration_filter
  - Model OrderItemDetails has a new parameter order_item_mode
  - Model OrderResource has a new parameter order_mode
  - Model Product has a new parameter fulfilled_by
  - Model ProductDetails has a new parameter child_configuration_device_details
  - Model ProductDetails has a new parameter identification_type
  - Model ProductDetails has a new parameter opt_in_additional_configurations
  - Model ProductDetails has a new parameter parent_device_details
  - Model ProductFamiliesMetadataDetails has a new parameter fulfilled_by
  - Model ProductFamily has a new parameter fulfilled_by
  - Model ProductFamilyProperties has a new parameter fulfilled_by
  - Model ProductLine has a new parameter fulfilled_by
  - Model ProductLineProperties has a new parameter fulfilled_by
  - Model ProductProperties has a new parameter fulfilled_by

### Breaking Changes

  - Model ConfigurationsRequest no longer has parameter configuration_filters
  - Model OrderItemDetails no longer has parameter management_rp_details
  - Model ProductDetails no longer has parameter count
  - Model ProductDetails no longer has parameter device_details

## 1.0.0 (2021-12-23)

**Features**

  - Model OrderItemDetails has a new parameter management_rp_details_list
  - Model ReturnOrderItemDetails has a new parameter shipping_box_required
  - Model ReturnOrderItemDetails has a new parameter service_tag
  - Model AddressResource has a new parameter address_validation_status
  - Model DeviceDetails has a new parameter management_resource_tenant_id
  - Model ProductFamily has a new parameter resource_provider_details
  - Model ProductFamilyProperties has a new parameter resource_provider_details
  - Model ProductFamiliesMetadataDetails has a new parameter resource_provider_details
  - Model ProductDetails has a new parameter product_double_encryption_status
  - Model AddressProperties has a new parameter address_validation_status

**Breaking changes**

  - Operation EdgeOrderManagementClientOperationsMixin.list_order_items_at_subscription_level has a new signature

## 1.0.0b1 (2021-07-27)

* Initial Release
