param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object
var managedIdentityId = userassignedidentity_exists.id
var managedIdentityPrincipalId = userassignedidentity_exists.properties.principalId
var managedIdentityClientId = userassignedidentity_exists.properties.clientId

resource userassignedidentity_exists 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' existing = {
  name: 'exists'
}



