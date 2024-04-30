# Release History

## 3.1.0b1 (2024-03-18)

### Features Added

  - Added operation ConfigurationsOperations.analysis
  - Model NginxCertificateProperties has a new parameter certificate_error
  - Model NginxCertificateProperties has a new parameter key_vault_secret_created
  - Model NginxCertificateProperties has a new parameter key_vault_secret_version
  - Model NginxCertificateProperties has a new parameter sha1_thumbprint
  - Model NginxDeploymentProperties has a new parameter auto_upgrade_profile
  - Model NginxDeploymentScalingProperties has a new parameter profiles
  - Model NginxDeploymentUpdateProperties has a new parameter auto_upgrade_profile

## 3.0.0 (2023-11-20)

### Features Added

  - Model NginxConfigurationPackage has a new parameter protected_files
  - Model NginxDeploymentProperties has a new parameter scaling_properties
  - Model NginxDeploymentProperties has a new parameter user_profile
  - Model NginxDeploymentUpdateProperties has a new parameter scaling_properties
  - Model NginxDeploymentUpdateProperties has a new parameter user_profile

### Breaking Changes

  - Model NginxCertificate no longer has parameter tags
  - Model NginxConfiguration no longer has parameter tags

## 2.1.0 (2023-03-14)

### Other Changes

  - Regular update

## 2.1.0b1 (2022-12-29)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 2.0.0 (2022-10-18)

### Features Added

  - Added operation CertificatesOperations.begin_create_or_update
  - Added operation DeploymentsOperations.begin_create_or_update

### Breaking Changes

  - Removed operation CertificatesOperations.begin_create
  - Removed operation DeploymentsOperations.begin_create

## 1.1.0 (2022-09-20)

### Features Added

  - Model NginxConfigurationProperties has a new parameter protected_files

## 1.0.0 (2022-08-26)

### Features Added

  - Model NginxDeploymentProperties has a new parameter logging
  - Model NginxDeploymentUpdateProperties has a new parameter logging

## 1.0.0b1 (2022-06-13)

* Initial Release
