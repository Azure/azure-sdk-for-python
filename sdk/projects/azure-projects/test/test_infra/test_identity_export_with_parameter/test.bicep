param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object
param testLocation string
var managedIdentityId = userassignedidentity.id
var managedIdentityPrincipalId = userassignedidentity.properties.principalId
var managedIdentityClientId = userassignedidentity.properties.clientId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  location: testLocation
  tags: azdTags
  name: defaultName
}



