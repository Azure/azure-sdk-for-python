# Azure Purview for Python

``` yaml
input-file:
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/preview/2023-04-18-preview/linkConnections.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/preview/2022-03-01-preview/runNotebook.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/preview/2021-11-01-preview/kqlScripts.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/preview/2021-07-01-preview/symsSync.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/preview/2021-06-01-preview/sparkConfigurations.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/preview/2021-06-01-preview/entityTypes/SparkConfiguration.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/artifacts.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/bigDataPools.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/dataflows.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/datasets.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/gitintegration.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/integrationRuntimes.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/library.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/linkedServices.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/notebooks.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/pipelines.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/sparkJobDefinitions.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/sqlPools.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/sqlScripts.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/triggers.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/workspace.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/DataFlow.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/Dataset.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/LinkedService.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/Notebook.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/Pipeline.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/SparkJobDefinition.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/SqlScript.json
  - https://github.com/Azure/azure-rest-api-specs/blob/02e1bd495ad6215aacec5d636a5ef7ad6f20281e/specification/synapse/data-plane/Microsoft.Synapse/stable/2020-12-01/entityTypes/Trigger.json

payload-flattening-threshold: 1
output-folder: ../
package-name: azure-synapse-artifacts
namespace: azure.synapse.artifacts
license-header: MICROSOFT_MIT_NO_VERSION
package-version: 0.19.0
version-tolerant: false
package-pprint-name: Synapse Artifacts
security: AADToken
security-scopes: https://dev.azuresynapse.net/.default
modelerfour:
  lenient-model-deduplication: true
```
