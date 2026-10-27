// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

targetScope = 'subscription'

import { SharedIdentities as SharedIdentityDictionary } from './shared-identities.bicep'

@sealed()
type RoleAssignmentMetadata = {
  roleAssignmentId: string
  principalId: string
  roleDefinitionId: string
  scope: string
  // Empty strings mean these optional properties are omitted from the assignment.
  condition: string
  conditionVersion: string
}

@sealed()
type BootstrapRoleAssignments = {
  project: RoleAssignmentMetadata[]
  pipeline: RoleAssignmentMetadata
}

@description('Only the explicitly approved NEW identity resource group may be bootstrapped. The parent must reject any pre-existing group except its own exact recorded state.')
@allowed([
  'rg-azsdk-sample-identities-wus3'
])
param identityResourceGroup string

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

@description('Non-secret, 32-character ownership token from the parent bootstrap state; preserve it on an exact-state retry.')
@minLength(32)
@maxLength(32)
param ownerToken string

@description('Service principal OBJECT GUID, not application/client ID. The parent must validate a nonzero GUID and verify the approved principal belongs to the deployment tenant.')
@minLength(36)
@maxLength(36)
param pipelinePrincipalId string

// The parent must bind and verify the explicitly approved subscription and tenant.
// Bicep resource declarations are upserts, not create-only ownership checks.
var locationSuffix = 'wus3'

resource identityResources 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: identityResourceGroup
  location: location
  tags: {
    purpose: 'azsdk-sample-identities'
    'sample-ci-owner': ownerToken
    'sample-ci-retention': 'permanent'
  }
}

module sharedIdentities './shared-identities.bicep' = {
  name: 'shared-identities-${uniqueString(identityResources.id, namePrefix, locationSuffix)}'
  scope: identityResources
  params: {
    namePrefix: namePrefix
    location: location
    locationSuffix: locationSuffix
    ownerToken: ownerToken
  }
}

var approvedRoleDefinitionIds = {
  foundryUser: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')
  storageBlobDataContributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  storageBlobDataOwner: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b')
  cosmosDbOperator: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '230815da-be43-4aae-9cb4-875f7bd000aa')
  searchServiceContributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
  searchIndexDataContributor: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
}

// Pinned blob-storage-container-role-assignments.bicep at fbbe89b701c758e871922adaceea0ac0e4dae40f:
// remove ONLY the explicitly approved workspace-prefix conjunct, preserving the rest.
// Only these three actions require the suffix; other Owner permissions remain allowed.
var storageBlobOwnerCondition = '((!(ActionMatches{\'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read\'})  AND  !(ActionMatches{\'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/filter/action\'}) AND  !(ActionMatches{\'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write\'}) ) OR (@Resource[Microsoft.Storage/storageAccounts/blobServices/containers:name] StringLikeIgnoreCase \'*-azureml-agent\'))'

var projectServiceGrants = [
  {
    roleDefinitionId: approvedRoleDefinitionIds.foundryUser
    condition: ''
  }
  {
    roleDefinitionId: approvedRoleDefinitionIds.storageBlobDataContributor
    condition: ''
  }
  {
    roleDefinitionId: approvedRoleDefinitionIds.storageBlobDataOwner
    condition: storageBlobOwnerCondition
  }
  {
    roleDefinitionId: approvedRoleDefinitionIds.cosmosDbOperator
    condition: ''
  }
  {
    roleDefinitionId: approvedRoleDefinitionIds.searchServiceContributor
    condition: ''
  }
  {
    roleDefinitionId: approvedRoleDefinitionIds.searchIndexDataContributor
    condition: ''
  }
]

// A new MI's principalId is runtime-only and cannot seed a Bicep resource name.
// Use its stable principal resource ID with scope, role, and exact condition instead.
// The parent must reject replacement identities or stale subscription assignments.
var projectIdentityResourceId = resourceId(
  subscription().subscriptionId,
  identityResourceGroup,
  'Microsoft.ManagedIdentity/userAssignedIdentities',
  '${namePrefix}-project-${locationSuffix}'
)

// These six fixed service roles do not grant ARM IAM-administration permissions.
resource projectRoleAssignments 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for grant in projectServiceGrants: {
  name: guid(
    toLower(projectIdentityResourceId),
    toLower(subscription().id),
    toLower(grant.roleDefinitionId),
    grant.condition
  )
  scope: subscription()
  properties: {
    principalId: sharedIdentities.outputs.identities.project.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: grant.roleDefinitionId
    condition: empty(grant.condition) ? null : grant.condition
    conditionVersion: empty(grant.condition) ? null : '2.0'
  }
}]

// Add only Foundry User. Never create or alter Contributor or an IAM-admin grant.
resource pipelineFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    toLower(pipelinePrincipalId),
    toLower(subscription().id),
    toLower(approvedRoleDefinitionIds.foundryUser),
    ''
  )
  scope: subscription()
  properties: {
    principalId: pipelinePrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: approvedRoleDefinitionIds.foundryUser
  }
}

output identityResourceGroupId string = identityResources.id
output identities SharedIdentityDictionary = sharedIdentities.outputs.identities
output roleDefinitionIds object = approvedRoleDefinitionIds
output blobOwnerCondition string = storageBlobOwnerCondition
output roleAssignments BootstrapRoleAssignments = {
  project: map(projectServiceGrants, grant => {
    roleAssignmentId: subscriptionResourceId('Microsoft.Authorization/roleAssignments', guid(
      toLower(projectIdentityResourceId),
      toLower(subscription().id),
      toLower(grant.roleDefinitionId),
      grant.condition
    ))
    principalId: sharedIdentities.outputs.identities.project.principalId
    roleDefinitionId: grant.roleDefinitionId
    scope: subscription().id
    condition: grant.condition
    conditionVersion: empty(grant.condition) ? '' : '2.0'
  })
  pipeline: {
    roleAssignmentId: pipelineFoundryUser.id
    principalId: pipelinePrincipalId
    roleDefinitionId: approvedRoleDefinitionIds.foundryUser
    scope: subscription().id
    condition: ''
    conditionVersion: ''
  }
}