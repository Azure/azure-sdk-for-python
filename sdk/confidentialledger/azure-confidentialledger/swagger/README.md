# Azure Confidential Ledger

> see https://aka.ms/autorest

### Settings

#### Tag: confidential-ledger
These settings apply only when `--tag=confidential-ledger` is specified on the command line.
```yaml $(tag) == 'confidential-ledger'
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/confidentialledger/data-plane/Microsoft.ConfidentialLedger/stable/2022-05-13/confidentialledger.json
output-folder: ../azure/confidentialledger
namespace: azure.confidentialledger
package-name: azure-confidentialledger
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
title: ConfidentialLedgerClient
version-tolerant: true
package-version: 1.0.0
python: true
```

#### Tag: identity-service
These settings apply only when `--tag=identity-service` is specified on the command line.
```yaml $(tag) == 'identity-service'
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/confidentialledger/data-plane/Microsoft.ConfidentialLedger/stable/2022-05-13/identityservice.json
output-folder: ../azure/acl_identity_service
namespace: azure.acl_identity_service
package-name: azure-acl-identity-service
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
title: ConfidentialLedgerIdentityServiceClient
version-tolerant: true
package-version: 1.0.0
python: true
```