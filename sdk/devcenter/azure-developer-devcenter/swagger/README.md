### Settings

```yaml
input-file:
  - https://github.com/Azure/azure-rest-api-specs/blob/552eaca3fb1940d5ec303746017d1764861031e6/specification/devcenter/data-plane/Microsoft.DevCenter/stable/2023-04-01/devcenter.json
  - https://github.com/Azure/azure-rest-api-specs/blob/552eaca3fb1940d5ec303746017d1764861031e6/specification/devcenter/data-plane/Microsoft.DevCenter/stable/2023-04-01/devbox.json
  - https://github.com/Azure/azure-rest-api-specs/blob/552eaca3fb1940d5ec303746017d1764861031e6/specification/devcenter/data-plane/Microsoft.DevCenter/stable/2023-04-01/environments.json
output-folder: ../
namespace: azure.developer.devcenter
package-name: azure-developer-devcenter
license-header: MICROSOFT_MIT_NO_VERSION
title: DevCenterClient
package-version: 1.0.0b3
package-mode: dataplane
package-pprint-name: Azure Developer DevCenter Service
security: AADToken
security-scopes: https://devcenter.azure.com/.default
```

``` yaml
directive:
  # Move project name to method level parameters
  - from: swagger-document
    where: $.parameters["ProjectNameParameter"]
    transform: >-
      $["x-ms-parameter-location"] = "method"

  # Override operation names to match SDK naming preferences
  # TODO: update these names in the Swagger itself for the 2023-07-01-preview version
  - from: swagger-document
    where-operation: DevBoxes_DelayActions
    transform: >-
      $.operationId = "DevBoxes_DelayAllActions";

  - from: swagger-document
    where-operation: DevBoxes_GetDevBoxByUser
    transform: >-
      $.operationId = "DevBoxes_GetDevBox";

  - from: swagger-document
    where-operation: DevBoxes_ListDevBoxesByUser
    transform: >-
      $.operationId = "DevBoxes_ListDevBoxes";

  - from: swagger-document
    where-operation: DevBoxes_ListSchedulesByPool
    transform: >-
      $.operationId = "DevBoxes_ListSchedules";

  - from: swagger-document
    where-operation: DevBoxes_GetScheduleByPool
    transform: >-
      $.operationId = "DevBoxes_GetSchedule";

  - from: swagger-document
    where-operation: DevCenter_ListAllDevBoxes
    transform: >-
      $.operationId = "DevBoxes_ListAllDevBoxes";

  - from: swagger-document
    where-operation: DevCenter_ListAllDevBoxesByUser
    transform: >-
      $.operationId = "DevBoxes_ListAllDevBoxesByUser";

  - from: swagger-document
    where-operation: Environments_CreateOrReplaceEnvironment
    transform: >-
      $.operationId = "DeploymentEnvironments_CreateOrUpdateEnvironment";

  - from: swagger-document
    where-operation: Environments_DeleteEnvironment
    transform: >-
      $.operationId = "DeploymentEnvironments_DeleteEnvironment";

  - from: swagger-document
    where-operation: Environments_GetCatalog
    transform: >-
      $.operationId = "DeploymentEnvironments_GetCatalog";

  - from: swagger-document
    where-operation: Environments_GetEnvironmentByUser
    transform: >-
      $.operationId = "DeploymentEnvironments_GetEnvironment";

  - from: swagger-document
    where-operation: Environments_GetEnvironmentDefinition
    transform: >-
      $.operationId = "DeploymentEnvironments_GetEnvironmentDefinition";

  - from: swagger-document
    where-operation: Environments_ListCatalogsByProject
    transform: >-
      $.operationId = "DeploymentEnvironments_ListCatalogs";

  - from: swagger-document
    where-operation: Environments_ListEnvironmentDefinitionsByCatalog
    transform: >-
      $.operationId = "DeploymentEnvironments_ListEnvironmentDefinitionsByCatalog";

  - from: swagger-document
    where-operation: Environments_ListEnvironmentDefinitionsByProject
    transform: >-
      $.operationId = "DeploymentEnvironments_ListEnvironmentDefinitions";

  - from: swagger-document
    where-operation: Environments_ListEnvironments
    transform: >-
      $.operationId = "DeploymentEnvironments_ListAllEnvironments";

  - from: swagger-document
    where-operation: Environments_ListEnvironmentsByUser
    transform: >-
      $.operationId = "DeploymentEnvironments_ListEnvironments";

  - from: swagger-document
    where-operation: Environments_ListEnvironmentTypes
    transform: >-
      $.operationId = "DeploymentEnvironments_ListEnvironmentTypes";
```