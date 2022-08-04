### Settings

```yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/loadtestservice/data-plane/Microsoft.LoadTestService/preview/2022-06-01-preview/loadtestservice.json
output-folder: ../
namespace: azure.developer.loadtesting
package-name: azure-developer-loadtesting
license-header: MICROSOFT_MIT_NO_VERSION
title: LoadTestingClient
package-version: 1.0.0b2
package-mode: dataplane
package-pprint-name: Azure Developer LoadTesting
security: AADToken
security-scopes: https://loadtest.azure-dev.com/.default
directive:
    - from: swagger-document 
      where: $["paths"]["/serverMetricsConfig/supportedResourceTypes"].get
      transform: $["operationId"] = "ServerMetrics_ListSupportedResourceTypes"
    - from: swagger-document
      where: $["paths"]["/testruns/sortAndFilter"].get
      transform: $["operationId"] = "TestRun_ListTestRuns"
    - from: swagger-document
      where: $["paths"]["/serverMetricsConfig"].get
      transform: $["operationId"] = "ServerMetrics_ListGetServerMetrics"
    - from: swagger-document
      where: $["paths"]["/appcomponents/{name}"].delete
      transform: $["operationId"] = "AppComponent_DeleteAppComponents"
    - from: swagger-document
      where: $["paths"]["/loadtests/{testId}/files"].get
      transform: $["operationId"] = "Test_ListTestFiles"
    - from: swagger-document
      where: $["paths"]["/testruns/sortAndFilter"].get
      transform: $["operationId"] = "TestRun_ListTestRuns"
    - from: swagger-document
      where: $["paths"]["/testruns/{testRunId}"].patch
      transform: $["operationId"] = "TestRun_CreateOrUpdateTest"
    - from: swagger-document
      where: $["paths"]["/serverMetricsConfig/{name}"].get
      transform: $["operationId"] = "ServerMetrics_GetServerMetricsConfigByName"
    - from: swagger-document
      where: $["paths"]["/serverMetricsConfig/{name}"].delete
      transform: $["operationId"] = "ServerMetrics_DeleteServerMetricsConfig"
    - from: swagger-document
      where: $["paths"]["/serverMetricsConfig"].get
      transform: $["operationId"] = "ServerMetrics_GetServerMetricsConfig"
    - from: swagger-document
      where: $["paths"]["/serverMetricsConfig/default"].get
      transform: $["operationId"] = "ServerMetrics_GetServerDefaultMetricsConfig"
```
