# Release History

## 2.1.0 (2023-10-23)

### Features Added

  - Added operation group CreationSupportedOperations
  - Added operation group MonitoredSubscriptionsOperations
  - Model DatadogOrganizationProperties has a new parameter cspm
  - Model MonitorUpdateProperties has a new parameter cspm
  - Model MonitoringTagRulesProperties has a new parameter automuting

## 2.1.0b1 (2022-11-02)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 2.0.0 (2021-05-26)

**Features**

  - Model DatadogMonitorResourceUpdateParameters has a new parameter sku
  - Added operation MonitorsOperations.begin_update

**Breaking changes**

  - Removed operation MonitorsOperations.update

## 1.0.0 (2021-03-22)

**Features**

  - Model DatadogAgreementResource has a new parameter system_data
  - Model MonitoringTagRules has a new parameter system_data
  - Model DatadogSingleSignOnResource has a new parameter system_data
  - Model DatadogMonitorResource has a new parameter system_data

## 1.0.0b3 (2021-03-02)

**Features**

  - Model DatadogOrganizationProperties has a new parameter application_key
  - Model DatadogOrganizationProperties has a new parameter redirect_uri
  - Model DatadogOrganizationProperties has a new parameter api_key
  - Model MonitoringTagRulesProperties has a new parameter provisioning_state
  - Model DatadogSingleSignOnProperties has a new parameter provisioning_state
  - Added operation MarketplaceAgreementsOperations.create_or_update
  - Added operation MonitorsOperations.list_monitored_resources
  - Added operation MonitorsOperations.refresh_set_password_link
  - Added operation MonitorsOperations.get_default_key
  - Added operation MonitorsOperations.set_default_key
  - Added operation MonitorsOperations.list_api_keys
  - Added operation MonitorsOperations.list_hosts
  - Added operation MonitorsOperations.list_linked_resources

**Breaking changes**

  - Removed operation MarketplaceAgreementsOperations.create
  - Removed operation group RefreshSetPasswordOperations
  - Removed operation group HostsOperations
  - Removed operation group ApiKeysOperations
  - Removed operation group MonitoredResourcesOperations
  - Removed operation group LinkedResourcesOperations

## 1.0.0b2 (2020-11-17)

**Features**

  - Added operation group MarketplaceAgreementsOperations

## 1.0.0b1 (2020-10-14)

* Initial Release
