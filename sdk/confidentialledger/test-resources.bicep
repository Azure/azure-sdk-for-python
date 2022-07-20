@description('Ledger Name')
@minLength(3)
@maxLength(24)
param ledgerName string = 'pysdkci-${uniqueString(resourceGroup().id)}'
// resourceGroup().name is too long
// uniqueString is 13 characters long
// https://docs.microsoft.com/en-us/azure/azure-resource-manager/bicep/bicep-functions-string#uniquestring
// Prepend a string to easy identification + ledger name must start with a letter.

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@description('The location of the resource. Currently, not all regions are supported.')
param location string = 'eastus'
// Explicitly set a region due to regional restrictions e.g. ACL is not currently available in westus

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
