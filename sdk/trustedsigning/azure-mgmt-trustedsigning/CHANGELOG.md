# Release History

## 1.0.0b2 (2025-04-15)

### Features Added

  - Model `Certificate` added property `enhanced_key_usage`
  - Added model `AccountSkuPatch`
  - Method `Certificate.__init__` has a new overload `def __init__(self: None, serial_number: Optional[str], enhanced_key_usage: Optional[str], subject_name: Optional[str], thumbprint: Optional[str], created_date: Optional[str], expiry_date: Optional[str], status: Optional[Union[str, _models.CertificateStatus]], revocation: Optional[_models.Revocation])`
  - Method `CertificateProfileProperties.__init__` has a new overload `def __init__(self: None, profile_type: Union[str, _models.ProfileType], identity_validation_id: str, include_street_address: Optional[bool], include_city: Optional[bool], include_state: Optional[bool], include_country: Optional[bool], include_postal_code: Optional[bool])`
  - Method `CodeSigningAccountPatchProperties.__init__` has a new overload `def __init__(self: None, sku: Optional[_models.AccountSkuPatch])`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, display: Optional[_models.OperationDisplay])`
  - Method `AccountSkuPatch.__init__` has a new overload `def __init__(self: None, name: Optional[Union[str, _models.SkuName]])`
  - Method `AccountSkuPatch.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`

### Breaking Changes

  - Model `CertificateProfileProperties` deleted or renamed its instance variable `common_name`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `organization`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `organization_unit`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `street_address`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `city`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `state`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `country`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `postal_code`
  - Model `CertificateProfileProperties` deleted or renamed its instance variable `enhanced_key_usage`

## 1.0.0b1 (2024-09-27)

### Other Changes

  - Initial version
