# Azure Confidential Ledger

> see https://aka.ms/autorest

### Settings

#### Tag: package-2022-20-04-preview-ledger
These settings apply only when `--tag=package-2022-20-04-preview-ledger` is specified on the command line.
```yaml $(tag) == 'package-2022-20-04-preview-ledger'
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/confidentialledger/data-plane/Microsoft.ConfidentialLedger/preview/2022-20-04-preview/confidentialledger.json
output-folder: ../azure/confidentialledger/_generated/_generated_ledger/v2022_20_04_preview
namespace: azure.confidentialledger
package-name: azure-confidential-ledger
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
title: ConfidentialLedgerClient
version-tolerant: true
package-version: 1.0.0b2
security: AADToken
security-scopes: https://confidential-ledger.azure.com/.default
```