### Settings

```yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/loadtestservice/data-plane/Microsoft.LoadTestService/stable/2022-11-01/loadtestservice.json
output-folder: ../
namespace: azure.developer.loadtesting
package-name: azure-developer-loadtesting
license-header: MICROSOFT_MIT_NO_VERSION
title: LoadTestingClient
package-version: 1.0.0
package-mode: dataplane
package-pprint-name: Azure Developer LoadTesting
security: AADToken
security-scopes: https://cnt-prod.loadtesting.azure.com/.default
directive:
  - from: swagger-document
    where: $["paths"]["/tests/{testId}/files/{fileName}"].put
    transform: $["operationId"] = "LoadTestAdministration_BeginUploadTestFile";
  - from: swagger-document
    where: $["paths"]["/test-runs/{testRunId}"].patch
    transform: $["operationId"] = "LoadTestRun_BeginTestRun";
    
  - from: swagger-document
    where: '$.paths.*[?(@.tags=="Test")]'
    transform: >
     $["operationId"] = $["operationId"].replace("LoadTestAdministration_", "Administration_");
  - from: swagger-document
    where: '$.paths.*[?(@.tags=="TestRun")]'
    transform: >
     $["operationId"] = $["operationId"].replace("LoadTestRun_", "TestRun_");
```
