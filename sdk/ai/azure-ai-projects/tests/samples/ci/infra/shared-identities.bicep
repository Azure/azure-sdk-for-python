// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

targetScope = 'resourceGroup'

@export()
@sealed()
type IdentityMetadata = {
  resourceId: string
  principalId: string
  clientId: string
  tenantId: string
}

@export()
@sealed()
type SharedIdentities = {
  project: IdentityMetadata
  account: IdentityMetadata
  search: IdentityMetadata
  function: IdentityMetadata
}

@description('Explicitly approved prefix for the four permanent shared identities.')
@allowed([
  'mi-azsdk-sample'
])
param namePrefix string

@description('Explicitly approved Azure region; no region fallback is permitted.')
@allowed([
  'westus3'
])
param location string

@description('Reviewed name suffix for westus3, producing names ending in -wus3.')
@allowed([
  'wus3'
])
param locationSuffix string

@description('Non-secret, 32-character ownership token from the parent bootstrap state; not an authorization credential.')
@minLength(32)
@maxLength(32)
param ownerToken string

var identityPurposes = [
  'project'
  'account'
  'search'
  'function'
]

// No role assignments are made to the reserved account, search, or function identities.
resource managedIdentities 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = [for identityPurpose in identityPurposes: {
  name: '${namePrefix}-${identityPurpose}-${locationSuffix}'
  location: location
  tags: {
    purpose: 'azsdk-sample-identities'
    'sample-ci-owner': ownerToken
    'sample-ci-retention': 'permanent'
    'sample-ci-identity': identityPurpose
  }
}]

output identities SharedIdentities = {
  project: {
    resourceId: managedIdentities[0].id
    principalId: managedIdentities[0].properties.principalId
    clientId: managedIdentities[0].properties.clientId
    tenantId: managedIdentities[0].properties.tenantId
  }
  account: {
    resourceId: managedIdentities[1].id
    principalId: managedIdentities[1].properties.principalId
    clientId: managedIdentities[1].properties.clientId
    tenantId: managedIdentities[1].properties.tenantId
  }
  search: {
    resourceId: managedIdentities[2].id
    principalId: managedIdentities[2].properties.principalId
    clientId: managedIdentities[2].properties.clientId
    tenantId: managedIdentities[2].properties.tenantId
  }
  function: {
    resourceId: managedIdentities[3].id
    principalId: managedIdentities[3].properties.principalId
    clientId: managedIdentities[3].properties.clientId
    tenantId: managedIdentities[3].properties.tenantId
  }
}