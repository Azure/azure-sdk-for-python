# Release History

## 8.0.0b2 (2026-04-20)

### Features Added

  - Model `Identity` added property `properties`
  - Model `IdentityUpdate` added property `properties`
  - Added model `AssignmentRestrictions`
  - Added model `ClaimsMatchingExpression`
  - Added model `CloudError`
  - Added model `ExtensionResource`
  - Added enum `IsolationScope`
  - Added model `UserAssignedIdentityProperties`

### Breaking Changes

  - Deleted or renamed client `ManagedServiceIdentityClient`
  - Model `Identity` deleted or renamed its instance variable `tenant_id`
  - Model `Identity` deleted or renamed its instance variable `principal_id`
  - Model `Identity` deleted or renamed its instance variable `client_id`
  - Model `IdentityUpdate` deleted or renamed its instance variable `tenant_id`
  - Model `IdentityUpdate` deleted or renamed its instance variable `principal_id`
  - Model `IdentityUpdate` deleted or renamed its instance variable `client_id`
  - Method `FederatedIdentityCredentialsOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`

## 1.0.0b1 (1970-01-01)

### Other Changes

  - Initial version