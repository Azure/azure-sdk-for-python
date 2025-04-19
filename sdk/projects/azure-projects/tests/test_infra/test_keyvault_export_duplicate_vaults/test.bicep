param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource configurationstore 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  name: defaultName
  sku: {
    name: 'Standard'
  }
  properties: {
    disableLocalAuth: true
    createMode: 'Default'
    dataPlaneProxy: {
      authenticationMode: 'Pass-through'
      privateLinkDelegation: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
  }
  location: location
  tags: azdTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource vault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    publicNetworkAccess: 'Enabled'
    tenantId: tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
  name: defaultName
  location: location
  tags: azdTags
}

output AZURE_KEYVAULT_ID_R1 string = vault.id
output AZURE_KEYVAULT_ID_R2 string = vault.id
output AZURE_KEYVAULT_NAME_R1 string = vault.name
output AZURE_KEYVAULT_NAME_R2 string = vault.name
output AZURE_KEYVAULT_RESOURCE_GROUP_R1 string = resourceGroup().name
output AZURE_KEYVAULT_RESOURCE_GROUP_R2 string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT_R1 string = vault.properties.vaultUri
output AZURE_KEYVAULT_ENDPOINT_R2 string = vault.properties.vaultUri


resource keyvalue_azureappconfigid 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_ID'
  properties: {
    value: configurationstore.id
  }
}



resource keyvalue_azureappconfigname 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_NAME'
  properties: {
    value: configurationstore.name
  }
}



resource keyvalue_azureappconfigresourcegroup 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_RESOURCE_GROUP'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureappconfigendpoint 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_ENDPOINT'
  properties: {
    value: configurationstore.properties.endpoint
  }
}



resource keyvalue_azurekeyvaultidr1 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_ID_R1'
  properties: {
    value: vault.id
  }
}



resource keyvalue_azurekeyvaultidr2 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_ID_R2'
  properties: {
    value: vault.id
  }
}



resource keyvalue_azurekeyvaultnamer1 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_NAME_R1'
  properties: {
    value: vault.name
  }
}



resource keyvalue_azurekeyvaultnamer2 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_NAME_R2'
  properties: {
    value: vault.name
  }
}



resource keyvalue_azurekeyvaultresourcegroupr1 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_RESOURCE_GROUP_R1'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azurekeyvaultresourcegroupr2 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_RESOURCE_GROUP_R2'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azurekeyvaultendpointr1 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_ENDPOINT_R1'
  properties: {
    value: vault.properties.vaultUri
  }
}



resource keyvalue_azurekeyvaultendpointr2 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_KEYVAULT_ENDPOINT_R2'
  properties: {
    value: vault.properties.vaultUri
  }
}



resource roleassignment_gxaeyfznpvgorjrkpllp 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, defaultName, 'ServicePrincipal', 'App Configuration Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '516239f1-63e1-4d78-a4de-a74fb236a071'
    )

  }
  scope: configurationstore
}



resource roleassignment_unxsuzdqhucrcsmcfuyc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, defaultName, 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: configurationstore
}



resource roleassignment_gcbdbuudnabzzeifflkj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', environmentName, defaultName, 'ServicePrincipal', 'Key Vault Administrator')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault
}



resource roleassignment_nqvjjhotidgzatrnakyo 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', environmentName, defaultName, 'User', 'Key Vault Administrator')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault
}



resource roleassignment_kvjoxlocbytxyhtrwdln 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftResourcesresourceGroups', environmentName, defaultName, 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: resourceGroup()
}



