@description('Ledger Name')
@minLength(3)
@maxLength(24)
param ledgerName string = uniqueString(resourceGroup().id)
// resourceGroup().name is too long
// uniqueString is 13 characters long
// https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-functions-string#uniquestring

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@description('The location of the resource. By default, this is the same as the resource group.')
param location string = resourceGroup().location

var azureConfidentialLedgerUrl = 'https://${ledgerName}.confidential-ledger.azure.com'

resource ledgerName_resource 'Microsoft.ConfidentialLedger/ledgers@2022-05-13' = {
  name: ledgerName
  location: location
  properties: {
    ledgerType: 'Public'
    aadBasedSecurityPrincipals: [
      {
        principalId: testApplicationOid
        ledgerRoleName: 'Administrator'
      }
    ]
  }
}

output CONFIDENTIALLEDGER_ENDPOINT string = azureConfidentialLedgerUrl
output CONFIDENTIALLEDGER_ID string = ledgerName
