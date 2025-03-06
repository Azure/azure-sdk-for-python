param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object
var managedIdentityId = userassignedidentity_foo.id
var managedIdentityPrincipalId = userassignedidentity_foo.properties.principalId
var managedIdentityClientId = userassignedidentity_foo.properties.clientId

resource userassignedidentity_foo 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  name: 'foo'
  location: 'westus'
  tags: {
    key: 'value'
  }
}



