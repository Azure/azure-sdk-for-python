### Settings

```yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/main/specification/loadtestservice/data-plane/Microsoft.LoadTestService/preview/2022-06-01-preview/loadtestservice.json
output-folder: ../
namespace: azure.developer.loadtestservice
package-name: azure-developer-loadtestservice
license-header: MICROSOFT_MIT_NO_VERSION
title: LoadTestClient
package-version: 1.0.0b1
package-mode: dataplane
package-pprint-name: Azure Developer LoadTestService
security: AADToken
security-scopes: https://loadtest.azure-dev.com/.default
directive:
    - from: swagger-document 
      where: $["paths"]["/serverMetricsConfig/supportedResourceTypes"].get
      transfrom: $["operationId"] = "ServerMetrics_ListSupportedResourceTypes"
    - from: swagger-document
      where: $["paths"]["/testruns/sortAndFilter"].get
      transfrom: $["operationId"] = "TestRun_ListTestRuns"
    - from: swagger-document
      where: $["paths"]["/serverMetricsConfig"].get
      transfrom: $["operationId"] = "ServerMetrics_ListGetServerMetrics"
```
