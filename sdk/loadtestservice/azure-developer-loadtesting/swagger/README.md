### Settings

```yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/loadtest_stableapis/specification/loadtestservice/data-plane/Microsoft.LoadTestService/stable/2022-11-01/loadtestservice.json
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
      where: $["paths"]["/tests/{testId}"].patch
      transform: $["operationId"] = "Test_CreateOrUpdateLoadTest";
    - from: swagger-document 
      where: $["paths"]["/tests/{testId}"].delete
      transform: $["operationId"] = "Test_DeleteLoadTest";
    - from: swagger-document 
      where: $["paths"]["/tests/{testId}"].get
      transform: $["operationId"] = "Test_GetLoadTest";
    - from: swagger-document 
      where: $["paths"]["/tests"].get
      transform: $["operationId"] = "Test_ListLoadTests";
    - from: swagger-document 
      where: $["paths"]["/tests/{testId}/files/{fileId}"].put
      transform: $["operationId"] = "Test_UploadTestFile";
    - from: swagger-document 
      where: $["paths"]["/tests/{testId}/files/{fileId}"].get
      transform: $["operationId"] = "Test_GetTestFile";
    - from: swagger-document 
      where: $["paths"]["/tests/{testId}/files/{fileId}"].delete
      transform: $["operationId"] = "Test_DeleteTestFile";
    - from: swagger-document 
      where: $["paths"]["/tests/{testId}/files"].get
      transform: $["operationId"] = "Test_ListTestFiles";
    - from: swagger-document 
      where: $["paths"]["/test-runs/{testRunId}"].delete
      transform: $["operationId"] = "TestRun_DeleteTestRun";
    - from: swagger-document 
      where: $["paths"]["/test-runs/{testRunId}"].patch
      transform: $["operationId"] = "TestRun_CreateOrUpdateTestRun";
    - from: swagger-document 
      where: $["paths"]["/test-runs/{testRunId}"].get
      transform: $["operationId"] = "TestRun_GetTestRun";
    - from: swagger-document 
      where: $["paths"]["/test-runs/{testRunId}/files/{fileId}"].get
      transform: $["operationId"] = "TestRun_GetTestRunFile";
    - from: swagger-document 
      where: $["paths"]["/test-runs"].get
      transform: $["operationId"] = "TestRun_ListTestRuns";
    - from: swagger-document 
      where: $["paths"]["/test-runs/{testRunId}:stop"].post
      transform: $["operationId"] = "TestRun_StopTestRun";
    

    - from: swagger-document
      where: '$.paths.*[?(@.tags=="Test")]'
      transform: $["operationId"] = $["operationId"].replace("Test_", "LoadTestAdministration_");
    - from: swagger-document
      where: '$.paths.*[?(@.tags=="TestRun")]'
      transform: $["operationId"] = $["operationId"].replace("TestRun_", "LoadTestRun_");
```
